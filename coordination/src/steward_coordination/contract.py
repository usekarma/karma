"""Strict synthetic metadata inspection; never a dispatcher or authority source."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from datetime import date
from typing import Any

VERSION = "karma.steward-work.v1"
STATES = {
    "INTAKE",
    "TRIAGED",
    "READY_FOR_PREPARATION",
    "PREPARED",
    "STOP_FOR_HUMAN",
    "UNKNOWN",
    "FAILED",
    "BLOCKED",
    "CLOSED",
}
UNKNOWN = {"evidence_unknown", "dependency_unknown", "approval_unknown", "source_unknown"}
FAILURES = {"tests_failed", "privacy_denied", "input_rejected"}
CHECKS = {"deterministic_tests", "privacy_isolation", "authorization_boundary"}
FIELDS = {
    "version",
    "work_id",
    "steward",
    "owner_id",
    "source_issue",
    "state",
    "active",
    "dependencies",
    "artifact_sha256",
    "evidence",
    "approval",
    "unknown_conditions",
    "failure_conditions",
    "sharing",
    "gate",
}


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def exact(value: object, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError("metadata object fields rejected")
    return value


def token(value: object, prefix: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(prefix + r"-[0-9a-f]{32}", value):
        raise ValueError("opaque metadata identifier required")


def sha(value: object) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("artifact/evidence digest required")


def choice(value: object, allowed: set[str]) -> None:
    if not isinstance(value, str) or value not in allowed:
        raise ValueError("metadata enumeration rejected")


def flag(value: object) -> None:
    if type(value) is not bool:
        raise ValueError("metadata boolean required")


def day(value: object) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("metadata calendar date required")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError("metadata calendar date rejected") from None


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate metadata key")
        result[key] = value
    return result


def decode(raw: str, limit: int = 16_384) -> object:
    if not isinstance(raw, str):
        raise ValueError("metadata input size/type rejected")
    try:
        length = len(raw.encode())
    except UnicodeError:
        raise ValueError("metadata encoding rejected") from None
    if length > limit:
        raise ValueError("metadata input size/type rejected")
    try:
        return json.loads(raw, object_pairs_hook=unique_pairs)
    except (ValueError, RecursionError):
        raise ValueError("metadata JSON rejected") from None


def bounded_list(value: object) -> list[Any]:
    if not isinstance(value, list) or len(value) > 16:
        raise ValueError("metadata collection rejected")
    return value


def validate_work(raw: str, today: date) -> dict[str, Any]:
    """Validate and freshly authorize disclosure of synthetic workflow metadata."""
    if type(today) is not date:
        raise ValueError("fixed calendar date required")
    work = exact(decode(raw), FIELDS)
    choice(work["version"], {VERSION})
    token(work["work_id"], "wk")
    token(work["owner_id"], "actor")
    choice(work["steward"], {"prudence", "aegis"})
    issue = "4" if work["steward"] == "prudence" else "5"
    choice(work["source_issue"], {"https://github.com/usekarma/karma/issues/" + issue})
    choice(work["state"], STATES)
    choice(work["gate"], {"STOP_FOR_HUMAN"})
    flag(work["active"])
    sha(work["artifact_sha256"])
    deps = bounded_list(work["dependencies"])
    for dependency in deps:
        token(dependency, "wk")
    if len(deps) != len(set(deps)) or work["work_id"] in deps:
        raise ValueError("dependency identity rejected")
    for field, allowed in (("unknown_conditions", UNKNOWN), ("failure_conditions", FAILURES)):
        values = bounded_list(work[field])
        for value in values:
            choice(value, allowed)
        if len(values) != len(set(values)):
            raise ValueError("duplicate metadata condition")
    evidence = bounded_list(work["evidence"])
    references: set[str] = set()
    for value in evidence:
        ev = exact(value, {"reference", "sha256", "verification", "verifier_id"})
        token(ev["reference"], "ev")
        sha(ev["sha256"])
        choice(ev["verification"], {"VERIFIED", "UNKNOWN", "FAILED"})
        if ev["verifier_id"] is not None:
            token(ev["verifier_id"], "actor")
        if ev["verification"] == "VERIFIED" and ev["verifier_id"] is None:
            raise ValueError("VERIFIED evidence requires a verifier reference")
        if ev["reference"] in references:
            raise ValueError("duplicate evidence identity")
        references.add(ev["reference"])
    approval = work["approval"]
    if approval is not None:
        ap = exact(
            approval,
            {
                "reviewer_id",
                "work_id",
                "artifact_sha256",
                "scope",
                "disposition",
                "issued_on",
                "expires_on",
                "revoked",
            },
        )
        token(ap["reviewer_id"], "actor")
        token(ap["work_id"], "wk")
        sha(ap["artifact_sha256"])
        choice(ap["scope"], {"offline_preparation", "metadata_review"})
        choice(ap["disposition"], {"APPROVED", "DENIED"})
        flag(ap["revoked"])
        if day(ap["issued_on"]) >= day(ap["expires_on"]):
            raise ValueError("approval validity window rejected")
    sharing = exact(work["sharing"], {"synthetic", "authorized", "revoked", "expires_on"})
    for field in ("synthetic", "authorized", "revoked"):
        flag(sharing[field])
    if (
        not sharing["synthetic"]
        or not sharing["authorized"]
        or sharing["revoked"]
        or today >= day(sharing["expires_on"])
    ):
        raise PermissionError("STOP_FOR_HUMAN: synthetic metadata disclosure denied")
    return work


def evidence_check(ev: Mapping[str, Any], receipts: Mapping[str, bytes]) -> str:
    """A receipt can verify synthetic check bytes, never personal domain facts."""
    if ev["verification"] != "VERIFIED":
        return str(ev["verification"])
    raw = receipts.get(ev["reference"])
    if not isinstance(raw, bytes) or len(raw) > 4096 or digest(raw) != ev["sha256"]:
        return "UNKNOWN"
    try:
        receipt = exact(
            decode(raw.decode("utf-8"), 4096), {"reference", "synthetic", "check", "result"}
        )
        token(receipt["reference"], "ev")
        choice(receipt["check"], CHECKS)
        choice(receipt["result"], {"PASS", "FAIL", "UNKNOWN"})
        if receipt["synthetic"] is not True or receipt["reference"] != ev["reference"]:
            return "UNKNOWN"
        return {"PASS": "VERIFIED", "FAIL": "FAILED", "UNKNOWN": "UNKNOWN"}[receipt["result"]]
    except (ValueError, UnicodeError):
        return "UNKNOWN"


def approval_valid(work: Mapping[str, Any], today: date) -> bool:
    ap = work["approval"]
    return bool(
        ap is not None
        and ap["disposition"] == "APPROVED"
        and not ap["revoked"]
        and ap["work_id"] == work["work_id"]
        and ap["artifact_sha256"] == work["artifact_sha256"]
        and ap["scope"] == "metadata_review"
        and day(ap["issued_on"]) <= today < day(ap["expires_on"])
    )


def inspect_snapshot(
    raw_items: tuple[str, ...],
    receipts: Mapping[str, bytes],
    today: date,
    current_active_work_id: str | None = None,
) -> dict[str, Any]:
    """Inspect claimed work state; never select, dispatch or change an active task."""
    if type(today) is not date:
        raise ValueError("fixed calendar date required")
    if (
        not isinstance(raw_items, tuple)
        or len(raw_items) > 64
        or not isinstance(receipts, Mapping)
        or len(receipts) > 1024
    ):
        raise ValueError("snapshot size/type rejected")
    if current_active_work_id is not None:
        token(current_active_work_id, "wk")
    works = [validate_work(raw, today) for raw in raw_items]
    ids = [w["work_id"] for w in works]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate work identity")
    active = [w["work_id"] for w in works if w["active"]]
    if len(active) > 1 or (active and active[0] != current_active_work_id):
        raise ValueError("single-active-task conflict; no transition permitted")
    # Resolve dependency order without recursion. Remaining nodes are cyclic or depend on cycles.
    pending = {w["work_id"]: w for w in works}
    ordered: list[dict[str, Any]] = []
    while pending:
        ready = [w for w in pending.values() if not any(d in pending for d in w["dependencies"])]
        if not ready:
            break
        for work in ready:
            ordered.append(work)
            del pending[work["work_id"]]
    ordered.extend(pending.values())
    complete: set[str] = set()
    reports: dict[str, dict[str, Any]] = {}
    for work in ordered:
        checks = [
            {"reference": ev["reference"], "verification": evidence_check(ev, receipts)}
            for ev in work["evidence"]
        ]
        conditions = set(work["unknown_conditions"]) | set(work["failure_conditions"])
        if not checks or any(ev["verification"] == "UNKNOWN" for ev in checks):
            conditions.add("evidence_unknown")
        if any(ev["verification"] == "FAILED" for ev in checks) or work["state"] == "FAILED":
            conditions.add("tests_failed")
        if work["state"] in {"UNKNOWN", "BLOCKED"}:
            conditions.add("source_unknown")
        valid = approval_valid(work, today)
        if not valid:
            conditions.add("approval_unknown")
        if work["work_id"] in pending or any(d not in complete for d in work["dependencies"]):
            conditions.add("dependency_unknown")
        verified = not conditions
        if verified and work["state"] == "CLOSED":
            complete.add(work["work_id"])
        reports[work["work_id"]] = {
            "metadata": work,
            "evidence_checks": checks,
            "approval_valid": valid,
            "verification": "VERIFIED" if verified else "UNKNOWN",
            "conditions": sorted(conditions),
            "coordination_state": "STOP_FOR_HUMAN" if verified else "BLOCKED",
            "gate": "STOP_FOR_HUMAN",
        }
    audit = [
        {
            "work_id": w["work_id"],
            "metadata_sha256": digest(canonical(w).encode()),
            "decision": reports[w["work_id"]]["coordination_state"],
            "gate": "STOP_FOR_HUMAN",
        }
        for w in works
    ]
    return {
        "version": VERSION,
        "items": [reports[w["work_id"]] for w in works],
        "current_active_work_id": current_active_work_id,
        "audit": audit,
        "gate": "STOP_FOR_HUMAN",
    }
