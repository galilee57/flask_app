---
title: Documentation des APIs
summary: Référence des endpoints JSON de l'application
---

# Documentation des APIs

Cette page recense les endpoints JSON exposés par l'application Flask. Les URLs
ci-dessous sont relatives à l'adresse de l'application, par exemple
`http://localhost:5000` en développement.

Les réponses sont au format JSON sauf indication contraire. Les écritures qui
modifient des données partagées peuvent demander l'en-tête `X-Admin-Token` en
production. Le token est configuré côté serveur avec `ADMIN_API_TOKEN` et ne
doit jamais être placé dans le code frontend ou dans cette documentation.

## Vue d'ensemble

| Projet | Préfixe | Fonctionnalité |
| --- | --- | --- |
| Musculation | `/projects/musculation` | Exercices, programmes et analyse |
| Snake | `/projects/snake` | État du jeu, déplacements et statistiques |
| Todo list | `/projects/todolist` | Lecture et gestion de tâches |
| Game of Life | `/projects/game_of_life` | Grille, générations et motifs |
| Game of Life 3D | `/projects/game_of_life_3d` | État et configuration de la simulation |
| Puissance 4 | `/projects/connect_four` | Déplacement de l'IA |
| A* | `/projects/a_star` | Résolution d'un état |
| Viewer 360 | `/projects/viewer360` | Liste des images disponibles |
| Charts | `/projects/charts` | Stations, trains et diagramme de Marey |
| Pays | `/projects/countries` | Proxy de récupération des pays |

## Authentification

En production, les endpoints d'écriture administratifs utilisent :

```http
X-Admin-Token: <ADMIN_API_TOKEN>
```

Sans token valide, l'API retourne `403`. Si le token serveur n'est pas
configuré, elle retourne `503`. En développement, la vérification peut être
désactivée par la configuration de l'application.

## Musculation

### `GET /projects/musculation/api/exercices`

Retourne le catalogue des exercices contenu dans `exercices.json`.

### `GET /projects/musculation/api/reps_evaluation`

Retourne les coefficients d'analyse associés aux nombres de répétitions.

### `GET /projects/musculation/api/programmes`

Retourne les programmes, avec `id`, `name` et `exercices_count`.

### `POST /projects/musculation/api/programmes`

Crée un programme. Authentification administrateur possible selon la
configuration.

```json
{
  "name": "Séance force",
  "exercices": [
    {"exercice_id": "squat", "reps": 5, "weight": 100}
  ]
}
```

Réponse `201` : `{ "success": true, "programme_id": 1, "name": "Séance force" }`.
Le nom est limité à 100 caractères et la liste contient de 1 à 100 exercices.

### `GET /projects/musculation/api/programmes/<programme_id>`

Retourne le détail d'un programme et ses exercices.

### `PUT /projects/musculation/api/programmes/<programme_id>`

Remplace le nom et la liste des exercices. Le body reprend le format du POST.

### `DELETE /projects/musculation/api/programmes/<programme_id>`

Supprime un programme. Authentification administrateur possible selon la
configuration.

### `GET /projects/musculation/api/programmes/<programme_id>/analyse`

Calcule le volume et les scores force, hypertrophie et endurance, exercice par
exercice et pour l'ensemble du programme.

## Snake

Les paramètres `record=true` permettent d'enregistrer certaines statistiques.

| Méthode | Endpoint | Rôle |
| --- | --- | --- |
| GET | `/projects/snake/api/state` | État courant du jeu |
| POST | `/projects/snake/api/move/<direction>/<mode>` | Déplace le serpent; direction: `up`, `down`, `left`, `right` |
| POST | `/projects/snake/api/reset` | Réinitialise le jeu |
| GET | `/projects/snake/api/astar` | Retourne le chemin calculé vers le fruit |
| POST | `/projects/snake/api/ai/move` | Effectue un déplacement calculé par A* |
| GET | `/projects/snake/api/stats` | Retourne les statistiques enregistrées |
| GET | `/projects/snake/api/stats/curve` | Retourne les moyennes groupées pour les courbes |

## Todo list

| Méthode | Endpoint | Rôle |
| --- | --- | --- |
| GET | `/projects/todolist/api/todolist` | Liste les tâches |
| POST | `/projects/todolist/api/todolist` | Crée une tâche |
| PUT | `/projects/todolist/api/todolist/<task_id>` | Modifie `text` et/ou `done` |
| DELETE | `/projects/todolist/api/todolist/<task_id>` | Supprime une tâche |

Création : `{"text": "Préparer la documentation"}`. Le texte est obligatoire
et limité à 500 caractères. Les opérations d'écriture peuvent exiger
`X-Admin-Token`.

## Game of Life

| Méthode | Endpoint | Body ou rôle |
| --- | --- | --- |
| POST | `/projects/game_of_life/grid` | `{ "rows": 30, "cols": 60 }` |
| GET | `/projects/game_of_life/state` | État de la grille en session |
| GET | `/projects/game_of_life/next` | Calcule la génération suivante |
| POST | `/projects/game_of_life/reset` | Réinitialise la grille |
| POST | `/projects/game_of_life/toggle` | `{ "row": 2, "col": 4 }` |
| POST | `/projects/game_of_life/clear` | Vide la grille |
| POST | `/projects/game_of_life/save` | `{ "name": "glider" }` |
| POST | `/projects/game_of_life/load` | `{ "name": "glider" }` |
| GET | `/projects/game_of_life/saved` | Liste les motifs sauvegardés |
| POST | `/projects/game_of_life/pattern` | Applique un motif à une position |

## Game of Life 3D

`GET /projects/game_of_life_3d/state` retourne l'état. Les endpoints
`POST /projects/game_of_life_3d/next`, `/reset` et `/config` font avancer,
réinitialisent ou configurent la simulation.

## Autres projets

- `POST /projects/connect_four/api/ai-move` reçoit `grid`, `player` et
  éventuellement `type` (`easy`, `medium` ou `hard`), puis retourne la colonne
  choisie.
- `POST /projects/a_star/solve` reçoit un état dans `{"state": [...]}` et
  retourne `solvable`, `solution`, `moves` et `tree_nodes`.
- `GET /projects/viewer360/api/images` retourne `{ "items": [...] }` avec le
  nom et l'URL de chaque image autorisée.
- `GET /projects/countries/get_countries` récupère les données pays depuis
  l'API externe Rest Countries et les prépare pour l'interface.

## Charts

| Méthode | Endpoint | Rôle |
| --- | --- | --- |
| GET | `/projects/charts/api/stations` | Liste les stations |
| POST | `/projects/charts/api/stations` | Crée une station avec `name` et `km` |
| GET | `/projects/charts/api/trains` | Liste les trains; filtre optionnel `?date=YYYY-MM-DD` |
| POST | `/projects/charts/api/trains` | Crée un train |
| GET | `/projects/charts/api/marey` | Retourne les datasets du diagramme; filtre optionnel `?date=YYYY-MM-DD` |

Les écritures Charts peuvent exiger `X-Admin-Token`. Les dates acceptent
`YYYY-MM-DD`, `JJ/MM/AAAA` ou `JJ-MM-AAAA`; les heures acceptent `HH:MM` ou
`HH:MM:SS`.

## Exemple rapide

```bash
curl http://localhost:5000/projects/musculation/api/programmes
```

Pour mettre à jour une ressource protégée :

```bash
curl -X POST http://localhost:5000/projects/todolist/api/todolist \
  -H 'Content-Type: application/json' \
  -H 'X-Admin-Token: <ADMIN_API_TOKEN>' \
  -d '{"text":"Tester l API"}'
```

La route `/map`, disponible uniquement en mode debug, reste utile pour vérifier
la liste effective des routes enregistrées par Flask.
