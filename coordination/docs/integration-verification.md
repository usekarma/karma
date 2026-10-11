# Karma Coordination integration evidence

## Evidence

Executed October 11, 2026 (America/Chicago), Python 3.12.3, unchanged template v2
hash-locked development tools. make check exited 0: executable acceptance mappings,
selected credential scan, Ruff format/lint, strict mypy, 75 pytest tests, 100%
application branch coverage against the retained 90% gate, Bandit and live pip-audit.
The dependency audit found no known vulnerabilities. make test exited 0 (75 passed).
The initial audit attempt failed closed on sandbox DNS; rerunning unchanged with
network access passed. No audit bypass, coverage reduction or security suppression.

Production gate exited 1: Production blocked: stage is not production. Expected
safety result, not release readiness. New CI runs the same checks; inspect the exact
published PR head and attached checks before any human merge decision.

Shared code SHA-256: 16718a114edb22836bf4d2001af48069867333fd6da7aa68bce19d523c9f1cb3.
Executed cross-repository comparison confirmed byte-identical implementations, schema
and manifests. Each repository runs the same negative conformance corpus; this is
consistency testing of shared code, not independent implementations or authenticators.
Ignored artifacts/ holds JUnit, branch coverage, Bandit and audit JSON reports.

## Correctness, isolation and failure behavior

Known-answer fixture checks and cross-repository privacy/authorization tests were
executed. Domain demonstration details remain in the private steward repositories.
Karma's frozen snapshot preserves
an external synthetic active slot and missing human approvals/dependency closure.

Negative tests reject extra sensitive fields, invalid types, duplicate JSON keys,
wrong-domain metadata, missing disclosure permission, wrong/expired/revoked approvals,
changed artifact digests, missing/tampered receipts, multiple active claims, missing
and cyclic dependencies. UNKNOWN/failures remain visible, and no approval removes
STOP_FOR_HUMAN. Safe audit entries contain opaque work IDs, metadata digests and
review decisions; no personal records or domain values. Inputs remain unchanged.

## Limitations

Synthetic contracts are not authenticated identities, guardianship, consent, human
approval or provenance. Hashes detect consistency and do not sign an audit trail.
The prototype does not query the real active-task registry, dispatch agents, connect
accounts/providers, transfer data, deploy infrastructure or execute financial/medical
actions. No real financial or medical records were accessed. Real-data encryption,
retention/deletion, revocation across distributed caches, tamper-proof audits,
professional review and production operational evidence remain unresolved.
Karma checks cover this isolated component, not legacy runtimes or end-to-end services.
No stakeholder validation, human PR approval, merge or protection application claimed.

## Required human decisions

Review and explicitly approve exact updated PR #1 revisions before merging. Review
new integration PRs and the canonical contract together; stacked PRs depend on the
bootstrap branches and must be retargeted to main after approved bootstrap merges.
Choose eligible independent reviewers and operational/privacy/security owners.
Decide organization Team/Enterprise entitlement for private main protection, then
approve exact main-protection.proposed.json operations separately. Karma is public
and current main is unprotected; its proposal needs approval rather than an upgrade.
Retain manual merge authority until enforcement is configured and verified.
STOP_FOR_HUMAN.
