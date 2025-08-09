# Mongo CDC → Kafka → ClickHouse Normalizer (Kafka Streams)

A minimal Kafka Streams app that normalizes MongoDB Atlas Change Stream events into the Karma event envelope and writes them to `events.normalized`.
Use Kafka Connect (or CH Kafka Engine) for source/sink; this app focuses solely on normalization.

## Topology
`cdc.raw` (JSON) → **Normalizer (KStreams)** → `events.normalized` (JSON)

## Build & Run (local)
Prereqs: JDK 17+, Gradle 7.6+

```bash
cd karma/normalizers/mongo-cdc-clickhouse-kstreams
gradle run   -Dorg.gradle.jvmargs="-Xms256m -Xmx512m"   --args=""
```

Required env vars:
```bash
export KAFKA_BOOTSTRAP=localhost:9092
export INPUT_TOPIC=cdc.raw
export OUTPUT_TOPIC=events.normalized
export MAPPING_PATH=/absolute/path/to/mapping.yml   # optional; falls back to classpath
# Optional:
# export APPLICATION_ID=karma-normalizer
```

## Packaging
```bash
gradle build
# Runnable via: gradle run
```

## Configure
Edit `src/main/resources/mapping.yml` or point `MAPPING_PATH` to your own YAML.
The YAML allows per-collection tag extraction and simple computed attributes.

## Notes
- Processing guarantee is set to **exactly_once_v2**.
- SerDes are String→String; payloads are JSON strings in/out.
- For production, consider Avro/Protobuf + Schema Registry and stronger input validation.
