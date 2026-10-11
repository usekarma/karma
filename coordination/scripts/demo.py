"""Inspect fixed fictional check metadata, preserving an existing active task."""

import json
from datetime import date
from pathlib import Path

from steward_coordination.contract import canonical, inspect_snapshot

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    values = json.loads((ROOT / "examples/work-items.json").read_text())
    receipt = (ROOT / "examples/check-receipt.json").read_bytes()
    reference = json.loads(receipt)["reference"]
    result = inspect_snapshot(
        tuple(canonical(w) for w in values),
        {reference: receipt},
        date(2026, 10, 11),
        "wk-" + "3" * 32,
    )
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
