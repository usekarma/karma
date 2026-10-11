# Offline coordination operating procedure

Use synthetic fixtures only. Run make check and make test in coordination/.
Provide the already-existing global active-work identity; do not infer or replace it
from this new queue. A conflicting claim rejects, never activates another item.

Review safe evidence check receipts and their byte digests independently. Treat
metadata permission and approval objects as fixture claims, not authenticated grants.
Preserve UNKNOWN and failed attempts; do not rewrite an old receipt to force PASS.
A revoked/expired disclosure permission blocks inspection; new calls recheck it.
No webhook, upload, agent runner, cloud command or external system is available.

Human must explicitly approve exact PR revisions before merge. Protection proposals
are files for review, not applied settings. Future integrations need scoped authority,
security design, retention/deletion, authenticated audit and operational recovery.
STOP_FOR_HUMAN.
