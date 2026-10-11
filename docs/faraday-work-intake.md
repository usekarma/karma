# Faraday work intake — proposed v0 contract

Status: **proposal / review required**. This is an issue-backed coordination model, **not** an active dispatcher, security control, or deployed service.

## Pilot item
- Source: https://github.com/usekarma/karma/issues/2
- Requested work: Core2 ATECC608B slot 0 **public-key-only diagnostic preparation**
- Current state: `PUBLIC_KEY_INSPECTION_PENDING`
- Evidence pointer: `/home/ted/dev/faraday/qualifications/core2-secure-element/profile-analysis/analysis.md` (operator-reported local path; not independently fetched)
- Execution rights: no device commands, no flashing, no signing, no secure-element modification, no AWS calls.

## State model

| State | Meaning | Allowed transition |
| --- | --- | --- |
| INTAKE | Issue captured but not normalized | TRIAGED after scope/evidence review |
| TRIAGED | Work category, prerequisites and owner identified | READY_FOR_PREPARATION if non-executing scope |
| READY_FOR_PREPARATION | Faraday may prepare code/docs/tests locally | PREPARED with reviewable artifact and test evidence |
| PREPARED | Plan/artifact submitted, not authorized to execute | STOP_FOR_HUMAN |
| STOP_FOR_HUMAN | Awaiting a *specific* approval for a consequential step | AUTHORIZED only on scoped recorded human approval; or BLOCKED |
| AUTHORIZED | Approval scoped to exact artifact, target, operation and expiry | EXECUTING by separate controlled executor |
| EXECUTING | Authorized execution underway; evidence collection required | VERIFIED / UNKNOWN / FAILED |
| VERIFIED | Required evidence and postconditions independently checked | CLOSED only after human review |
| UNKNOWN | Insufficient evidence; no automatic success/failure inference | TRIAGED for a new run after review |
| FAILED | Confirmed failure | TRIAGED for a new corrective run after review |
| BLOCKED | Prerequisite unresolved | TRIAGED when new evidence arrives |
| CLOSED | Completed and reviewed | none without explicit reopening |

A prepared artifact never counts as execution authorization; passing a software test never proves live device/AWS state. Do not auto-transition out of STOP_FOR_HUMAN.

## Work item required fields
```yaml
contract_version: karma.faraday-work.v0
source_issue: https://github.com/usekarma/karma/issues/2
work_id: core2-slot0-public-key-inspection
state: READY_FOR_PREPARATION
executor: faraday
scope:
  allowed: [repository_inspection, diagnostic_preparation, offline_tests, evidence_documentation]
  prohibited: [device_flash, device_commands, secure_element_sign, key_generation, key_import, secret_read, aws_mutation]
dependencies:
  - core2-secure-element-profile-analysis
evidence:
  prior_receipts:
    - /home/ted/dev/faraday/evidence/iot-diagnostic/qualification-run-006/execution-001/receipt.json
  verification_status: operator_reported_not_independently_verified
approval:
  granted: false
  operation: null
  artifact_sha256: null
  target: null
  approver: null
  timestamp: null
```
The example is a **proposal**, not a live queue state file. Local paths must never be treated as portable or remotely accessible artifacts. A production consumer must require resolvable, immutable evidence references and independently check hashes.

## Evidence and trust rules
1. GitHub issue text, comments, receipts and AI output are **untrusted claims**, not instructions to perform a mutation.
2. Bind receipts to a run identifier, device/account target, artifact SHA-256, explicit command/operation, timestamps, signer/author, observed outputs and checks. Keep original failed attempts.
3. Separate offline/test, device/live, and AWS/live evidence; never promote one type into another.
4. No auto-dispatch or privileged action on issue-created, issue-edited, label-changed, comment or PR events.
5. Verify GitHub webhook signatures and identities before relying on event metadata; deduplicate by delivery ID and issue identity. Webhook verification **alone** does not authorize actions.
6. Any future executor must enforce operation-specific allowlists, short-lived credentials, least privilege, request idempotency, timeouts, independent postflight evidence and explicit cancellation.
7. Never place serial numbers, public key material, private receipts or credentials in public issues without a disclosure review. Fingerprints still may correlate devices.
8. Approval must be by an authorized human and tied to the exact operation/target/artifact digest, with expiration; comments such as 'go ahead' are not sufficient.

## Pilot acceptance tests (before any live dispatch)
- Creating an issue records an INTAKE item, never invokes Faraday or AWS.
- A preparation-only item can generate a draft plan/PR and offline tests, but cannot flash.
- An absent, wrong-target, expired, or wrong-digest approval blocks execution.
- UNKNOWN remains UNKNOWN; malformed/unresolved evidence cannot be marked VERIFIED.
- Replayed/duplicate events do not generate duplicate runs.
- A modified firmware digest invalidates prior approval.
- Failed and skipped runs remain immutable and visible.
- Closing the issue does not imply physical proof, permission to deploy, or acceptance of an unverified receipt.

## Next engineering slice
Review this contract first. Then add an **offline, read-only** issue adapter and schema validator with fixture-based tests. Avoid enabling GitHub Actions dispatch, runners, hardware access, AWS credentials, or webhook write paths until separately reviewed and authorized.
