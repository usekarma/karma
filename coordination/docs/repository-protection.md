# Karma main protection proposal — not applied

Observed: Karma is public, default main, current caller has repository administration
permission. main protection read returned HTTP 404 Branch not protected; repository
rulesets and effective main rules both returned empty lists. Unlike the two private
steward repositories, public Karma can use branch protection under the current plan.
No settings were changed. Reinspect inherited rules immediately before any approved write.

Proposed payload: docs/main-protection.proposed.json for usekarma/karma main only.
Require Steward coordination quality gates from GitHub Actions, strict/up-to-date
checks, one independent approving review, stale approval dismissal, most-recent-push
approval, resolved conversations, administrator enforcement, linear history, no force
push or deletion. Check scope is the isolated new component, not all legacy runtimes.
Eligible human reviewers and ownership still require assignment; no bypass is proposed.

Applying requires separate explicit approval for this concrete operation and payload,
repository Administration: write (or classic repo-scoped administrator credentials),
and confirmation of the observed check/app identity. Preserve any stricter rules
introduced in the meantime. No billing change or repository visibility change is needed
for Karma; usekarma organization Team/Enterprise entitlement is needed to enforce the
private Prudence/Aegis rules. Do not publish private repositories as a workaround.
STOP_FOR_HUMAN.
