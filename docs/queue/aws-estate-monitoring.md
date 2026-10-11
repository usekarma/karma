---
id: KARMA-AWS-ESTATE-001
status: queued
priority: high
owner: karma
faraday_visible: true
authority: read-only-first
active: false
---

# AWS estate monitoring

Karma should maintain an evidence-backed view of the state of all authorized AWS deployments and accounts.

## Strategic direction

Continuously reconcile desired state, deployed state, operational state, security posture, and cost across the authorized AWS estate.

For every authorized account/environment, Karma should eventually be able to answer:

- what is supposed to exist?
- what actually exists?
- what changed since the last observation?
- what is drifting from desired state?
- what is unhealthy or unreachable?
- what is generating cost?
- what appears orphaned, stale, duplicated, oversized, or unexpected?
- what security or configuration risks are present?
- what evidence supports each conclusion?
- what action is recommended?
- what remains UNKNOWN?
- what requires human approval?

Use `aws-config` as desired-state evidence and `aws-iac` as implementation evidence where applicable.

Do not assume profile names are account identity. Resolve and retain authoritative AWS account, role, and region identity for observations.

## First bounded proof

Do not build broad collectors first. The first proof should be a read-only inventory of one authorized AWS account/environment that produces source-linked evidence for:

1. authoritative account/role/region identity,
2. actual resource inventory,
3. desired-state evidence where available,
4. observed cost evidence where available,
5. stale or UNKNOWN evidence explicitly represented,
6. deterministic reconciliation output,
7. no AWS mutations.

Success means every conclusion is traceable to retained evidence and uncertainty is preserved rather than guessed away.

## Queue semantics for Faraday

This item is deliberately **queued, not active**. Faraday should treat it as a strategic Karma work item available for prioritization when the current active direction permits it.

Faraday may inspect and rank this item, but should not automatically start implementation or AWS observation merely because the queue item exists. Existing `STOP_FOR_HUMAN` and single-active-task constraints remain binding.

Before starting this work, Faraday should confirm the current authorization boundary and propose the smallest first account-inventory experiment.
