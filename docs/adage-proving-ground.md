# Karma as Adage's proving ground

Karma is an experimental workload for understanding events and change. Adage defines the infrastructure control model; Karma provides a concrete place to test its results. Governance controls belong in the authorized infrastructure workflow and IAM/execution boundaries, rather than being inferred from Karma's name or event graph.

## Evidence before capability claims

The repository contains normalization implementations, schemas, mappings, ClickHouse SQL, development services, and API scaffolding. Graph queries are mocked, graph insertion is a TODO, predictor/detector jobs are placeholders, and action examples are pseudocode. These are useful engineering starting points, not a finished graph platform or production automation system.

The website's Neptune, CLI, coordinated-change, audit-history, and machine-learning pages describe design directions. They must not be treated as deployed features. Historical infrastructure or a working demo does not establish that every current source path is complete or that AWS services remain running.

## Engineering loop

A bounded objective leads to a specification with acceptance criteria. An agent inspects `aws-config`, `aws-iac`, and relevant Karma code, prepares changes, runs deterministic checks, generates plans where possible, and produces an evidence/risk report. A human owns the consequential execution decision. Read-only post-change checks and later cost/health observations test the result.

[Adage](https://github.com/usekarma/adage) explains the architecture, and [agent-business-solution-template](https://github.com/usekarma/agent-business-solution-template) supplies the general methodology. Supporting agent controls are under review in [aws-iac PR #1](https://github.com/usekarma/aws-iac/pull/1) and [aws-config PR #1](https://github.com/usekarma/aws-config/pull/1). Do not assume those changes are active on `main`.

## First cost proof

**Status: to validate; no complete public end-to-end proof is claimed here.**

Explain every cent of AWS spend above the owner-specified $0.51/month strall.com and $0.61/month usekarma.dev targets ($1.12/month combined), identify infrastructure causes, map them to desired state/IaC where possible, and prepare safe remediation without destructive changes.

These targets apply to the intended minimal steady state for the two sites. They do not represent the full historical Kafka/ClickHouse/MongoDB/Grafana stack, and they do not include adage.usekarma.dev. A report must explicitly reconcile wider account spend and explain any resources outside the target's scope.

Required evidence:

- Repository revisions and an explicit desired-state inventory.
- Read-only observations across declared accounts/regions, with inaccessible scope marked.
- Billing period, cost basis, usage assumptions, shared charges, and a ledger that reconciles to billing precision.
- Resource/service attribution, ownership, and mapping to configuration/IaC where supported.
- Proposed remediation, estimated savings, dependencies, service impact, persistent-data risk, and recovery requirements.
- Deterministic check results and relevant plans, with failures or missing access recorded as blockers.

Success means no unexplained excess and no unobserved scope silently counted as empty. If attribution is unavailable or the target omits unavoidable charges, report the limitation and revise assumptions with the owner. Estimated savings become proven savings only after separately authorized execution and later billing observation.

Agents may prepare evidence and changes. Production apply/destroy, data deletion, SSM writes, environment rebinding, sensitive IAM/security changes, and irreversible operations require explicit human authorization. Raw plans and evidence may contain sensitive values; publish only redacted summaries.

## Next measurable steps

Complete the infrastructure cost proof before expanding automation. Separately validate one synthetic event path from normalized input to ClickHouse query output. Replace API mocks or job placeholders only against explicit behavior contracts and observed tests. Persistent graph storage, autonomous actions, and predictive recommendations remain future directions until their own evidence exists.

Link a public, redacted proof artifact here when one is available.
