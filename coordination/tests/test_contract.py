from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path

import pytest

from steward_coordination.contract import (
    FIELDS,
    VERSION,
    canonical,
    decode,
    digest,
    inspect_snapshot,
    validate_work,
)

TODAY = date(2026, 10, 11)
W1 = "wk-" + "1" * 32
W2 = "wk-" + "2" * 32
W3 = "wk-" + "3" * 32
ACTOR = "actor-" + "4" * 32
EV = "ev-" + "5" * 32
ARTIFACT = "6" * 64


def receipt(result: str = "PASS") -> bytes:
    return canonical(
        {"reference": EV, "synthetic": True, "check": "deterministic_tests", "result": result}
    ).encode()


def work() -> dict[str, object]:
    return {
        "version": VERSION,
        "work_id": W1,
        "steward": "prudence",
        "owner_id": ACTOR,
        "source_issue": "https://github.com/usekarma/karma/issues/4",
        "state": "PREPARED",
        "active": False,
        "dependencies": [],
        "artifact_sha256": ARTIFACT,
        "evidence": [
            {
                "reference": EV,
                "sha256": digest(receipt()),
                "verification": "VERIFIED",
                "verifier_id": ACTOR,
            }
        ],
        "approval": {
            "reviewer_id": ACTOR,
            "work_id": W1,
            "artifact_sha256": ARTIFACT,
            "scope": "metadata_review",
            "disposition": "APPROVED",
            "issued_on": "2026-10-01",
            "expires_on": "2026-11-01",
            "revoked": False,
        },
        "unknown_conditions": [],
        "failure_conditions": [],
        "sharing": {
            "synthetic": True,
            "authorized": True,
            "revoked": False,
            "expires_on": "2026-11-01",
        },
        "gate": "STOP_FOR_HUMAN",
    }


def report(data: dict[str, object], raw_receipt: bytes | None = None) -> dict[str, object]:
    return inspect_snapshot((canonical(data),), {EV: raw_receipt or receipt()}, TODAY)


def test_valid_and_deterministic_audit() -> None:
    original = work()
    before = copy.deepcopy(original)
    result = report(original)
    assert result == report(original)
    assert original == before
    item = result["items"][0]
    assert item["verification"] == "VERIFIED"
    assert item["coordination_state"] == item["gate"] == "STOP_FOR_HUMAN"
    assert result["current_active_work_id"] is None
    assert result["audit"][0]["metadata_sha256"] == digest(canonical(original).encode())
    assert result["audit"][0]["gate"] == "STOP_FOR_HUMAN"
    schema = json.loads(
        (Path(__file__).parents[1] / "contracts/steward-work.v1.schema.json").read_text()
    )
    assert set(schema["required"]) == FIELDS
    assert schema["additionalProperties"] is False
    aegis = work() | {
        "steward": "aegis",
        "source_issue": "https://github.com/usekarma/karma/issues/5",
    }
    assert validate_work(canonical(aegis), TODAY)["steward"] == "aegis"


@pytest.mark.parametrize(
    "field,value",
    [
        ("version", "unsupported"),
        ("work_id", "person-alex"),
        ("owner_id", "family-member"),
        ("steward", "other"),
        ("source_issue", "https://example.com/medical-record"),
        ("state", "EXECUTING"),
        ("active", "false"),
        ("artifact_sha256", "abc"),
        ("gate", "EXECUTE"),
        ("dependencies", [W2] * 17),
        ("dependencies", [W2, W2]),
        ("dependencies", [W1]),
        ("dependencies", {}),
        ("dependencies", [None]),
        ("unknown_conditions", ["diagnosis"]),
        ("unknown_conditions", ["source_unknown"] * 2),
        ("failure_conditions", ["tests_failed"] * 2),
        ("evidence", {}),
    ],
)
def test_invalid_root_contract(field: str, value: object) -> None:
    data = work() | {field: value}
    with pytest.raises(ValueError):
        validate_work(canonical(data), TODAY)


@pytest.mark.parametrize(
    "extra", ["balance", "account", "diagnosis", "medications", "family", "notes"]
)
def test_sensitive_payload_rejected_without_disclosure(extra: str) -> None:
    secret_marker = "synthetic-sensitive-payload-marker"
    with pytest.raises(ValueError) as error:
        validate_work(canonical(work() | {extra: secret_marker}), TODAY)
    assert secret_marker not in str(error.value)


def test_malformed_and_duplicate_json_and_bounds() -> None:
    for raw in ('{"work_id":1,"work_id":2}', "[{}]", "{", "x" * 16_385, "[" * 2000 + "]" * 2000):
        with pytest.raises(ValueError):
            validate_work(raw, TODAY)
    with pytest.raises(ValueError):
        decode(1)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        validate_work(canonical(work()), "today")  # type: ignore[arg-type]
    for raw_items, active_id in (
        ([canonical(work())], None),
        ((canonical(work()),) * 65, None),
        ((), "real-active-person"),
    ):
        with pytest.raises(ValueError):
            inspect_snapshot(raw_items, {}, TODAY, active_id)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field,value",
    [
        ("reference", "file:///record"),
        ("sha256", None),
        ("verification", "trusted"),
        ("verifier_id", "person"),
        ("verifier_id", None),
    ],
)
def test_invalid_evidence_fields(field: str, value: object) -> None:
    data = work()
    data["evidence"][0][field] = value
    with pytest.raises(ValueError):
        validate_work(canonical(data), TODAY)


def test_duplicate_evidence_and_missing_fields() -> None:
    data = work()
    data["evidence"] *= 2
    with pytest.raises(ValueError):
        validate_work(canonical(data), TODAY)
    data = work()
    del data["sharing"]["expires_on"]
    with pytest.raises(ValueError):
        validate_work(canonical(data), TODAY)


@pytest.mark.parametrize(
    "field,value",
    [("authorized", False), ("synthetic", False), ("revoked", True), ("expires_on", "2026-10-11")],
)
def test_sharing_missing_expired_revoked_or_real(field: str, value: object) -> None:
    data = work()
    data["sharing"][field] = value
    with pytest.raises(PermissionError, match="STOP_FOR_HUMAN"):
        validate_work(canonical(data), TODAY)


@pytest.mark.parametrize("date_value", ["2026-02-30", "tomorrow", "2026-1-01", 1])
def test_invalid_dates(date_value: object) -> None:
    data = work()
    data["sharing"]["expires_on"] = date_value
    with pytest.raises(ValueError):
        validate_work(canonical(data), TODAY)


@pytest.mark.parametrize(
    "field,value",
    [
        ("scope", "merge"),
        ("disposition", "execute"),
        ("reviewer_id", "human-name"),
        ("revoked", 1),
        ("expires_on", "2026-10-01"),
    ],
)
def test_invalid_approval_syntax(field: str, value: object) -> None:
    data = work()
    data["approval"][field] = value
    with pytest.raises(ValueError):
        validate_work(canonical(data), TODAY)


@pytest.mark.parametrize(
    "field,value",
    [
        ("work_id", W2),
        ("artifact_sha256", "7" * 64),
        ("scope", "offline_preparation"),
        ("disposition", "DENIED"),
        ("revoked", True),
        ("expires_on", "2026-10-11"),
        ("issued_on", "2026-10-12"),
    ],
)
def test_approval_binding_expiry_and_no_execution(field: str, value: object) -> None:
    data = work()
    data["approval"][field] = value
    result = report(data)
    assert result["items"][0]["approval_valid"] is False
    assert "approval_unknown" in result["items"][0]["conditions"]
    assert result["gate"] == "STOP_FOR_HUMAN"


def test_unknown_failure_and_unresolved_receipts() -> None:
    data = work()
    data["approval"] = None
    data["evidence"] = []
    data["unknown_conditions"] = ["source_unknown"]
    data["failure_conditions"] = ["privacy_denied"]
    result = report(data)
    assert set(result["items"][0]["conditions"]) == {
        "source_unknown",
        "privacy_denied",
        "evidence_unknown",
        "approval_unknown",
    }
    for declared in ("UNKNOWN", "FAILED"):
        data = work()
        data["evidence"][0]["verification"] = declared
        data["evidence"][0]["verifier_id"] = None
        assert report(data)["items"][0]["evidence_checks"][0]["verification"] == declared
    result = inspect_snapshot((canonical(work()),), {}, TODAY)
    assert result["items"][0]["verification"] == "UNKNOWN"
    assert report(work(), b"wrong bytes")["items"][0]["verification"] == "UNKNOWN"


@pytest.mark.parametrize(
    "raw",
    [
        b"{}",
        b"\xff",
        b"{",
        b"x" * 4097,
        canonical(
            {"reference": EV, "synthetic": False, "check": "deterministic_tests", "result": "PASS"}
        ).encode(),
        canonical(
            {
                "reference": "ev-" + "8" * 32,
                "synthetic": True,
                "check": "deterministic_tests",
                "result": "PASS",
            }
        ).encode(),
        canonical(
            {
                "reference": EV,
                "synthetic": True,
                "check": "deterministic_tests",
                "result": "PASS",
                "diagnosis": "synthetic",
            }
        ).encode(),
    ],
)
def test_bad_receipts_never_verify(raw: bytes) -> None:
    data = work()
    data["evidence"][0]["sha256"] = digest(raw)
    assert report(data, raw)["items"][0]["evidence_checks"][0]["verification"] == "UNKNOWN"


@pytest.mark.parametrize("outcome", ["FAIL", "UNKNOWN"])
def test_receipt_failures_retained(outcome: str) -> None:
    data = work()
    raw = receipt(outcome)
    data["evidence"][0]["sha256"] = digest(raw)
    result = report(data, raw)
    assert result["items"][0]["verification"] == "UNKNOWN"
    if outcome == "FAIL":
        assert "tests_failed" in result["items"][0]["conditions"]


def test_single_active_slot_and_no_dispatch() -> None:
    first = work() | {"active": True}
    second = work() | {"work_id": W2, "active": True}
    for active in (None, W3):
        with pytest.raises(ValueError, match="single-active-task"):
            inspect_snapshot((canonical(first),), {EV: receipt()}, TODAY, active)
    with pytest.raises(ValueError, match="single-active-task"):
        inspect_snapshot((canonical(first), canonical(second)), {}, TODAY, W1)
    result = inspect_snapshot((canonical(first),), {EV: receipt()}, TODAY, W1)
    assert result["current_active_work_id"] == W1
    assert result["gate"] == "STOP_FOR_HUMAN"
    result = inspect_snapshot((canonical(work()),), {EV: receipt()}, TODAY, W3)
    assert result["current_active_work_id"] == W3
    assert result["items"][0]["metadata"]["active"] is False
    with pytest.raises(ValueError, match="duplicate work"):
        inspect_snapshot((canonical(work()), canonical(work())), {}, TODAY)


def test_dependencies_cycles_and_closed_claims() -> None:
    first = work() | {"state": "CLOSED"}
    second = work() | {"work_id": W2, "dependencies": [W1]}
    second["approval"]["work_id"] = W2
    result = inspect_snapshot((canonical(second), canonical(first)), {EV: receipt()}, TODAY)
    assert result["items"][0]["conditions"] == []
    for bad in (work(), work() | {"state": "CLOSED", "evidence": []}):
        result = inspect_snapshot((canonical(second), canonical(bad)), {EV: receipt()}, TODAY)
        assert "dependency_unknown" in result["items"][0]["conditions"]
    result = inspect_snapshot((canonical(second),), {EV: receipt()}, TODAY)
    assert "dependency_unknown" in result["items"][0]["conditions"]
    first["dependencies"] = [W2]
    result = inspect_snapshot((canonical(first), canonical(second)), {EV: receipt()}, TODAY)
    assert all("dependency_unknown" in r["conditions"] for r in result["items"])
    for state in ("UNKNOWN", "FAILED", "BLOCKED"):
        assert report(work() | {"state": state})["items"][0]["verification"] == "UNKNOWN"


def test_empty_snapshot_and_encoding_fail_closed() -> None:
    assert inspect_snapshot((), {}, TODAY)["items"] == []
    with pytest.raises(ValueError):
        inspect_snapshot((), {}, "today")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        inspect_snapshot((), None, TODAY)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        inspect_snapshot((), {str(i): b"" for i in range(1025)}, TODAY)
    with pytest.raises(ValueError, match="encoding rejected"):
        decode("\ud800")
