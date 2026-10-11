"""Local cross-repository proof. Install approved local packages; no fetching or services."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from datetime import date
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any

from steward_coordination.contract import canonical, digest
from steward_coordination.governance import record_simulated_decision, review_for_human

TODAY = date(2026, 10, 11)
ACTIVE_ID = "wk-" + "e" * 32
REVIEWER_ID = "actor-" + "f" * 32


def source_revision(module: ModuleType) -> str:
    if module.__file__ is None:
        raise ValueError("approved local module has no source artifact")
    return digest(Path(module.__file__).read_bytes())


def run(*, simulate_decision: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    """Execute actual producer/isolation APIs locally, sending strict metadata to Karma."""
    finance = import_module("prudence.governance")
    health = import_module("aegis.isolation")
    shared = [
        import_module(n)
        for n in ("prudence.coordination", "aegis.coordination", "steward_coordination.contract")
    ]
    source_hashes = [source_revision(m) for m in shared]
    if len(set(source_hashes)) != 1:
        raise ValueError("cross-repository work contract mismatch")
    finance_revision = source_revision(finance)
    health_revision = source_revision(health)
    proposal = finance.build_proposal(TODAY, finance_revision, metadata_permission=True)
    alex, blair = health.fictional_profiles()
    ca, cb = health.fictional_consent(alex, TODAY), health.fictional_consent(blair, TODAY)
    vault = health.ProfileVault((alex, blair), (ca, cb))
    vault.read(alex.member.member_id, alex.member.member_id, TODAY)
    vault.read(blair.member.member_id, blair.member.member_id, TODAY)
    packet = vault.packet(alex.member.member_id, alex.member.member_id, TODAY, health_revision)
    denied = 0
    for subject, requester in (
        (blair.member.member_id, alex.member.member_id),
        (alex.member.member_id, blair.member.member_id),
    ):
        try:
            vault.read(subject, requester, TODAY)
        except PermissionError:
            denied += 1
    revoked_ref = vault.withdraw(
        alex.member.member_id, alex.member.member_id, actor_id=alex.member.member_id
    )
    try:
        vault.read(alex.member.member_id, alex.member.member_id, TODAY)
    except PermissionError:
        denied += 1
    try:
        vault.packet(alex.member.member_id, alex.member.member_id, TODAY, health_revision)
    except PermissionError:
        denied += 1
    if denied != 4 or ca.revoked:
        raise ValueError("profile isolation or current-state revocation proof failed")
    vault.read(blair.member.member_id, blair.member.member_id, TODAY)
    altered = replace(
        alex,
        care=replace(alex.care, guidance_reference="changed-private-plan"),
        medication=replace(
            alex.medication, fictional_medication_label="changed-private-medication"
        ),
    )
    alternate_vault = health.ProfileVault((altered,), (ca,))
    if packet != alternate_vault.packet(
        alex.member.member_id, alex.member.member_id, TODAY, health_revision
    ):
        raise ValueError("private content affected shared metadata")
    permitted_packet = vault.packet(
        blair.member.member_id, blair.member.member_id, TODAY, health_revision
    )
    packets = [
        (proposal.work_json, proposal.check_receipt, proposal.provenance_json),
        permitted_packet,
    ]
    registry = {finance.PRODUCER_ID: finance_revision, health.PRODUCER_ID: health_revision}
    verifiers = frozenset({finance.VERIFIER_ID, health.VERIFIER_ID})
    reviewers = frozenset({REVIEWER_ID})
    revoked_source = json.loads(packet[2]) | {"revoked": True}
    if revoked_source["reference"] != revoked_ref:
        raise ValueError("revocation evidence identity mismatch")
    replay = review_for_human(
        (packet[0],),
        {revoked_ref: packet[1]},
        {revoked_ref: canonical(revoked_source)},
        TODAY,
        json.loads(packet[0])["work_id"],
        ACTIVE_ID,
        registry,
        verifiers,
        reviewers,
    )
    if replay["body"]["readiness"] != "REJECTED":
        raise ValueError("cached withdrawn metadata was accepted")
    outcomes: list[dict[str, Any]] = []
    for raw, check, source in packets:
        w = json.loads(raw)
        ref = w["evidence"][0]["reference"]
        args = {
            "raw_items": (raw,),
            "receipts": {ref: check},
            "provenance": {ref: source},
            "today": TODAY,
            "target_work_id": w["work_id"],
            "current_active_work_id": ACTIVE_ID,
            "producers": registry,
            "verifiers": verifiers,
            "reviewers": reviewers,
        }
        reviewed = review_for_human(**args)
        if reviewed["body"]["readiness"] != "AWAITING_SIMULATED_HUMAN":
            raise ValueError("valid synthetic work rejected")
        receipts: tuple[str, ...] = ()
        if simulate_decision:
            receipts = record_simulated_decision(
                **args,
                expected_review_sha256=reviewed["sha256"],
                reviewer_id=REVIEWER_ID,
                disposition="DEFER",
                explicitly_simulated=True,
            )
        negatives: dict[str, str] = {}
        for case in (
            "missing",
            "invalid",
            "stale",
            "unauthorized",
            "missing_dependency",
            "active_conflict",
        ):
            changed = dict(args)
            if case == "missing":
                changed["receipts"], changed["provenance"] = {}, {}
            elif case == "invalid":
                changed["receipts"] = {ref: b"invalid synthetic receipt"}
            elif case == "stale":
                p = json.loads(source) | {"checked_on": "2026-10-01", "expires_on": "2026-10-20"}
                changed["provenance"] = {ref: canonical(p)}
            elif case == "unauthorized":
                changed["verifiers"] = frozenset()
            elif case == "missing_dependency":
                altered_work = w | {"dependencies": ["wk-" + "d" * 32]}
                changed["raw_items"] = (canonical(altered_work),)
            else:
                altered_work = w | {"active": True}
                changed["raw_items"] = (canonical(altered_work),)
            try:
                result = review_for_human(**changed)
            except ValueError:
                if case != "active_conflict":
                    raise
                negatives[case] = "REJECTED"
                continue
            if result["body"]["readiness"] != "REJECTED":
                raise ValueError("negative evidence unexpectedly accepted")
            negatives[case] = "REJECTED"
        outcomes.append(
            {
                "work_id": w["work_id"],
                "review": reviewed,
                "simulated_decision_receipts": [json.loads(r) for r in receipts],
                "negative_evidence": negatives,
            }
        )
    # No private domain text/value/hash is stored or printed in these artifacts.
    fixture = {
        "packets": [
            {
                "work": json.loads(raw),
                "receipt": json.loads(check),
                "provenance": json.loads(source),
            }
            for raw, check, source in packets
        ],
        "producers": registry,
        "verifiers": sorted(verifiers),
        "reviewers": sorted(reviewers),
        "current_active_work_id": ACTIVE_ID,
    }
    summary = {
        "synthetic": True,
        "financial_brief_generated_locally": bool(proposal.brief),
        "as_of": TODAY.isoformat(),
        "contract_hash": source_hashes[0],
        "profile_denials": denied,
        "private_data_noninterference": "PASS",
        "cached_consent_cannot_bypass_withdrawal": True,
        "revoked_packet_replay": "REJECTED",
        "work": outcomes,
        "gate": "STOP_FOR_HUMAN",
        "execution_authorized": False,
    }
    return summary, fixture


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--simulate-decision",
        action="store_true",
        help="Record fictional DEFER receipts; never actual approvals",
    )
    parser.add_argument(
        "--write-fixtures",
        action="store_true",
        help="Write only safe synthetic metadata proof artifacts",
    )
    args = parser.parse_args()
    summary, fixtures = run(simulate_decision=args.simulate_decision)
    if args.write_fixtures:
        root = Path(__file__).resolve().parents[1] / "examples"
        (root / "governance-packets.json").write_text(json.dumps(fixtures, indent=2) + "\n")
        (root / "governance-proof.expected.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
