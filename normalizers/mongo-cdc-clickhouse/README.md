# Mongo CDC → Kafka → ClickHouse Normalizer

This module ingests raw CDC events (e.g., from MongoDB Atlas) from Kafka,
maps them to the Karma event envelope, and emits them to `events.normalized`.
ClickHouse stores the canonical event ledger and materialized views for
querying current state, baselines, and edges.

## Goals
- Generic, config-driven normalization via mapping DSL.
- Stateless processing: Kafka in → Kafka out.
- First-class ClickHouse sink (events_raw + MVs).

## Status
Scaffolding only — implementation to follow.
