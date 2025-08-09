#!/usr/bin/env python3
# Minimal Kafka normalizer: consumes raw CDC events, emits Karma envelope.
# Env:
#   KAFKA_BOOTSTRAP, KAFKA_USER, KAFKA_PASS, KAFKA_SECURITY_PROTOCOL, KAFKA_SASL_MECHANISM
#   INPUT_TOPICS (comma-separated), OUTPUT_TOPIC, DLQ_TOPIC (optional), MAPPING_PATH

import os, json, hashlib, signal
from datetime import datetime, timezone
from typing import Any, Dict
from confluent_kafka import Consumer, Producer
try:
    import yaml
except ImportError:
    yaml = None

RUN = True
def _stop(*_):  # graceful shutdown
    global RUN; RUN = False

def to_iso(ts: Any) -> str:
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    if isinstance(ts, str):
        try:
            if ts.isdigit():
                return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()
            from dateutil import parser as dtp
            return dtp.parse(ts).astimezone(timezone.utc).isoformat()
        except Exception:
            pass
    if isinstance(ts, datetime):
        return ts.astimezone(timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()

def sha256(v):
    if v is None: return None
    return hashlib.sha256(str(v).encode("utf-8")).hexdigest()

class Mapping:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg or {"mappings":[]}
        self.defaults = self.cfg.get("defaults", {"hash_pii": True})

    def find(self, ns: Dict[str,str]):
        for m in self.cfg.get("mappings", []):
            mm = m.get("match", {})
            if mm.get("ns.db") == ns.get("db") and mm.get("ns.coll") == ns.get("coll"):
                return m
        return None

    def extract(self, change: Dict[str,Any]) -> Dict[str,Any]:
        ns = change.get("ns", {})
        doc = change.get("fullDocument") or {}
        mapping = self.find(ns) or {}
        op = change.get("operationType") or change.get("op") or "event"

        # event_type override (simple: when field equals value)
        et = op
        ovr = mapping.get("event_type_override")
        if ovr:
            when = ovr.get("when")
            try:
                if when and eval_when(when, change):
                    et = ovr.get("value", et)
                elif "else" in ovr:
                    et = ovr["else"]
            except Exception:
                pass

        # tags/attrs
        tags = {}
        for t in mapping.get("tags", []):
            v = deep_get(doc, t)
            if v is not None:
                tags[t] = v
        attrs = {}
        for item in mapping.get("attrs", []):
            if isinstance(item, dict):
                k, expr = list(item.items())[0]
                attrs[k] = eval_calc(expr, change)
            else:
                attrs[item] = deep_get(doc, item)

        # PII hashing
        if self.defaults.get("hash_pii", True):
            for f in mapping.get("pii", []):
                val = deep_get(doc, f)
                if val is not None:
                    set_in(doc, f, sha256(val))

        # Drops (shallow)
        for f in mapping.get("drops", []):
            if isinstance(doc, dict) and f in doc:
                del doc[f]

        entity_id = str(deep_get(doc, "_id") or deep_get(change, "_id") or "")
        corr = str(change.get("documentKey", {}).get("_id") or entity_id)

        evt = {
            "ts": to_iso(change.get("clusterTime") or change.get("wallTime") or change.get("ts")),
            "event_type": et,
            "entity_id": entity_id,
            "correlation_id": corr,
            "tags": tags,
            "attrs": attrs,
            "idempotency_key": f"mongo:{entity_id}:{op}:{change.get('clusterTime') or change.get('ts')}",
            "source": {"system":"mongo","ns":{"db": ns.get("db"), "coll": ns.get("coll")}}
        }
        return evt

def deep_get(dct, path, default=None):
    cur = dct
    for p in path.split("."):
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur

def set_in(dct, path, value):
    parts = path.split(".")
    cur = dct
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
    cur[parts[-1]] = value

def eval_when(expr: str, change: Dict[str,Any]) -> bool:
    if expr.startswith("$eq(") and expr.endswith(")"):
        a,b = split_args(expr[4:-1])
        return val(a, change) == val(b, change)
    if expr.startswith("$exists(") and expr.endswith(")"):
        a = expr[9:-1]
        return deep_get(change, a) is not None
    if expr.startswith("$gt(") and expr.endswith(")"):
        a,b = split_args(expr[4:-1])
        try: return float(val(a, change) or 0) > float(val(b, change) or 0)
        except: return False
    return False

def eval_calc(expr: str, change: Dict[str,Any]):
    if expr.startswith("$secondsDiff(") and expr.endswith(")"):
        a,b = split_args(expr[13:-1])
        from dateutil import parser as dtp
        try:
            ta = dtp.parse(str(val(a, change)))
            tb = dtp.parse(str(val(b, change)))
            return (ta - tb).total_seconds()
        except Exception:
            return None
    v = val(expr, change)
    return v

def split_args(s: str):
    depth = 0
    for i,ch in enumerate(s):
        if ch == "," and depth == 0:
            return s[:i], s[i+1:]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
    return s, ""

def val(token: str, change: Dict[str,Any]):
    token = token.strip()
    if token.startswith("'") and token.endswith("'"):
        return token[1:-1]
    if "." in token:
        return deep_get(change, token)
    try:
        if "." in token: return float(token)
        return int(token)
    except Exception:
        return token

def main():
    cfg_path = os.environ.get("MAPPING_PATH", "mappings/example.yml")
    cfg = {}
    if yaml and os.path.exists(cfg_path):
        with open(cfg_path,"r") as f:
            cfg = yaml.safe_load(f) or {}
    mapping = Mapping(cfg)

    consumer = Consumer({
        "bootstrap.servers": os.environ.get("KAFKA_BOOTSTRAP","localhost:9092"),
        "group.id": os.environ.get("KAFKA_GROUP","karma-normalizer"),
        "auto.offset.reset": "earliest",
        "security.protocol": os.environ.get("KAFKA_SECURITY_PROTOCOL","PLAINTEXT"),
        "sasl.mechanism": os.environ.get("KAFKA_SASL_MECHANISM",""),
        "sasl.username": os.environ.get("KAFKA_USER",""),
        "sasl.password": os.environ.get("KAFKA_PASS",""),
    })
    producer = Producer({"bootstrap.servers": os.environ.get("KAFKA_BOOTSTRAP","localhost:9092")})

    topics = [t.strip() for t in os.environ.get("INPUT_TOPICS","cdc.raw").split(",") if t.strip()]
    out_topic = os.environ.get("OUTPUT_TOPIC","events.normalized")
    dlq_topic = os.environ.get("DLQ_TOPIC","events.normalized.dlq")

    consumer.subscribe(topics)
    signal.signal(signal.SIGINT, _stop); signal.signal(signal.SIGTERM, _stop)

    while RUN:
        msg = consumer.poll(1.0)
        if msg is None: continue
        if msg.error():
            continue
        try:
            change = json.loads(msg.value())
            evt = mapping.extract(change)
            producer.produce(out_topic, json.dumps(evt).encode("utf-8"))
        except Exception:
            try:
                producer.produce(dlq_topic, msg.value())
            except Exception:
                pass
        finally:
            producer.poll(0)

    consumer.close()

if __name__ == "__main__":
    main()
