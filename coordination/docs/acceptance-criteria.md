# Acceptance and engineering gates

specs/work-request.md contains AC-001..AC-006; specs/acceptance.json maps them to tests.
Retain all template v2 gates, including strict types, 90% branch coverage, credential
scan, Bandit and live hash-locked dependency audit. Production readiness is separate.
Cross-repository implementations and schemas must match the recorded hash manifests.
