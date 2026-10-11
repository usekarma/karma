from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from steward_coordination.contract import canonical
from steward_coordination.governance import record_simulated_decision, review_for_human

ROOT = Path(__file__).parents[1]


def fixture() -> dict:
    return json.loads((ROOT / "examples/governance-packets.json").read_text())


def arguments(packet: dict, data: dict) -> dict:
    ref = packet["work"]["evidence"][0]["reference"]
    return {
        "raw_items": (canonical(packet["work"]),),
        "receipts": {ref: canonical(packet["receipt"]).encode()},
        "provenance": {ref: canonical(packet["provenance"])},
        "today": date(2026, 10, 11),
        "target_work_id": packet["work"]["work_id"],
        "current_active_work_id": data["current_active_work_id"],
        "producers": data["producers"],
        "verifiers": frozenset(data["verifiers"]),
        "reviewers": frozenset(data["reviewers"]),
    }


def test_actual_producer_packets_and_simulated_receipts() -> None:
    data = fixture()
    expected = json.loads((ROOT / "examples/governance-proof.expected.json").read_text())
    for packet, outcome in zip(data["packets"], expected["work"], strict=True):
        args = arguments(packet, data)
        review = review_for_human(**args)
        assert review == outcome["review"]
        with pytest.raises(PermissionError):
            record_simulated_decision(
                **args,
                expected_review_sha256=review["sha256"],
                reviewer_id=data["reviewers"][0],
                disposition="DEFER",
            )
        history = record_simulated_decision(
            **args,
            expected_review_sha256=review["sha256"],
            reviewer_id=data["reviewers"][0],
            disposition="DEFER",
            explicitly_simulated=True,
        )
        assert [json.loads(r) for r in history] == outcome["simulated_decision_receipts"]
        assert packet["work"]["state"] == "STOP_FOR_HUMAN"
        assert packet["work"]["approval"] is None
        assert review["body"]["current_active_work_id"] == data["current_active_work_id"]
        assert not {
            "balance",
            "brief",
            "recommendation",
            "subject_id",
            "medication",
            "due_on",
            "category",
            "family",
        } & set(packet["work"])
    assert expected["profile_denials"] == 4
    assert expected["private_data_noninterference"] == "PASS"
    assert expected["cached_consent_cannot_bypass_withdrawal"] is True
    raw = canonical(data)
    assert "fictional-alex" not in raw and "fictional-blair" not in raw


@pytest.mark.parametrize("kind", ["missing", "invalid", "stale", "unauthorized"])
def test_exported_packet_negative_evidence(kind: str) -> None:
    data = fixture()
    for packet in data["packets"]:
        args = arguments(packet, data)
        ref = packet["work"]["evidence"][0]["reference"]
        if kind == "missing":
            args["receipts"] = {}
            args["provenance"] = {}
        elif kind == "invalid":
            args["receipts"] = {ref: b"modified synthetic receipt"}
        elif kind == "stale":
            prov = packet["provenance"] | {"checked_on": "2026-10-01", "expires_on": "2026-10-20"}
            args["provenance"] = {ref: canonical(prov)}
        else:
            args["verifiers"] = frozenset()
        review = review_for_human(**args)
        assert review["body"]["readiness"] == "REJECTED"
        with pytest.raises(PermissionError):
            record_simulated_decision(
                **args,
                expected_review_sha256=review["sha256"],
                reviewer_id=data["reviewers"][0],
                disposition="DEFER",
                explicitly_simulated=True,
            )
