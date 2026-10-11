# Coordination architecture

Canonical strict metadata implementation and schema are versioned in this component.
Prudence and Aegis vendor identical bytes into their isolated namespaces and pin
hash manifests. All three run the same conformance corpus. No runtime GitHub/API
fetching, service, scheduling, webhook processing or agent execution is introduced.

Caller provides bounded serialized synthetic metadata, safe synthetic check-receipt
bytes, a fixed date and the already-existing active-work identity. Decoder rejects
unknown fields and ambiguous IDs. Per-person consent stays in Aegis; no member IDs,
care categories, due dates, medications or records enter shared work metadata.
Prudence keeps compensation, cash flow and account-related information local.

Inspector validates sharing, evidence receipts, human review claims and dependency
closure; then emits a deterministic snapshot plus safe audit digests. It does not
change any state. CLOSED is a claim until required evidence/review/dependencies are
satisfied. Missing sources and explicit failures remain visible. No more than one
active claim may match the supplied slot; external active work is preserved.

Every output retains STOP_FOR_HUMAN. Review scopes are offline_preparation or
metadata_review only, never merge/access/execution. Hashes detect byte changes but
cannot establish identity, consent authority or authentic human approval.

The active slot in the frozen demo is a synthetic opaque alias, not a fetched live
Faraday registry value. No real active direction is changed or declared complete.
The prototype checks consistency of supplied snapshots; authenticity of the live
registry and bindings remains a future reviewed integration prerequisite.

## Governance proof boundary

See governance-proof.md and specs/governance-proof.md. Fresh verifier/source policy,
explicit simulated decisions and hash-linked receipts supplement unchanged work-v1.
Aegis's trusted current in-memory consent state is tested against withdrawal and stale
copy reuse; private content is excluded before sharing. No network executor, actual
human approval, activation or production integration is implemented.
