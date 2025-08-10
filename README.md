# Karma

Karma is an event-driven infrastructure intelligence system.  
It can operate in two complementary modes:

1. **Streaming Mode** — real-time event processing, anomaly detection, and automated actions using Kafka, ClickHouse, and pluggable data sources.  
2. **API Mode** — queryable event graph API powered by AWS Lambda and API Gateway, with configuration and deployment resolved via AWS Parameter Store.

---

## Streaming Mode (Reference Pipeline)

The streaming pipeline ingests events from sources like MongoDB Atlas via MSK Connect, normalizes them, stores them in ClickHouse for analysis, detects deviations, and triggers automated actions.

**Flow:**
1. **Normalizer (Kafka Streams)**  
   - Consumes raw CDC events  
   - Produces standardized envelopes to `events.normalized`

2. **ClickHouse Sink**  
   - Stores normalized events in `karma.events_raw`  
   - Maintains materialized views for metrics and state tracking

3. **Entropy MVP**  
   - Calculates baselines and entropy scores  
   - Flags deviations as `entropy.deviation` events

4. **Actions**  
   - Consumes actionable events  
   - Emits `action.requested`, `action.progress`, `action.result` to Kafka

**Local Quickstart:**
```bash
docker compose up -d
# Produce sample normalized events
curl -s 'http://localhost:8123/?query=SELECT%20count()%20FROM%20karma.events_raw'
```

---

## API Mode (Graph API over Events)

The API mode allows interactive querying of infrastructure events as a graph, enabling exploration, relationship mapping, and human-in-the-loop decision-making.

**Flow:**
1. **Log Handler Lambda** — accepts structured events via API Gateway.  
2. **Graph Query Lambda** — queries stored events as a graph.  
3. **OpenAPI Spec** — declares Lambda handlers using `x-lambda-nickname` for dynamic resolution.

**Directory Structure:**
```
karma/
├── openapi/
│   └── karma-api/
│       └── openapi.yaml
├── lambdas/
│   ├── karma-log-handler/
│   └── karma-graph-query/
└── scripts/
    ├── deploy_lambda.py
    └── deploy_openapi.py
```

---

## How the Modes Work Together

- **Streaming Mode** can power the analytics and anomaly detection backend.  
- **API Mode** can expose those analytics (and the underlying event graph) for queries, dashboards, or integrations.  
- Both share the same **event envelope** and tagging conventions, so events can flow between them seamlessly.

---

## Requirements

**For Streaming Mode:**
- Docker + Docker Compose for local development  
- Kafka (MSK or local)  
- ClickHouse (local or managed)

**For API Mode:**
- Python 3.10+  
- AWS CLI credentials configured via `AWS_PROFILE`  
- `boto3`, `PyYAML`
