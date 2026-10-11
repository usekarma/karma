# Offline governance and isolation proof

Status: simulated proof only, no merge or execution authority. Existing work-v1 bytes
and schema remain unchanged. No external framework, real data, account/provider
connections, financial/clinical actions, AWS changes or autonomous dispatch.

AC-201: Independently configured synthetic verifier/producer policy checks strict
provenance envelopes against work/evidence/artifact/receipt digests, source revision,
validity, revocation and a maximum seven-day age. Missing, invalid, stale and
unauthorized evidence rejects review readiness; raw receipt integrity is still checked
by existing Karma code. Failed and UNKNOWN evidence never becomes verified.

AC-202: Review readiness freshly evaluates existing dependency and single-active-task
rules, preserves the external active slot and retains STOP_FOR_HUMAN. Approval is
not inferred from evidence, a proposal, issue text or a prepopulated decision. A new
review target must be pending human review; no automatic state change occurs.

AC-203: Recording requires a separately supplied explicit simulated=true decision,
trusted fictional reviewer, exact work/artifact/review binding and revalidation of
current evidence, consent/disclosure scope, dependencies and active context. Default
or actual approval is refused. Simulated disposition never authorizes action or closes
the work. Revocation or snapshot changes between review and record deny.

AC-204: Pure append-only-style audit receipts bind sequence, prior digest, review
snapshot, fixed date, simulated reviewer/disposition, active identity and the invariant
STOP_FOR_HUMAN/execution_authorized=false. Inputs are immutable; history corruption,
reordering, replay, unknown fields and modified receipt contents reject. Hash chains
show byte consistency, not authenticated/tamper-proof real-world human approval.

AC-205: Prudence actually generates its local synthetic decision brief and emits only
an opaque safe work packet plus synthetic check provenance. Human recommendation
review stays local; Karma receives no financial amounts or private brief text. All
three existing packages participate in the local harness without network orchestration.

AC-206: Aegis creates two fictional profiles, denies cross-profile reads, rechecks
withdrawn consent and exports permitted minimal metadata only. Noninterference tests
hold work identity/safe metadata constant while changing private profile data and
verify byte-identical exports. Do not share hashes of private profile contents,
member IDs, medications, categories, dates or plaintext in work packets. This proves
absence/noninterference for tested contents, not mathematical anonymity against every
side channel or an authenticated production consent system.

## Execution evidence

Synthetic fixture policies/decisions must be labelled simulated. No current real human
approval or active registry state is claimed. Safe Karma fixtures contain check metadata
only; domain artifacts stay in their private repositories. Local cross-repository harness
results and per-repository CI are separate evidence; CI consumes safe frozen packets
without tokens/cloning private repositories. Preserve all prior work and PR heads.

Current-state withdrawal is demonstrated through ProfileVault: retained consent
objects cannot be supplied to its read/export APIs. The source simulation never
permits a non-owner to withdraw another fictional adult's grant. Real identity and
persistent/atomic revocation still need separate production design and approval.
