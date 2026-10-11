"""Explicit synthetic governance proof on top of unchanged work-v1 coordination."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from typing import Any

from .contract import (
    canonical,
    choice,
    day,
    decode,
    digest,
    exact,
    flag,
    inspect_snapshot,
    sha,
    token,
)

VERSION = "karma.simulated-governance.v1"
PROVENANCE_FIELDS = {
    "version",
    "synthetic",
    "work_id",
    "artifact_sha256",
    "reference",
    "receipt_sha256",
    "producer_id",
    "producer_revision",
    "verifier_id",
    "checked_on",
    "expires_on",
    "revoked",
}


def provenance_condition(
    raw: str | None,
    work: Mapping[str, Any],
    ev: Mapping[str, Any],
    today: date,
    producers: Mapping[str, str],
    verifiers: frozenset[str],
) -> str | None:
    if raw is None:
        return "missing_evidence"
    try:
        p = exact(decode(raw, 4096), PROVENANCE_FIELDS)
        choice(p["version"], {VERSION})
        for field, prefix in (
            ("work_id", "wk"),
            ("reference", "ev"),
            ("producer_id", "actor"),
            ("verifier_id", "actor"),
        ):
            token(p[field], prefix)
        for field in ("artifact_sha256", "receipt_sha256", "producer_revision"):
            sha(p[field])
        flag(p["synthetic"])
        flag(p["revoked"])
        checked, expires = day(p["checked_on"]), day(p["expires_on"])
        if expires <= checked:
            return "invalid_evidence"
        if (
            p["work_id"] != work["work_id"]
            or p["artifact_sha256"] != work["artifact_sha256"]
            or p["reference"] != ev["reference"]
            or p["receipt_sha256"] != ev["sha256"]
            or p["verifier_id"] != ev["verifier_id"]
        ):
            return "invalid_evidence"
        if (
            not p["synthetic"]
            or p["revoked"]
            or p["verifier_id"] not in verifiers
            or producers.get(p["producer_id"]) != p["producer_revision"]
        ):
            return "unauthorized_evidence"
        if not checked <= today < expires or (today - checked).days > 7:
            return "stale_evidence"
        return None
    except ValueError:
        return "invalid_evidence"


def review_for_human(
    raw_items: tuple[str, ...],
    receipts: Mapping[str, bytes],
    provenance: Mapping[str, str],
    today: date,
    target_work_id: str,
    current_active_work_id: str | None,
    producers: Mapping[str, str],
    verifiers: frozenset[str],
    reviewers: frozenset[str],
) -> dict[str, Any]:
    """Readiness is for simulated human review only; no state or permission changes."""
    token(target_work_id, "wk")
    if (
        not isinstance(producers, Mapping)
        or len(producers) > 16
        or not isinstance(provenance, Mapping)
        or len(provenance) > 1024
        or not isinstance(verifiers, frozenset)
        or not isinstance(reviewers, frozenset)
        or len(verifiers) > 16
        or len(reviewers) > 16
    ):
        raise ValueError("synthetic policy rejected")
    for actor in verifiers | reviewers | set(producers):
        token(actor, "actor")
    for revision in producers.values():
        sha(revision)
    snapshot = inspect_snapshot(raw_items, receipts, today, current_active_work_id)
    targets = [r for r in snapshot["items"] if r["metadata"]["work_id"] == target_work_id]
    if len(targets) != 1:
        raise ValueError("review target missing")
    target = targets[0]
    references = {
        ev["reference"] for item in snapshot["items"] for ev in item["metadata"]["evidence"]
    }
    if set(provenance) - references:
        raise ValueError("provenance inventory scope rejected")
    conditions = set(target["conditions"]) - {"approval_unknown"}
    if (
        target["metadata"]["state"] != "STOP_FOR_HUMAN"
        or target["metadata"]["approval"] is not None
    ):
        conditions.add("unsolicited_approval_or_transition")
    # Strict provenance applies to dependencies too; they cannot supply forged completion.
    accepted_provenance: dict[str, Any] = {}
    for item in snapshot["items"]:
        work = item["metadata"]
        for ev in work["evidence"]:
            condition = provenance_condition(
                provenance.get(ev["reference"]), work, ev, today, producers, verifiers
            )
            if condition:
                conditions.add(condition)
            else:
                accepted_provenance[ev["reference"]] = exact(
                    decode(provenance[ev["reference"]], 4096), PROVENANCE_FIELDS
                )
        if (
            work["work_id"] != target_work_id
            and work["approval"] is not None
            and work["approval"]["reviewer_id"] not in reviewers
        ):
            conditions.add("unauthorized_dependency_review")
        if any(e["verification"] != "VERIFIED" for e in item["evidence_checks"]):
            conditions.add("invalid_evidence")
    body = {
        "version": VERSION,
        "synthetic": True,
        "work_id": target_work_id,
        "artifact_sha256": target["metadata"]["artifact_sha256"],
        "snapshot_sha256": digest(canonical(snapshot).encode()),
        "provenance_sha256": digest(canonical(accepted_provenance).encode()),
        "policy_sha256": digest(
            canonical(
                {
                    "producers": dict(producers),
                    "verifiers": sorted(verifiers),
                    "reviewers": sorted(reviewers),
                }
            ).encode()
        ),
        "as_of": today.isoformat(),
        "current_active_work_id": current_active_work_id,
        "conditions": sorted(conditions),
        "readiness": "REJECTED" if conditions else "AWAITING_SIMULATED_HUMAN",
        "gate": "STOP_FOR_HUMAN",
        "execution_authorized": False,
    }
    return {"body": body, "sha256": digest(canonical(body).encode())}


AUDIT_FIELDS = {
    "version",
    "sequence",
    "previous_sha256",
    "event",
    "work_id",
    "artifact_sha256",
    "review_sha256",
    "reviewer_id",
    "disposition",
    "as_of",
    "current_active_work_id",
    "simulated",
    "gate",
    "execution_authorized",
}


def validate_history(history: tuple[str, ...]) -> str:
    if not isinstance(history, tuple) or len(history) > 64:
        raise ValueError("synthetic audit history rejected")
    previous = "0" * 64
    seen_reviews: set[str] = set()
    previous_day: date | None = None
    for index, raw in enumerate(history, 1):
        entry = exact(decode(raw, 4096), {"body", "sha256"})
        body = exact(entry["body"], AUDIT_FIELDS)
        choice(body["version"], {VERSION})
        if type(body["sequence"]) is not int or body["sequence"] != index:
            raise ValueError("audit sequence rejected")
        for field in ("previous_sha256", "artifact_sha256", "review_sha256"):
            sha(body[field])
        token(body["work_id"], "wk")
        token(body["reviewer_id"], "actor")
        choice(body["event"], {"simulated_decision"})
        choice(body["disposition"], {"DEFER", "REJECT", "ACKNOWLEDGE_FOR_REVIEW"})
        recorded_day = day(body["as_of"])
        if previous_day is not None and recorded_day < previous_day:
            raise ValueError("audit chronology rejected")
        previous_day = recorded_day
        if body["current_active_work_id"] is not None:
            token(body["current_active_work_id"], "wk")
        if (
            body["simulated"] is not True
            or body["execution_authorized"] is not False
            or body["gate"] != "STOP_FOR_HUMAN"
        ):
            raise PermissionError("STOP_FOR_HUMAN: audit authority rejected")
        if body["previous_sha256"] != previous or entry["sha256"] != digest(
            canonical(body).encode()
        ):
            raise ValueError("audit chain integrity rejected")
        if body["review_sha256"] in seen_reviews:
            raise ValueError("audit review replay rejected")
        seen_reviews.add(body["review_sha256"])
        previous = entry["sha256"]
    return str(previous)


def record_simulated_decision(
    raw_items: tuple[str, ...],
    receipts: Mapping[str, bytes],
    provenance: Mapping[str, str],
    today: date,
    target_work_id: str,
    current_active_work_id: str | None,
    producers: Mapping[str, str],
    verifiers: frozenset[str],
    reviewers: frozenset[str],
    expected_review_sha256: str,
    reviewer_id: str,
    disposition: str,
    history: tuple[str, ...] = (),
    *,
    explicitly_simulated: bool = False,
) -> tuple[str, ...]:
    """Freshly revalidate and append a simulation receipt; no actual approval exists."""
    if explicitly_simulated is not True:
        raise PermissionError("STOP_FOR_HUMAN: explicit simulation input required")
    token(reviewer_id, "actor")
    choice(disposition, {"DEFER", "REJECT", "ACKNOWLEDGE_FOR_REVIEW"})
    sha(expected_review_sha256)
    if reviewer_id not in reviewers:
        raise PermissionError("STOP_FOR_HUMAN: simulated reviewer not authorized")
    review = review_for_human(
        raw_items,
        receipts,
        provenance,
        today,
        target_work_id,
        current_active_work_id,
        producers,
        verifiers,
        reviewers,
    )
    if (
        review["body"]["readiness"] != "AWAITING_SIMULATED_HUMAN"
        or review["sha256"] != expected_review_sha256
    ):
        raise PermissionError("STOP_FOR_HUMAN: stale or rejected review cannot record a decision")
    previous = validate_history(history)
    if len(history) >= 64:
        raise ValueError("synthetic audit history full")
    if history:
        latest = exact(decode(history[-1]), {"body", "sha256"})
        if today < day(latest["body"]["as_of"]):
            raise ValueError("audit chronology rejected")
    for raw in history:
        entry = exact(decode(raw), {"body", "sha256"})
        if entry["body"]["review_sha256"] == review["sha256"]:
            raise ValueError("simulated review replay rejected")
    body = {
        "version": VERSION,
        "sequence": len(history) + 1,
        "previous_sha256": previous,
        "event": "simulated_decision",
        "work_id": target_work_id,
        "artifact_sha256": review["body"]["artifact_sha256"],
        "review_sha256": review["sha256"],
        "reviewer_id": reviewer_id,
        "disposition": disposition,
        "as_of": today.isoformat(),
        "current_active_work_id": current_active_work_id,
        "simulated": True,
        "gate": "STOP_FOR_HUMAN",
        "execution_authorized": False,
    }
    return (*history, canonical({"body": body, "sha256": digest(canonical(body).encode())}))
