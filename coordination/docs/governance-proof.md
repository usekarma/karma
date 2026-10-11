# Karma first governance proof

## Evidence

October 11, 2026, Python 3.12.3, unchanged hash-locked v2 tooling. Original five PRs
were tested at exact heads in merge-readiness.md; all CI runs were explicitly rerun.
This follow-up's make check passes: 118 deterministic tests, 100% application branch
coverage (90% threshold retained), Ruff format/lint, strict mypy, selected credential
scan, Bandit and live pip-audit (no known vulnerabilities). make test is run separately.
Production readiness remains prototype; --production is expected to fail closed.

The local cross-repository CLI imports actual Prudence, Aegis and Karma packages,
checks unchanged work-v1 hashes, generates a financial brief locally, sends only safe
synthetic work/check packets, and evaluates provenance, dependencies and active identity.
Default invocation produces NO decision. Explicit --simulate-decision records only
fictional DEFER receipts; simulated=true, execution_authorized=false and STOP_FOR_HUMAN
remain present. A minimal opaque revocation reference marks the prior packet revoked
in the trusted synthetic inventory; replay is rejected. Only the unaffected profile
exports a fresh packet after withdrawal. Work approval remains null; no closure, action or task activation occurs.

Observed negative evidence: missing, invalid, stale and unauthorized packets reject.
Missing dependencies and conflicting active claims also reject. Audit tests reject
changed snapshots, revoked sharing/provenance, wrong reviewers, replay, corrupt/reordered
history, backdating, over-limit history and attempts to mark execution authorized.

Aegis's in-memory ProfileVault uses current grants rather than caller-supplied cached
copies. Both cross-profile reads deny; owner withdrawal blocks later reads AND exports
while the original consent copy remains unrevoked. The other fictional profile remains
accessible under its own grant. Non-owner withdrawal denies. Private profile mutations
leave exported bytes identical; packets contain no private fields or private-record
content hashes. Shared artifact digests cover structural metadata only.

v1 implementation SHA-256:
16718a114edb22836bf4d2001af48069867333fd6da7aa68bce19d523c9f1cb3
v1 schema SHA-256:
c2ea629fb0e479a6965a56992aa2e63a709bef77d1a39ef41eac84e7d8994e0b
Both match all three existing manifests. No v1 bytes or parent PR head was changed.

## Limitations

Synthetic identities, verifier/reviewer registries and explicit simulated decisions
are fixtures, not authenticated real people or actual human approval. Code/receipt
hashes prove byte consistency, not signatures or true clinical/financial facts.
The profile vault is an in-memory API model, not secure against a hostile Python
process, a durable consent service, crash recovery or distributed cache races.
Previously disclosed metadata cannot be retracted; no private plaintext is sent.
Noninterference covers tested content changes, not universal anonymity or resistance
to correlation/outside knowledge. No real active registry was queried; its supplied
opaque fixture identity is preserved. CI tests safe frozen packets without access to
private repositories; actual cross-repository execution was performed locally.
No real data, provider/account connection, financial/medical action, AWS change,
autonomous approval, agent dispatch or merge occurred.

## Approval boundary

Merge-readiness.md supplies the exact original source heads and staged approval order.
Review follow-up PRs and current CI at their exact final heads. No simulated receipt
or passing check grants merge, production, external-data or execution permission.
STOP_FOR_HUMAN.
