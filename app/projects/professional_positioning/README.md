# Professional positioning

Private workspace: `/projects/professional_positioning/`, accessible after `/admin` login.
Apply the migration with `flask --app wsgi db upgrade` before using it. No source data is seeded.

Create a diagnostic, choose the target role and describe the selection context. Add one portfolio and public references, then document each criterion with a factual finding, exact excerpt, HTTP(S) URL, consultation timestamp and justified confidence. The date input uses the browser's local timezone and sends UTC. An administrator manually confirms each verification; edits reset verification. No external URLs are fetched. Missing evidence remains undocumented.

All private endpoints require an active admin session, including development and API calls. Production mutations additionally require `X-Admin-Token`. The UI keeps the token in the current page only. It must be entered again after navigation; never put credentials in the URL.

Snapshots count distinct reference records with a verified assessment for each criterion. They measure evidence coverage, not skill, relative seniority or market position. Groups smaller than five are suppressed without a denominator. The threshold is a disclosure rule, not a guarantee of anonymity: review duplicate identities and recognition risk before publishing. Selection bias and self-reported evidence remain limitations. The user reviews a frozen private preview before explicit publication at `/positioning/<snapshot_id>`. The original diagnostic stays private regardless of publication.

Snapshots contain a private frozen provenance record to preserve auditability when source assessments change. This is available only under `/projects/professional_positioning/api/snapshots/<snapshot_id>/provenance`. Public rendering uses only allowlisted aggregates. The preview includes a publication withdrawal control; withdrawn snapshots return 404 publicly. Responses are not cached. Published copies already saved by readers cannot be recalled.

Version 1 uses one current evidence-backed assessment per profile and criterion. Saving replaces it; published snapshots preserve their source record. Public counts never include the personal portfolio. A richer narrative positioning graphic requires editorial analysis beyond these counts.

Tests: `.venv/bin/pytest tests/test_professional_positioning.py -q`.
Styles: `npm run build:css`.

## Sourced analyses and working memory (v2)

The project entry now opens the latest private dashboard when analyses exist. The original manual editor remains at `/projects/professional_positioning/manual`. Codex appends sourced analysis runs through `positioning-import`; `positioning-context` exports all revisions and memory to a private instance file. Each profile review includes an original URL, consulted pages and dated excerpts; observation frequencies are computed from the actual corpus. Runs are independent of the legacy manual assessments and are never automatically published.

The dashboard preserves historical findings, records comments and supplied evidence, and tracks action status with audit events. Supplied evidence stays pending review; a new run lists the memory entries actually examined. See [skills.md](skills.md), [schema.md](schema.md), [tools.md](tools.md), and the reusable [portfolio-diagnostic skill](skills/portfolio-diagnostic/SKILL.md).
