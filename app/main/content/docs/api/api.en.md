---
title: API Documentation
summary: Reference for the application's JSON endpoints
---

# API Documentation

This page lists the JSON endpoints exposed by the Flask application. URLs are
relative to the application address, such as `http://localhost:5000` in
development.

Responses use JSON unless stated otherwise. Writes that change shared data may
require the `X-Admin-Token` header in production. The token is configured on
the server with `ADMIN_API_TOKEN` and must never be placed in frontend code or
in this documentation.

## Authentication

In production, administrative write endpoints use:

```http
X-Admin-Token: <ADMIN_API_TOKEN>
```

An invalid token returns `403`; a missing server-side token returns `503`.
Development configuration may disable this check.

## Endpoints

### Musculation

- `GET /projects/musculation/api/exercices` returns the exercise catalogue.
- `GET /projects/musculation/api/reps_evaluation` returns repetition analysis coefficients.
- `GET /projects/musculation/api/programmes` lists programmes.
- `POST /projects/musculation/api/programmes` creates a programme from:
  `{"name":"Strength session","exercices":[{"exercice_id":"squat","reps":5,"weight":100}]}`.
- `GET /projects/musculation/api/programmes/<programme_id>` returns programme details.
- `PUT /projects/musculation/api/programmes/<programme_id>` replaces the name and exercises.
- `DELETE /projects/musculation/api/programmes/<programme_id>` deletes a programme.
- `GET /projects/musculation/api/programmes/<programme_id>/analyse` calculates volume and strength, hypertrophy and endurance scores.

### Snake

- `GET /projects/snake/api/state` returns the current game state.
- `POST /projects/snake/api/move/<direction>/<mode>` moves the snake. Directions are `up`, `down`, `left` and `right`.
- `POST /projects/snake/api/reset` resets the game.
- `GET /projects/snake/api/astar` returns the path to the fruit.
- `POST /projects/snake/api/ai/move` performs an A* move.
- `GET /projects/snake/api/stats` returns recorded statistics.
- `GET /projects/snake/api/stats/curve` returns grouped averages for charts.

Add `?record=true` to relevant Snake calls to record statistics.

### Todo list

- `GET /projects/todolist/api/todolist` lists tasks.
- `POST /projects/todolist/api/todolist` creates a task from `{"text":"..."}`.
- `PUT /projects/todolist/api/todolist/<task_id>` updates `text` and/or `done`.
- `DELETE /projects/todolist/api/todolist/<task_id>` deletes a task.

The text field is required for creation and limited to 500 characters. Writes
may require `X-Admin-Token`.

### Game of Life

- `POST /projects/game_of_life/grid` accepts `{"rows":30,"cols":60}`.
- `GET /projects/game_of_life/state` returns the session grid.
- `GET /projects/game_of_life/next` computes the next generation.
- `POST /projects/game_of_life/reset` resets the grid.
- `POST /projects/game_of_life/toggle` accepts `{"row":2,"col":4}`.
- `POST /projects/game_of_life/clear` clears the grid.
- `POST /projects/game_of_life/save` and `POST /projects/game_of_life/load` use `{"name":"glider"}`.
- `GET /projects/game_of_life/saved` lists saved patterns.
- `POST /projects/game_of_life/pattern` applies a pattern.

### Other projects

- `POST /projects/connect_four/api/ai-move` accepts `grid`, `player` and optional `type` (`easy`, `medium` or `hard`), then returns the selected column.
- `POST /projects/a_star/solve` accepts `{"state":[...]}` and returns `solvable`, `solution`, `moves` and `tree_nodes`.
- `GET /projects/viewer360/api/images` returns `{ "items": [...] }` with allowed image URLs.
- `GET /projects/countries/get_countries` fetches and prepares country data from the external Rest Countries API.

### Charts

- `GET /projects/charts/api/stations` lists stations.
- `POST /projects/charts/api/stations` creates a station from `name` and `km`.
- `GET /projects/charts/api/trains` lists trains and accepts `?date=YYYY-MM-DD`.
- `POST /projects/charts/api/trains` creates a train.
- `GET /projects/charts/api/marey` returns Marey chart datasets and accepts `?date=YYYY-MM-DD`.

Charts writes may require `X-Admin-Token`. Dates accept ISO, French slash or
hyphen formats; times accept `HH:MM` or `HH:MM:SS`.

## Quick example

```bash
curl http://localhost:5000/projects/musculation/api/programmes
```

The `/map` route, available only in debug mode, can be used to inspect the
routes actually registered by Flask.
