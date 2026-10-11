# Offline Prudence/Aegis coordination

Requirements: [Karma #4](https://github.com/usekarma/karma/issues/4) and
[Karma #5](https://github.com/usekarma/karma/issues/5).
This component follows the existing [Faraday work intake](../docs/faraday-work-intake.md)
without changing that lifecycle, queue, runtime, APIs, streaming lanes or deployments.

`karma.steward-work.v1` carries only opaque work/owner/evidence IDs, lifecycle claims,
dependencies, artifact digests, human review records and enumerated UNKNOWN/failure
conditions. Sharing itself requires explicit unexpired, unrevoked synthetic permission.
No text bodies, raw records, financial amounts, diagnoses, medications or family IDs
are accepted. Every report retains STOP_FOR_HUMAN; approval never dispatches an agent.

Python 3.12: `./scripts/bootstrap.sh`, `make check`, `make test` from this directory.
Schema, behavioral spec and conformance tests live in contracts/ and specs/.
Canonical implementation is src/steward_coordination/contract.py; Prudence and Aegis
vendor identical bytes into their isolated namespaces, with hash/version manifests.
No runtime repository fetching or shared sensitive store is introduced.

Consent and review records are synthetic assertions, not authenticated real-world grants.
Hashes establish byte consistency, not author identity. Future real metadata can itself
be sensitive and needs separate minimization/authorization review. Production is blocked.
STOP_FOR_HUMAN.

## Frozen coordination demonstration

Run `.venv/bin/python scripts/demo.py`. Two fictional pending work items retain an
external active-work slot, checked synthetic test evidence and missing human review.
The dependent item stays blocked. examples/snapshot.expected.json pins the output;
no transition, transmission or dispatch occurs.

## First governance proof

[Proof and security evidence](docs/governance-proof.md) ·
[Exact parent merge plan](docs/merge-readiness.md) ·
[Proof contracts](specs/governance-proof.md).
Explicit simulation retains STOP_FOR_HUMAN and never grants execution or merge authority.

Local cross-repository execution requires reviewed local producer checkouts installed
in this virtual environment, with no network fetching:

```bash
.venv/bin/python -m pip install --no-deps --no-build-isolation -e "$PRUDENCE_CHECKOUT" -e "$AEGIS_CHECKOUT"
.venv/bin/python scripts/end_to_end.py
.venv/bin/python scripts/end_to_end.py --simulate-decision
```

Set those two variables to the approved local checkout paths. The first command
installs local code only. The default proof stops before recording a decision; the
explicit flag records fictional DEFER only. `--write-fixtures` writes safe synthetic
metadata artifacts, never private briefs/profiles. CI uses those frozen packets and
does not fetch the private repositories. No external orchestration framework.
