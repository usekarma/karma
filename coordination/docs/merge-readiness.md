# Exact merge-readiness plan — no merge authorized

## Inspected and revalidated source heads

| PR | Exact source head | Current base | Tests |
| --- | --- | --- | ---: |
| Prudence #1 | `624a9515cabca01dc24c14822e39bb01d7a340b2` | `main` | 38 |
| Prudence #2 | `65f37dd31522f5d33f74d8709f9ddb4f5d6fd4e0` | `bootstrap/prudence` | 109 |
| Aegis #1 | `8d9b999a5e9af543874f98369bbb943b499908f8` | `main` | 42 |
| Aegis #2 | `141179f38e277a9ba55ee66ce7d84920a746e0fd` | `bootstrap/aegis` | 111 |
| Karma #6 | `09c109f80d15fb4a4199b396ca65551f2e6f5f52` | `main` | 75 |

Each original PR is open/MERGEABLE; exact-head local gates passed and existing CI runs
were explicitly rerun successfully. All application branch coverage is 100%. Ancestor
checks confirm each integration contains its exact bootstrap head; v1 source/schema
bytes match across all three. No existing branch was rebased, reset, force-pushed,
retargeted, discarded or merged. No bootstrap correctness/security blocker found for
its explicitly offline synthetic scope. This is not production acceptance.

## Candidate order, subject to separate human approval at every step

1. Approve the exact Prudence #1 and Aegis #1 source heads independently for main.
2. Approve Karma #6's exact head as the canonical offline work-v1 foundation.
3. After approved bootstrap merges, retarget Prudence/Aegis #2 to main, verify the
   resulting base and head and rerun/review CI. Obtain separate integration merge
   approvals; bootstrap approval never includes #2.
4. Review the three new proof branches together. Each is stacked on the corresponding
   #2/#6 branch and needs separate exact-head approval after its parent is merged,
   retargeted and revalidated. Final proof heads are recorded in PR descriptions and
   the completion report; this document does not attempt to predict its own Git SHA.

All three repositories currently permit merge commits, squash and rebase merges.
Candidate strategy: merge commits preserve approved parent SHAs and the stack's
ancestry if current rules permit. If the human chooses squash/rebase or linear-history
rules require it, rebase only the affected child onto the new main, preserving its
unique patches, then revalidate and seek approval for its NEW exact SHA. Never reuse
old head approval after a rewrite. Do not rewrite unrelated branches or delete work.
Main result merge SHAs cannot be known before the human-authorized GitHub operation.
Check exact source head, latest main, CI and rules immediately before execution; no
admin bypass, auto-merge or automatic dispatch is proposed.

## Remaining governance blockers

No human merge approvals exist. Private main-protection API reads remain HTTP 403
(plan entitlement); Karma main remains HTTP 404 Branch not protected. Protections
were not changed. Desired protections need independent reviewer assignment and a
separately approved operation. Merging code does not grant data/provider/cloud access.
Identity, signed provenance, real consent authority, durable/atomic revocation,
retention/encryption, immutable audits and professional/operational evidence remain
unimplemented. Preserve prototype production blockers and STOP_FOR_HUMAN.
