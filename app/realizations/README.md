# Nouvelle section Projets — aperçu privé

Ce blueprint est indépendant de `app/experiences/`, qui conserve les anciennes pages et leurs routes. Son point d’entrée est `/realizations/`, accessible depuis le lien « Aperçu projets » du bandeau admin. Toutes ses routes, médias compris, exigent une session admin valide.

- `routes.py` : routes et contrôle d’accès.
- `content.py` : lecture des sources Markdown et préparation des sections.
- `templates/realizations/` : catalogue, études et composants.
- `static/` : médias et JavaScript de cette nouvelle version.

Conformément au socle commun du portfolio, les sources FR/EN restent sous `app/main/content/docs/realizations/`, les fiches d’information sous `app/main/content/docs/projects/realizations.*.md` et les styles Tailwind sous `app/main/styles/projects/realizations.css`, importés dans le bundle partagé. Consulter le README des sources pour les modifier.

Aucune bascule de l’entrée PRO n’est effectuée : elle reste liée aux anciennes pages jusqu’à la future intégration.
