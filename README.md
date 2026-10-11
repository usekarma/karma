# Karma

**An experimental event-driven system for understanding change—and a real workload for proving Adage's infrastructure control model.**

Karma explores how events, state, dependencies, and outcomes can make a system's behavior explainable. Its source includes Kafka normalization code, event/action contracts, ClickHouse state and latency analysis, and prototype API handlers. The longer-term goal is to connect observations with reviewable decisions and measured results.

[Website](https://usekarma.dev) · [Adage architecture](https://github.com/usekarma/adage) · [Implementation and proof status](docs/adage-proving-ground.md)

## What Karma is for

Karma asks: what happened, what changed, which entities or dependencies were affected, and what evidence supports the next decision? Event processing and queryable history provide the foundation for observability, analysis, and proposed actions.

Adage supplies the configuration-driven infrastructure model. Karma is the workload and experimental proving ground; Adage defines how infrastructure intent, implementation, runtime discovery, and controlled deployment fit together.

## What exists today

| Area | Source evidence | Current scope |
| --- | --- | --- |
| Event and action contracts | [contracts/](contracts/), [action topics](actions/topics.md) | JSON schemas and topic conventions; enforcement across every producer/consumer is not established. |
| CDC normalization | [Kafka Streams normalizer](normalizers/mongo-cdc-clickhouse-kstreams/), [Python normalizer](normalizers/mongo-cdc-clickhouse/src/normalizer.py) | Implementation source and mappings exist; deployment and end-to-end behavior need verification. |
| State and latency analysis | [ClickHouse sink SQL](sinks/clickhouse/sql/), [analysis SQL](entropy/sql/) | Table, materialized-view, and query definitions. Their presence does not prove a live pipeline. |
| Local services | [docker-compose.yml](docker-compose.yml) | Kafka/ZooKeeper and ClickHouse development services; not a complete application deployment. |
| Graph API prototype | [query handler](lambdas/karma-graph-query/main.py), [log handler](lambdas/karma-log-handler/main.py), [OpenAPI](openapi/karma-api/openapi.yaml) | Query handler returns mock graphs; logging handler prints events and has a graph insertion TODO. |
| Prediction and deviation jobs | [predictor](entropy/jobs/predictor/), [detector](entropy/jobs/deviation/) | Placeholder code and design notes, not working detection services. |
| Action processing | [actions/](actions/) | Contracts and example placeholders; no verified execution engine. |

Persistent Neptune graph integration, a complete Karma CLI/service, coordinated changes, and autonomous remediation remain proposals. Source availability is not production readiness. No complete end-to-end verification or live deployment is claimed by this README.

## Reference pipeline

The intended streaming flow is raw CDC → normalization → `events.normalized` → ClickHouse history/state/latency views → analysis → proposed actions. Normalization and SQL source exist; prediction, deviation detection, and action execution are incomplete. Kafka Connect or another source/sink integration must be supplied and validated.

The API prototype uses Lambda handlers and an OpenAPI specification with `x-lambda-nickname` for discovery. It is not yet a persistent graph API or an automatically connected front end for the streaming pipeline. Shared envelope conventions are an integration goal to verify, not proof that both paths already interoperate.

## How Adage supports Karma

| Part | Responsibility |
| --- | --- |
| [Adage](https://github.com/usekarma/adage) | Infrastructure control model and architectural rationale. |
| [aws-config](https://github.com/usekarma/aws-config) | Desired instances and environment bindings. |
| [aws-iac](https://github.com/usekarma/aws-iac) | Reusable Terraform/Terragrunt implementations. |
| AWS SSM Parameter Store | Published configuration and runtime dependency metadata. |
| **Karma** | Workload, observations, experiments, and evidence about the model's results. |
| [agent-business-solution-template](https://github.com/usekarma/agent-business-solution-template) | Specification, deterministic verification, security/readiness evidence, and human release decisions. |

Adage's architecture predates the current agent use case. Its explicit state, reusable interfaces, and controlled execution make it a useful substrate for agent-assisted engineering. See [Adage's full story](https://github.com/usekarma/adage).

## Agent work and human authority

Agents can inspect source/history and AWS read-only, develop components, prepare configuration, run checks, generate plans, investigate cost/drift, and produce evidence and pull requests. Consequential AWS execution—including production apply, destroy, data deletion, sensitive IAM/security changes, and SSM publishing—requires explicit human authorization.

Agent safeguards are implemented in [aws-iac PR #1](https://github.com/usekarma/aws-iac/pull/1) and [aws-config PR #1](https://github.com/usekarma/aws-config/pull/1), currently under review. They are not Karma runtime capabilities and are not yet the infrastructure repositories' default-branch behavior.

## Queued strategic work

Faraday-visible queued directions are recorded under [`docs/queue/`](docs/queue/). Queue entries are planning signals, not execution authority.

- [`KARMA-AWS-ESTATE-001` — AWS estate monitoring](docs/queue/aws-estate-monitoring.md): read-only-first reconciliation of desired state, deployed state, operational state, security posture, and cost across authorized AWS accounts and deployments. It is queued, not active, and remains subject to the current `STOP_FOR_HUMAN` and single-active-task boundaries.

## First infrastructure proof

Compare **desired state vs. actual AWS state vs. actual cost**, explain discrepancies, and prepare safe remediation without destructive changes.

| Minimal site steady state | Exact expected target |
| --- | ---: |
| strall.com | $0.51/month |
| usekarma.dev | $0.61/month |
| **Combined** | **$1.12/month** |

These owner-specified targets are awaiting billing proof. They describe the intended minimal state for those two sites, not the full historical Karma stack or the additional Adage documentation site. The proof must establish scope, usage assumptions, shared charges, resource attribution, uncertainty, and data-loss risk. [Proof requirements](docs/adage-proving-ground.md#first-cost-proof) define success.

## Explore the source

For local service development, inspect `docker-compose.yml`, then start the services:

```bash
docker compose up -d
```

This starts supporting services only. Review [ClickHouse definitions](sinks/clickhouse/sql/) and the [normalizer's build/run instructions](normalizers/mongo-cdc-clickhouse-kstreams/README.md) before connecting a source and sink. Confirm topics, schemas, listener configuration, and query results rather than assuming the stack is wired end-to-end.

Streaming development requires Docker/Compose, Kafka, and ClickHouse; the Java normalizer documents JDK/Gradle requirements. API/deployment tools require Python, `boto3`, `PyYAML`, and properly configured AWS access. [Lambda publishing](scripts/deploy_lambda.md) and [OpenAPI publishing](scripts/deploy_openapi.md) change AWS and require separate authorization.

There is no root Poetry project or complete application test suite in this checkout. Start with the component-specific instructions and record what was actually verified.

## Deeper documentation

- [Adage proving ground, evidence, and next steps](docs/adage-proving-ground.md)
- [Website theory and design proposals](https://usekarma.dev/theory/)
- [Adage quickstarts and deployment documentation](https://github.com/usekarma/adage#getting-started)

## Offline personal stewards (review prototype)

[coordination/](coordination/) proposes a strict minimal work-item contract for
[Prudence #4](https://github.com/usekarma/karma/issues/4) and
[Aegis #5](https://github.com/usekarma/karma/issues/5). Only opaque workflow metadata
and synthetic check receipts are accepted. Financial/medical records and family
identities stay outside Karma. The existing active task and STOP_FOR_HUMAN are
preserved; no dispatch, runtime integration or infrastructure is enabled.
Run the isolated component quality gates and frozen demonstration before reviewing.
