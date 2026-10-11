import hashlib
import json
from pathlib import Path


def test_vendor_manifest_matches_exact_schema_and_implementation() -> None:
    root = Path(__file__).parents[1]
    manifest = json.loads((root / "contracts/steward-work.v1.manifest.json").read_text())
    implementation = root / "src/steward_coordination/contract.py"
    schema = root / "contracts/steward-work.v1.schema.json"
    assert (
        hashlib.sha256(implementation.read_bytes()).hexdigest() == manifest["implementation_sha256"]
    )
    assert hashlib.sha256(schema.read_bytes()).hexdigest() == manifest["schema_sha256"]
    assert manifest["version"] == "karma.steward-work.v1"
    assert manifest["runtime_fetch"] is False
