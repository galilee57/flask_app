# Déploiements Docker

La préparation Azure ACR / Container Apps, Vercel et Docker Compose est documentée
[dans infra/README.md](infra/README.md). Les fichiers Docker n'incluent aucune donnée
locale ni secret. Appliquer la nouvelle migration avant de redémarrer un hébergement
existant ; importer explicitement les anciens JSON avec `storage-import`.

# Environnement de développement local

Depuis le répertoire du projet (Python 3.14 testé) :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock -r requirements-dev.txt
python -m pip check
python -m pytest -q
```

Un environnement virtuel doit être recréé après un changement de Mac ou de
chemin du projet ; il ne suffit pas de restaurer son dossier depuis iCloud.

La couverture, l'isolation et les commandes détaillées des tests sont documentées
dans [tests/README.md](tests/README.md).

## Tailwind CSS

Installer Node.js et npm sur macOS avec `brew install node`, puis :

```bash
npm ci
npm run build:css
```

Pendant les modifications de styles, lancer `npm run watch:css` dans un second
terminal pour recompiler automatiquement le CSS.

## Lancement du portfolio

L'application charge `.env` à la racine du projet. Sur Mac, utiliser
`FLASK_CONFIG=development` et une base PostgreSQL locale :
`DATABASE_URL=postgresql+psycopg://flask_app:MOT_DE_PASSE_LOCAL@127.0.0.1:5432/flask_app`.
Encoder les caractères réservés du mot de passe dans l'URI. Installer et démarrer
PostgreSQL 15 avec `brew install postgresql@15` puis
`brew services start postgresql@15`. La base locale et son rôle `flask_app`
doivent être créés avant les migrations. Les tests conservent leur base SQLite isolée.

```bash
source .venv/bin/activate
FLASK_CONFIG=development flask --app wsgi --debug run
```

Ouvrir http://127.0.0.1:5000. Pour une base locale neuve, appliquer les migrations
avec `FLASK_CONFIG=development flask --app wsgi db upgrade` avant le lancement.

# Déploiement PythonAnywhere

PythonAnywhere utilise ici Python 3.10 : installer `requirements-python310.lock`.
Le fichier `requirements.lock` est réservé à Python 3.14 (Mac et Docker).
Conserver le virtualenv PythonAnywhere existant ; le workflow teste désormais Python 3.10.

## Staging (GitHub Actions)

Seule la branche `staging` est déployée automatiquement sur
`staging-Galilee57.pythonanywhere.com`. La branche `main` et l'application
`Galilee57.pythonanywhere.com` ne sont jamais visées par ce workflow.

Les secrets de l'environnement GitHub `staging` requis sont :

```text
PA_USERNAME
PA_API_TOKEN
PA_STAGING_DOMAIN
PA_SSH_PRIVATE_KEY
```

`PA_SSH_PRIVATE_KEY` correspond à une clé de déploiement dédiée. Sa clé publique
doit être ajoutée dans `~/.ssh/authorized_keys` du compte PythonAnywhere. Le
workflow lit ensuite le répertoire source et le virtualenv de l'application de
staging via l'API, met à jour le checkout `staging`, applique les migrations,
puis demande le rechargement de cette seule web app.

Créer le fichier `.env` dans le répertoire source de staging sur PythonAnywhere
avant le premier déploiement, avec `FLASK_CONFIG=production`, `SECRET_KEY`
(la clé propre à staging), `ADMIN_API_TOKEN` et `DATABASE_URL`.
Le workflow conserve ce fichier, limite ses permissions à `600` et vérifie les
variables requises avant les migrations, sans afficher leurs valeurs.
Le secret GitHub `STAGING_SECRET_KEY` n'est plus utilisé.

La configuration de production est pilotée par les variables d'environnement, jamais par
des valeurs commitées :

```bash
export FLASK_CONFIG=production
export SECRET_KEY='une-cle-aleatoire-longue-et-privee'
export ADMIN_API_TOKEN='un-jeton-prive-pour-les-ecritures-admin'
export DATABASE_URL='postgresql+psycopg://flask_app:MOT_DE_PASSE_PA@Galilee57-5457.postgres.pythonanywhere-services.com:15457/flask_app'
```

Dans le fichier WSGI PythonAnywhere, définir `FLASK_CONFIG=production` avant
`create_app()`. À chaque déploiement :

Le `.env` distant contient la connexion PythonAnywhere et la clé de session propre
à l'environnement ; ne pas le remplacer par celui du Mac. Le workflow staging
applique les migrations puis vérifie `/health/ready`, qui contrôle l'accès à la base.
Les migrations créent les tables ; elles ne transfèrent pas les données SQLite
existantes. Conserver les anciennes bases pour un éventuel import séparé.

Pour récupérer une ancienne base SQLite, sauvegarder PostgreSQL puis utiliser :

```bash
flask --app wsgi sqlite-import --source /chemin/database.db --dry-run
flask --app wsgi sqlite-import --source /chemin/database.db
```

L'import conserve les identifiants, les références et le fichier source. Il ignore
les lignes identiques et annule toutes les insertions en cas de conflit ou de
contrainte invalide. Les séquences PostgreSQL sont ajustées pour les futures
insertions. La table de version Alembic et les sessions ne sont pas transférées.
Exécuter la même commande sur PythonAnywhere avec sa propre configuration `.env`
et une copie privée du fichier SQLite, après les migrations.

```bash
git pull
pip install -r requirements-python310.lock
flask --app wsgi db upgrade
```

Les API qui modifient les données partagées requièrent, en production, l'en-tête HTTP
`X-Admin-Token`. Les routes `/debug`, `/map` et `/files-map` retournent désormais 404.
Les tâches Todo sont enregistrées dans la table PostgreSQL `todo`.
Ne pas définir `TODOLIST_DATA_PATH` dans `.env` pour ce stockage SQL.
Pour reprendre les anciennes tâches, lancer une fois
`flask --app wsgi storage-import --todos app/projects/todolist/static/data/todolist.json`.
Le fichier JSON source est conservé et n'est plus modifié par les actions de l'API.

# Console pythonAnyWhere (utiliser celle à partir de l'env dans Web Menu)

git pull
puis valider par :wq
Reload App (menu Web)

# Lancement de npx pour compilation de tailwind avec watch

npx @tailwindcss/cli \
 -i ./input.css \
 -o ./app/main/static/css/output.css \
 --watch

# Structure de l'application

```text
app/
├── __init__.py       # Fabrique Flask : create_app
├── core/             # Configuration, initialisation, blueprints, admin, sécurité, i18n
├── storage/          # Modèles partagés et commandes d'import des données
├── extensions/       # Instances db/migrate et extensions de contenu
├── main/             # Portfolio, contenu bilingue, templates et assets
├── experiences/      # Pages des expériences
├── projects/         # Un blueprint par projet
└── static/           # Assets communs
```

Chaque blueprint conserve ses routes, templates et fichiers statiques dans son
propre dossier. Les projets sont enregistrés dans `app/core/blueprints.py`,
généralement sous `/projects/<project_name>`. Leurs modèles métier restent auprès
du projet ; les modèles de stockage partagés sont dans `app/storage/runtime_models.py`.

Les paramètres sont définis dans `app/core/config.py`. Les points d'entrée
`run.py` et `wsgi.py` utilisent toujours `from app import create_app`.
Les instances SQLAlchemy et Flask-Migrate sont définies uniquement dans
`app/extensions/__init__.py` et s'importent depuis `app.extensions`.

# API documentation

The bilingual API reference is available in:

- `app/main/content/docs/api/api.fr.md`
- `app/main/content/docs/api/api.en.md`

# Configuration WSGI

Utiliser `FLASK_CONFIG=production` avant de charger `wsgi:app` et fournir les variables
privées documentées ci-dessus. `APP_ENV` n'est plus utilisé.

# Link the environement nenv (in web page) :

/home/Galilee57/.virtualenvs/nenv

# NOTE : example of portfolios

https://www.codewonders.dev
https://dunks1980.com
https://mattfarley.ca/
https://www.rammaheshwari.com/#about

https://lottiefiles.com/free-animations/gaming

Retrogaming : incarner un personnage qui nqvigue dqns un monde varié. Bien les placer pour assurer une coherence et eviter que les visiteurs ne se perdent. Phaser Game Engine.

# TODO : utilisation de Taipy pour montrer des tableaux de bord

# TODO : Ideas for future projects

- Reinforcement AI
- Jeu du Taquin : exploration d'un arbre / notion d'heuristique
- Simulation Modèle Prédateur - proie / isometrique
- Simulation d'une contagion / isometrique
- Machine de Turing
- Pacman
- Configurateur 3D : https://sketchfab.com/3d-models/
- Admin, healthy


## Instance publique et brouillons privés

Le catalogue `app/main/static/data/cartes.json` utilise `published: true` pour
les projets publics. Les projets avec `published: false` (ou sans statut) sont
réservés à l’admin : pages, API, fichiers du projet et image de carte dédiée.
Le catalogue JSON statique complet est privé ; utiliser `/data/cartes` pour
obtenir la liste adaptée au visiteur. Tout nouveau projet doit avoir une carte.

Configurer `ADMIN_USERNAME` (identifiant, `admin` par défaut) et
`ADMIN_PASSWORD_HASH` dans l’environnement de l’instance publique.
Générer le hash localement sans écrire le mot de passe dans l’historique :

```sh
.venv/bin/python -c 'from getpass import getpass; from werkzeug.security import generate_password_hash; print(generate_password_hash(getpass("Mot de passe admin : ")))'
```

Cliquer sur le logo dans la navigation, puis saisir
l’identifiant et le mot de passe sur `/admin` pour ouvrir une session de
prévisualisation d’une heure. Une fois connecté, le logo ouvre le LAB et la déconnexion reste accessible
dans le bandeau admin.
Le LAB affiche alors aussi les brouillons ; la déconnexion ferme cet accès.
La session admin ne remplace pas `X-Admin-Token` pour les écritures persistantes.
Pour publier, modifier `published` dans le catalogue et déployer la modification
par le workflow `staging` documenté. Il n’y a pas de bouton de publication dans
cette première version et aucune migration de base de données n’est nécessaire.

Pour les tests techniques locaux :

```sh
FLASK_CONFIG=development .venv/bin/flask --app wsgi --debug run
.venv/bin/python -m pytest -q
```

Les brouillons nécessitent une connexion admin, y compris en développement local.
Utiliser une base locale distincte, jamais la base de l’instance publique.
Les fichiers placés dans les ressources statiques communes restent publics ;
placer les ressources privées sous le répertoire statique du projet concerné.
La configuration des instances hébergées n’est pas modifiée par cette évolution.
Avant de retirer la seconde instance, valider cet accès sur staging puis préparer
la bascule de l’instance publique via le workflow documenté.

## Promotion manuelle vers PythonAnywhere principal

Le workflow `promote-production.yml` est uniquement déclenché manuellement depuis
`main`. Il réutilise les accès PythonAnywhere de l'environnement GitHub `staging`.
Par défaut, `inspect_only=true` compare les configurations sans afficher de secrets.
Pour une promotion explicitement validée, `inspect_only=false` installe le commit
`RELEASE_SHA` épinglé dans le workflow, qui doit être présent dans `main` et être
exactement la version du checkout staging. Il sauvegarde le code, les données
locales, le `.env` et le WSGI sous `~/deployment-backups/production-<date>/`, puis
conserve les modifications locales dans un stash Git. Il préserve le `.env` de
production et complète uniquement le jeton administrateur manquant depuis staging.
La procédure vérifie que la base partagée est déjà migrée, sans appliquer de
migration, puis recharge uniquement `Galilee57.pythonanywhere.com`.
