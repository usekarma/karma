import json
from datetime import date
from pathlib import Path

from steward_coordination.contract import canonical, inspect_snapshot


def test_frozen_coordination_example() -> None:
    root = Path(__file__).parents[1] / "examples"
    values = json.loads((root / "work-items.json").read_text())
    receipt = (root / "check-receipt.json").read_bytes()
    ref = json.loads(receipt)["reference"]
    result = inspect_snapshot(
        tuple(canonical(w) for w in values), {ref: receipt}, date(2026, 10, 11), "wk-" + "3" * 32
    )
    assert result == json.loads((root / "snapshot.expected.json").read_text())
    assert result["current_active_work_id"] == "wk-" + "3" * 32
    assert all(r["approval_valid"] is False for r in result["items"])
    assert all(r["gate"] == "STOP_FOR_HUMAN" for r in result["items"])
    assert "dependency_unknown" in result["items"][1]["conditions"]
