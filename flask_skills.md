# 🧭 SKILLS ABOUT FLASK

## 🟢 Level 1 — Beginner

_(Goal : publish a simple, stable and readable Flask app)_

| ✅  | Skills                                                                           | Projects |
| --- | -------------------------------------------------------------------------------- | -------- |
| ✅  | Installer Flask et lancer une app avec `flask run`                               |
| ✅  | Comprendre la structure minimale d’une app (`app.py`, routes, templates, static) |
| ✅  | Créer des routes avec `@app.route` et gérer les méthodes GET/POST                |
| ✅  | Récupérer des paramètres (`request.args`, `request.form`, `request.json`)        |
| ✅  | Renvoyer une réponse JSON (`jsonify`) ou HTML (`render_template`)                |
| ✅  | Utiliser Jinja2 : boucles, conditions, héritage de template                      |
| ✅  | Servir des fichiers statiques (CSS, images, JS)                                  |
| ✅  | Configurer `app.config` et utiliser un fichier `.env`                            |
| ☑️  | Créer un premier CRUD avec SQLite et SQLAlchemy                                  |
| ☑️  | Gérer les erreurs 404/500 avec des templates dédiés                              |
| ☑️  | Utiliser les logs (`app.logger`)                                                 |
| ☑️  | Écrire un premier test unitaire Flask (client de test intégré)                   |

---

## 🟡 Niveau 2 — Intermédiaire : architecture & API

_(objectif : structurer l’app et la rendre réutilisable)_

| ✅  | Compétence                                                               | Projects |
| --- | ------------------------------------------------------------------------ | -------- |
| ✅  | Mettre en place une Application Factory (`create_app()`)                 |
| ✅  | Organiser le code avec des Blueprints                                    |
| ☐   | Gérer la configuration par environnement (dev, test, prod)               |
| ☐   | Utiliser SQLAlchemy avec des relations et des requêtes complexes         |
| ☐   | Mettre en place des migrations avec Alembic / Flask-Migrate              |
| ☐   | Gérer l’authentification avec Flask-Login (session)                      |
| ☐   | Sécuriser les formulaires avec CSRF (Flask-WTF)                          |
| ☐   | Créer une API REST propre (JSON, statuts HTTP, `/api/v1`)                |
| ☐   | Documenter l’API avec Swagger / OpenAPI (Flask-Smorest, apispec, etc.)   |
| ☐   | Valider les entrées avec Marshmallow ou Pydantic                         |
| ☐   | Ajouter un cache simple (Flask-Caching)                                  |
| ☐   | Lancer des tâches en arrière-plan (Celery, RQ, Thread)                   |
| ☐   | Configurer une app Flask dans Docker (Gunicorn + Nginx)                  |
| ☐   | Gérer les variables sensibles via `.env` (dotenv / secrets)              |
| ☐   | Mettre en place des tests d’intégration et mocks (pytest + client Flask) |

---

## 🔵 Niveau 3 — Avancé : production & scalabilité

_(objectif : une API robuste, testée et déployée en production)_

| ✅  | Skills                                                                    | Projects |
| --- | ------------------------------------------------------------------------- | -------- |
| ☐   | Comprendre les contextes d’application et de requête (`current_app`, `g`) |
| ☐   | Ajouter des hooks (`before_request`, `after_request`, `teardown_request`) |
| ☐   | Gérer les transactions SQL et les rollbacks atomiques                     |
| ☐   | Structurer le code par modules “domain / service / repository”            |
| ☐   | Gérer la sécurité avancée : JWT, RBAC, CORS, headers de sécurité          |
| ☐   | Implémenter la pagination, la recherche et les filtres d’API              |
| ☐   | Surveiller l’application avec Prometheus / OpenTelemetry                  |
| ☐   | Ajouter des endpoints `/healthz`, `/metrics` et `/readyz`                 |
| ☐   | Implémenter un logging structuré (JSON) pour la prod                      |
| ☐   | Déployer avec Docker Compose, Gunicorn et Nginx                           |
| ☐   | Configurer un worker Celery (Redis, Kafka, ou RabbitMQ)                   |
| ☐   | Gérer les erreurs uniformes (`errorhandler`)                              |
| ☐   | Écrire des tests e2e (end-to-end) complets                                |
| ☐   | Intégrer un pipeline CI/CD (GitHub Actions, GitLab CI, etc.)              |

---

## 🔴 Niveau 4 — Expert confirmé : architecture & observabilité

_(objectif : app distribuée, résiliente et conforme aux bonnes pratiques de prod)_

| ✅  | Skills                                                                      | Projects |
| --- | --------------------------------------------------------------------------- | -------- |
| ☐   | Créer une architecture “clean” (hexagonale, DDD léger)                      |
| ☐   | Gérer la configuration avec Pydantic Settings ou dynaconf                   |
| ☐   | Utiliser Flask 3 avec des vues `async` (Uvicorn / Hypercorn)                |
| ☐   | Implémenter WebSockets ou SSE pour temps réel                               |
| ☐   | Publier/consommer des messages Kafka depuis Flask                           |
| ☐   | Gérer la charge : rate limiting distribué, cache Redis                      |
| ☐   | Ajouter une authentification OAuth2 / OIDC (Authlib, Keycloak, Azure AD)    |
| ☐   | Monitorer logs, métriques et traces corrélées                               |
| ☐   | Mettre en place du blue-green deployment                                    |
| ☐   | Implémenter une API versionnée stable (contrats OpenAPI)                    |
| ☐   | Tester la montée en charge (Locust / k6)                                    |
| ☐   | Sécuriser la gestion des secrets (Vault, AWS Secrets Manager)               |
| ☐   | Ajouter la gestion RGPD : anonymisation, purge, consentement                |
| ☐   | Intégrer des dashboards d’observabilité (Grafana, Loki, Tempo)              |
| ☐   | Mettre en place un système de feature flags (Flask-Toggles ou LaunchDarkly) |

---

## 🧠 Compétences transverses utiles

| ✅  | Skills                                                            | Projects                        |
| --- | ----------------------------------------------------------------- | ------------------------------- |
| ☐   | Comprendre HTTP, REST, statuts et idempotence                     |
| ☐   | Savoir profiler et optimiser les performances (CPU, mémoire, SQL) |
| ☐   | Utiliser Docker, docker-compose, et gérer un stack complet        |
| 🔶  | Maîtriser Git et GitHub Actions pour CI/CD                        | ToDo Tree to manage improvments |
| ☐   | Documenter et versionner ses API (OpenAPI, changelog)             |
| ☐   | Gérer un environnement multi-services : Flask + Kafka + Airflow   |
| ☐   | Développer des extensions Flask personnalisées                    |
