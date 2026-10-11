# Coordination privacy and authority threats

Assets: minimal synthetic work metadata, safe check receipts and review records.
Entry points: strict JSON and caller-provided receipt inventory. Threats: extra raw
record fields, data hidden in names/URLs, duplicate keys, forged VERIFIED/approval
claims, stale digests, replayed/revoked permissions, cyclic dependencies, simultaneous
active tasks, and unsafe reinterpretation of a report as execution permission.

Controls: exact fields at every nesting level; opaque fixed-format identifiers;
enumerated conditions; bounded inputs; fresh expiry/revocation checks; receipt hash
and PASS verification; approval work/artifact/scope binding; read-only slot preservation;
always STOP_FOR_HUMAN; no dispatch function, network, persistence or credentials.
Aegis separately rechecks individual consent before metadata export. Shared evidence
is check-only metadata, never personal data. Denial errors omit raw values.

Residual: caller can fabricate synthetic grants and self-consistent receipt hashes.
Opaque IDs/digests can correlate activity or covertly encode data. Synthetic metadata
is not an authenticated audit trail. Real identity, consent, retention, encryption,
provenance and security/clinical/financial professional reviews remain unimplemented.
No safeguards here authorize real-data integration. Human review required.

## Governance proof boundary

See governance-proof.md and specs/governance-proof.md. Fresh verifier/source policy,
explicit simulated decisions and hash-linked receipts supplement unchanged work-v1.
Aegis's trusted current in-memory consent state is tested against withdrawal and stale
copy reuse; private content is excluded before sharing. No network executor, actual
human approval, activation or production integration is implemented.
