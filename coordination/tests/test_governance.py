from __future__ import annotations

import copy
import json
from datetime import date
from typing import Any

import pytest
from test_contract import ACTOR, ARTIFACT, EV, TODAY, W1, W2, W3, receipt, work

from steward_coordination.contract import canonical, digest
from steward_coordination.governance import (
    VERSION,
    record_simulated_decision,
    review_for_human,
    validate_history,
)

PRODUCER = "actor-" + "8" * 32
REVIEWER = "actor-" + "7" * 32
REVISION = "9" * 64


def inputs() -> dict[str, Any]:
    w = work() | {"state": "STOP_FOR_HUMAN", "approval": None}
    p = {
        "version": VERSION,
        "synthetic": True,
        "work_id": W1,
        "artifact_sha256": ARTIFACT,
        "reference": EV,
        "receipt_sha256": digest(receipt()),
        "producer_id": PRODUCER,
        "producer_revision": REVISION,
        "verifier_id": ACTOR,
        "checked_on": "2026-10-10",
        "expires_on": "2026-10-17",
        "revoked": False,
    }
    return {
        "raw_items": (canonical(w),),
        "receipts": {EV: receipt()},
        "provenance": {EV: canonical(p)},
        "today": TODAY,
        "target_work_id": W1,
        "current_active_work_id": W3,
        "producers": {PRODUCER: REVISION},
        "verifiers": frozenset({ACTOR}),
        "reviewers": frozenset({REVIEWER}),
    }


def record(
    config: dict[str, Any],
    *,
    explicit: bool = True,
    history: tuple[str, ...] = (),
    expected: str | None = None,
    reviewer: str = REVIEWER,
) -> tuple[str, ...]:
    reviewed = review_for_human(**config)
    return record_simulated_decision(
        **config,
        expected_review_sha256=expected or reviewed["sha256"],
        reviewer_id=reviewer,
        disposition="DEFER",
        history=history,
        explicitly_simulated=explicit,
    )


def test_end_to_end_simulated_review_and_receipt_boundary() -> None:
    config = inputs()
    before = copy.deepcopy(config)
    review = review_for_human(**config)
    assert review["body"]["readiness"] == "AWAITING_SIMULATED_HUMAN"
    assert review["body"]["current_active_work_id"] == W3
    assert review["body"]["gate"] == "STOP_FOR_HUMAN"
    with pytest.raises(PermissionError, match="explicit simulation"):
        record(config, explicit=False)
    history = record(config)
    body = json.loads(history[0])["body"]
    assert body["disposition"] == "DEFER" and body["simulated"] is True
    assert body["gate"] == "STOP_FOR_HUMAN" and body["execution_authorized"] is False
    assert body["current_active_work_id"] == W3
    assert validate_history(history) == json.loads(history[0])["sha256"]
    assert config == before
    assert json.loads(config["raw_items"][0])["approval"] is None
    assert record(config) == history
    with pytest.raises(ValueError, match="replay"):
        record(config, history=history)
    config["today"] = date(2026, 10, 12)
    second = record(config, history=history)
    assert len(history) == 1 and len(second) == 2
    assert json.loads(second[1])["body"]["previous_sha256"] == json.loads(history[0])["sha256"]
    validate_history(second)


@pytest.mark.parametrize("case", ["missing", "invalid", "stale", "unauthorized"])
def test_missing_invalid_stale_unauthorized_evidence(case: str) -> None:
    config = inputs()
    p = json.loads(config["provenance"][EV])
    if case == "missing":
        config["provenance"] = {}
        config["receipts"] = {}
    elif case == "invalid":
        config["receipts"][EV] = b"modified receipt"
        p["artifact_sha256"] = "a" * 64
        config["provenance"][EV] = canonical(p)
    elif case == "stale":
        p["checked_on"] = "2026-10-01"
        p["expires_on"] = "2026-10-20"
        config["provenance"][EV] = canonical(p)
    else:
        config["verifiers"] = frozenset()
    review = review_for_human(**config)
    assert review["body"]["readiness"] == "REJECTED"
    assert case + "_evidence" in review["body"]["conditions"]
    with pytest.raises(PermissionError, match="rejected review"):
        record(config)


@pytest.mark.parametrize(
    "field,value,condition",
    [
        ("version", "old", "invalid_evidence"),
        ("synthetic", "true", "invalid_evidence"),
        ("synthetic", False, "unauthorized_evidence"),
        ("revoked", True, "unauthorized_evidence"),
        ("expires_on", "2026-10-10", "invalid_evidence"),
        ("expires_on", "2026-10-11", "stale_evidence"),
        ("checked_on", "2026-10-12", "stale_evidence"),
        ("producer_revision", "a" * 64, "unauthorized_evidence"),
        ("work_id", W2, "invalid_evidence"),
        ("reference", "ev-" + "a" * 32, "invalid_evidence"),
        ("receipt_sha256", "b" * 64, "invalid_evidence"),
        ("verifier_id", REVIEWER, "invalid_evidence"),
        ("notes", "synthetic-private", "invalid_evidence"),
    ],
)
def test_provenance_bindings_and_fields(field: str, value: object, condition: str) -> None:
    config = inputs()
    p = json.loads(config["provenance"][EV])
    p[field] = value
    config["provenance"][EV] = canonical(p)
    assert condition in review_for_human(**config)["body"]["conditions"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("producers", {}),
        ("verifiers", set()),
        ("reviewers", set()),
        ("producers", {"actor-" + "a" * 32: "a" * 64} | {str(i): "a" * 64 for i in range(16)}),
        ("provenance", {str(i): "{}" for i in range(1025)}),
        ("verifiers", frozenset({"not-opaque"})),
        ("producers", {PRODUCER: "invalid"}),
    ],
)
def test_invalid_or_missing_trust_policy(field: str, value: object) -> None:
    config = inputs() | {field: value}
    if field == "producers" and value == {}:
        assert "unauthorized_evidence" in review_for_human(**config)["body"]["conditions"]
    else:
        with pytest.raises(ValueError):
            review_for_human(**config)


def test_dependency_active_and_approval_claims() -> None:
    config = inputs()
    w = json.loads(config["raw_items"][0])
    w["dependencies"] = [W2]
    config["raw_items"] = (canonical(w),)
    assert "dependency_unknown" in review_for_human(**config)["body"]["conditions"]
    w["active"] = True
    config["raw_items"] = (canonical(w),)
    with pytest.raises(ValueError, match="single-active-task"):
        review_for_human(**config)
    config = inputs()
    config["target_work_id"] = W2
    with pytest.raises(ValueError, match="target missing"):
        review_for_human(**config)
    for field, value in (("state", "CLOSED"), ("approval", work()["approval"])):
        config = inputs()
        w = json.loads(config["raw_items"][0]) | {field: value}
        config["raw_items"] = (canonical(w),)
        assert (
            "unsolicited_approval_or_transition" in review_for_human(**config)["body"]["conditions"]
        )
    config = inputs()
    config["provenance"]["ev-" + "f" * 32] = "private-unknown"
    with pytest.raises(ValueError, match="inventory scope"):
        review_for_human(**config)


def test_changed_review_and_unauthorized_decision_rejected() -> None:
    config = inputs()
    old = review_for_human(**config)["sha256"]
    with pytest.raises(PermissionError, match="reviewer"):
        record(config, reviewer=PRODUCER)
    config["current_active_work_id"] = W2
    with pytest.raises(PermissionError, match="stale"):
        record(config, expected=old)
    config = inputs()
    p = json.loads(config["provenance"][EV]) | {"revoked": True}
    config["provenance"][EV] = canonical(p)
    with pytest.raises(PermissionError):
        record(config, expected=old)
    config = inputs()
    w = json.loads(config["raw_items"][0])
    w["sharing"]["revoked"] = True
    config["raw_items"] = (canonical(w),)
    with pytest.raises(PermissionError, match="disclosure"):
        record(config, expected=old)


@pytest.mark.parametrize(
    "field,value",
    [
        ("sequence", True),
        ("previous_sha256", "a" * 64),
        ("gate", "EXECUTE"),
        ("simulated", False),
        ("execution_authorized", True),
        ("disposition", "APPROVE_PAYMENT"),
        ("notes", "synthetic-private"),
    ],
)
def test_audit_corruption_and_no_execution(field: str, value: object) -> None:
    entry = json.loads(record(inputs())[0])
    entry["body"][field] = value
    with pytest.raises((ValueError, PermissionError)):
        validate_history((canonical(entry),))


def test_history_type_hash_order_and_limits() -> None:
    config = inputs()
    history = record(config)
    entry = json.loads(history[0]) | {"sha256": "f" * 64}
    with pytest.raises(ValueError, match="integrity"):
        validate_history((canonical(entry),))
    with pytest.raises(ValueError):
        validate_history(list(history))  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        validate_history(history * 65)
    config["today"] = date(2026, 10, 12)
    second = record(config, history=history)
    with pytest.raises(ValueError, match="sequence"):
        validate_history(tuple(reversed(second)))
    assert validate_history(()) == "0" * 64


def dependency_inputs() -> dict[str, Any]:
    config = inputs()
    target = json.loads(config["raw_items"][0])
    target["dependencies"] = [W2]
    dep = work() | {"work_id": W2, "state": "CLOSED"}
    ref = "ev-" + "2" * 32
    check = canonical(json.loads(receipt()) | {"reference": ref}).encode()
    dep["evidence"][0].update(reference=ref, sha256=digest(check))
    dep["approval"].update(work_id=W2, reviewer_id=REVIEWER)
    p = json.loads(config["provenance"][EV]) | {
        "work_id": W2,
        "reference": ref,
        "receipt_sha256": digest(check),
    }
    config["raw_items"] = (canonical(target), canonical(dep))
    config["receipts"][ref] = check
    config["provenance"][ref] = canonical(p)
    return config


def test_verified_dependency_and_wrong_reviewer() -> None:
    config = dependency_inputs()
    assert review_for_human(**config)["body"]["readiness"] == "AWAITING_SIMULATED_HUMAN"
    dep = json.loads(config["raw_items"][1])
    dep["approval"]["reviewer_id"] = PRODUCER
    config["raw_items"] = (config["raw_items"][0], canonical(dep))
    assert "unauthorized_dependency_review" in review_for_human(**config)["body"]["conditions"]


def test_append_limits_replayed_and_backdated_history() -> None:
    config = inputs()
    first = json.loads(record(config)[0])
    duplicate = copy.deepcopy(first)
    duplicate["body"].update(sequence=2, previous_sha256=first["sha256"])
    duplicate["sha256"] = digest(canonical(duplicate["body"]).encode())
    with pytest.raises(ValueError, match="replay"):
        validate_history((canonical(first), canonical(duplicate)))
    chain: list[str] = []
    prev = "0" * 64
    for index in range(1, 65):
        body = first["body"] | {
            "sequence": index,
            "previous_sha256": prev,
            "review_sha256": f"{1000 + index:064x}",
        }
        prev = digest(canonical(body).encode())
        chain.append(canonical({"body": body, "sha256": prev}))
    with pytest.raises(ValueError, match="full"):
        record(config, history=tuple(chain))
    config["today"] = date(2026, 10, 12)
    history = record(config)
    config["today"] = TODAY
    with pytest.raises(ValueError, match="chronology"):
        record(config, history=history)
    backdated = json.loads(history[0])
    backdated["body"].update(sequence=2, previous_sha256=first["sha256"], as_of="2026-10-01")
    backdated["sha256"] = digest(canonical(backdated["body"]).encode())
    with pytest.raises(ValueError, match="chronology"):
        validate_history((canonical(first), canonical(backdated)))


def test_absent_active_slot_is_not_invented() -> None:
    config = inputs() | {"current_active_work_id": None}
    review = review_for_human(**config)
    history = record(config)
    assert review["body"]["current_active_work_id"] is None
    assert json.loads(history[0])["body"]["current_active_work_id"] is None
    assert json.loads(history[0])["body"]["gate"] == "STOP_FOR_HUMAN"
    validate_history(history)
