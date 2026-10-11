# Minimal steward metadata contract v1

Authority: user-authorized offline synthetic integration only. Karma issues #4 and #5.
This supplements docs/faraday-work-intake.md; it does not replace the strategic queue
or authorize the active Faraday/device direction to change.

## Trust and representation

Strict versioned JSON, exact allowed fields, bounded collections and opaque IDs.
No unrestricted strings, payloads, URLs to records or personally identifying aliases.
Duplicate keys, unsupported versions, raw records, NaN and oversized inputs reject
with field-category-only errors. Schema permits no additional properties at any object.
Validation is on every call. Root state/approval fields remain claims.

## Acceptance

AC-001: Strict decoding validates metadata and rejects unexpected or sensitive fields,
wrong types, duplicate keys, unsupported versions, oversized lists and non-opaque IDs.

AC-002: Sharing requires explicit synthetic=true, authorized=true, revoked=false and
an expiry after the supplied fixed date. Missing, revoked, expired or real-data grants
fail closed before returning metadata. Aegis additionally applies individual consent
at its export boundary; permission on one member cannot disclose another member.

AC-003: Evidence stays UNKNOWN unless it was declared VERIFIED and a separately
supplied strict synthetic check receipt has matching raw-byte SHA-256, reference and
PASS result. Missing, invalid, mismatched or unresolved receipts never become VERIFIED.
Declared/observed failure remains visible. Receipts contain only check IDs/results;
no domain records. Hash consistency does not authenticate a verifier.

AC-004: Human approvals bind work ID, artifact digest, offline scope, reviewer,
issuance, expiry and revocation. Stale/wrong/expired/denied approvals are not valid.
Even a valid approval never grants merge, external access or agent execution; all
reports retain STOP_FOR_HUMAN and dispatch is not implemented.

AC-005: Snapshot inspection is read-only and preserves the externally supplied
current-active-work identity. Two active claims, or a new active claim that conflicts
with the existing slot, reject. No automatic selection, transition or dispatch occurs.
Missing dependencies, cycles and incomplete dependencies remain blocked/UNKNOWN.
CLOSED claims require checked evidence, metadata review and resolved dependencies.

AC-006: Reports are deterministic and include safe audit entries (work ID, source
metadata hash, decision and fixed gate). Inputs, failure claims and unknowns survive
inspection; no optimistic promotion, mutation, logging, persistence or network occurs.

## Limits

At most 64 items, 16 dependencies/evidence references/conditions each, 16 KiB per work
JSON and 4 KiB per synthetic receipt. Fixed supplied calendar date; no ambient clock.
Opaque IDs can still correlate activity; approval is required even for metadata.
Audit reports are synthetic local evidence, not tamper-proof authenticated audit logs.
Production identity, consent authority, encryption, retention and recovery are unresolved.

AC-007: Canonical implementation/schema hashes are pinned in a version manifest and
checked against exact bytes. Consumers run the shared conformance corpus offline.
