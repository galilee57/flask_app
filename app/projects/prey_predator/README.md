# Prey and predators

Flask page: `/projects/prey_predator/?lang=fr` (or `en`). The simulation runs entirely in the browser. No database, external service or production write API is needed.

The template uses the shared `hero`, `info_modal` and `t(...)` helpers. The `pp-text` JSON block supplies translated dynamic strings to TypeScript. French and English information sheets live in `app/main/content/docs/projects/prey_predator.*.md`.

The original TypeScript simulation and its regression tests were imported from the user-provided `simulation_proie_predateur` project. Engine, animal drawing and chart logic are preserved. The interface uses the shared Tailwind build, scoped components in `app/main/styles/projects/prey_predator.css`, and mobile controls, including zoom buttons. Hiding the tab pauses playback.

## Development

In this directory, run `npm install`, then `npm run build` after changing `src/`. Commit the generated `static/js/prey_predator.js`; Flask does not require Node at runtime. Run `npm test` for deterministic engine, shelter, sprite and chart regression checks. Run `pytest tests/test_prey_predator.py -q` from the repository root for Flask integration checks.
