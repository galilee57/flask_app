# Schéma du diagnostic et de sa mémoire

Les données utilisent l’extension SQLAlchemy et la même base PostgreSQL que le portfolio. Les migrations créent seulement le schéma, jamais un corpus réel.

## Modèles

- `positioning_diagnostics` : dossier privé et rôle cible.
- `positioning_profiles` : identité locale d’une personne, URL d’origine et type portfolio/référence. Réutilisée entre analyses d’un dossier.
- `positioning_analysis_runs` : analyse complète immuable, parent, clé d’import unique, hash du contenu, auteur, référentiel bilingue, synthèse, limites, identifiants des apports mémoire examinés et date UTC.
- `positioning_portfolio_reviews` : un profil par run, URL d’origine, rôle affiché, comparabilité `target/exact/adjacent`, périmètre et sources JSON figées.
- `positioning_review_observations` : un critère par review, état documentaire, constat FR/EN, confiance, justification FR/EN et clés des sources de cette review.
- `positioning_memory_entries` : commentaires et preuves utilisateur ajoutés sans écrasement, auteur, critère/run éventuel et date ; événements de changement des actions.
- `positioning_work_items` : actions courantes, priorité et statut. Les changements de statut sont journalisés dans la mémoire.
- `positioning_assessments` / `positioning_snapshots` : éditeur manuel historique et instantanés de publication v1. Les runs v2 ne sont pas projetés automatiquement dans cet éditeur ni publiés. Leur analyse reste dans le dashboard.

## Contrat d’import JSON, `schema_version: 2`

Champs racine obligatoires :

- `import_key` : nouvelle clé à chaque analyse ; même clé et même contenu = import idempotent, même clé et contenu différent = refus.
- `actor`, `title`, `context` : auteur et contexte du dossier.
- `rubric` : liste de `{key, label: {fr,en}, definition: {fr,en}}`, clés uniques.
- `summary`, `limitations` : listes non vides de textes `{fr,en}`.
- `reviews` : exactement un portfolio et une ou plusieurs références, URL d’origine uniques.
- `memory_entry_ids` : liste optionnelle des apports effectivement examinés, appartenant au même dossier.
- `actions` : liste optionnelle `{criterion,title,body,priority}` pour amorcer le premier run seulement ; un amendement préserve les actions courantes.

Chaque review :

```json
{
  "name": "Nom privé",
  "kind": "reference",
  "origin_url": "https://example.org/",
  "role_label": "Intitulé effectivement lu",
  "comparability": "exact",
  "scope": "Pages consultées, projets et limites",
  "sources": [{
    "key": "s1",
    "url": "https://example.org/projects",
    "excerpt": "Court extrait exact",
    "consulted_at": "2026-01-01T10:00:00Z",
    "method": "browser_dom",
    "kind": "self_report"
  }],
  "observations": [{
    "criterion": "cle_du_referentiel",
    "status": "claimed",
    "finding": {"fr": "Constat limité à la preuve.", "en": "Finding limited to the evidence."},
    "confidence": "medium",
    "confidence_reason": {"fr": "Justification.", "en": "Rationale."},
    "source_keys": ["s1"]
  }]
}
```

Cet extrait décrit la forme d’une review ; un import complet exige une observation pour **chaque** critère de la grille et les champs racine.

États : `claimed` = décrit par l’auteur ; `demonstrated` = artefact effectivement inspecté ; `not_documented` = aucune preuve explicite retenue dans le périmètre ; `not_assessable` = consultation insuffisante. Tout état a au moins une source de périmètre. Un positif exige une preuve autre que `scope` ; `demonstrated` exige `artifact`. Cela valide la structure, pas la vérité de l’interprétation : l’agent doit vérifier le contenu.

Méthodes : `web_open` (peut refléter un index), `browser_dom` (navigateur rendu), `local_render` (rendu Flask visiteur), `repository` (code inspecté, ne prouve pas sa visibilité publique). Nature : `self_report`, `artifact`, `scope`. Confiance : `low/medium/high`, toujours justifiée. Dates avec fuseau et non futures. URL HTTP(S) sans identifiants. Les sources ne sont pas récupérées automatiquement par l’import.

Les fréquences comptent uniquement `claimed` et `demonstrated` une fois par référence ; les effectifs non évaluables sont affichés séparément. Aucun score ni percentile. Les modifications de corpus changent la base de comparaison et doivent être expliquées, jamais interprétées automatiquement comme une progression personnelle.
