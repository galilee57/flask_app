# Déploiements Docker parallèles

Le conteneur sert `wsgi:app` avec Gunicorn sur `0.0.0.0:$PORT` (8080 par défaut).
Le build compile Tailwind puis copie uniquement Python et les assets dans l'image finale.
Docker et sa CI utilisent Python 3.14 ; PythonAnywhere et sa CI conservent Python 3.10.
`requirements.txt` déclare les dépendances directes ; `requirements.lock` fixe les versions
résolues pour Python 3.14. `requirements-python310.lock` verrouille séparément les
dépendances de PythonAnywhere, notamment NumPy 2.2.6. Les outils de développement sont
dans `requirements-dev.txt`.

## Local avec Docker Compose

Configurer le fichier `.env` à la racine du projet et remplacer les trois valeurs privées.
L'application charge ce fichier via `app/core/config.py` ; Docker Compose le lit également.
Utiliser un mot de passe PostgreSQL composé de caractères sûrs dans une URI
(par exemple une valeur hexadécimale aléatoire), ou encoder ses caractères réservés.
Ne jamais commiter `.env`.

```bash
docker compose up --build
```

PostgreSQL est conservé dans un volume. Le service `migrate` termine avant le démarrage
web ; aucune migration ne s'exécute au démarrage de chaque worker. Ouvrir
http://localhost:8080 et vérifier `/health/ready`.

## Données et sessions

En mode conteneur, `DATABASE_URL` PostgreSQL, `SECRET_KEY` et `ADMIN_API_TOKEN` sont
obligatoires. Les tâches et motifs sont stockés en SQL. Les sessions sont enregistrées
en SQL avec un identifiant opaque signé dans un cookie Secure/HttpOnly/SameSite=Lax.
Leurs données expirent après 24 heures depuis leur dernière modification. Les requêtes
d'un visiteur existant sont sérialisées par un verrou PostgreSQL pour éviter les
modifications concurrentes des jeux. Les grilles 3D sont compactées avant stockage.
Exécuter quotidiennement `flask --app wsgi sessions-prune` dans une tâche externe.
Dimensionner les pools PostgreSQL : chaque worker Gunicorn peut ouvrir jusqu'à 20 connexions
pour les sessions, en plus du pool SQLAlchemy des routes. Les limites PostgreSQL doivent
couvrir le nombre de workers par instance, le nombre maximal d'instances et les jobs.

Toutes les instances d'un même déploiement doivent partager la clé de session et la base.
Deux domaines différents ne partagent pas automatiquement leurs cookies : leurs données
SQL peuvent être communes, mais le visiteur reçoit une session de jeu par domaine.
Utiliser des bases et secrets séparés pour staging et production.

Pour récupérer les anciens fichiers, sauvegarder d'abord la base, appliquer les
migrations puis lancer une fois, depuis un environnement ayant accès aux fichiers :

```bash
flask --app wsgi db upgrade
flask --app wsgi storage-import --todos /chemin/instance/data/todolist.json --patterns /chemin/instance/data/patterns
```

L'import préserve les sources et ignore les identifiants déjà présents. Il ne transfère
pas les autres tables d'une ancienne base SQLite vers PostgreSQL : programmes, trains et
statistiques nécessitent un transfert de données distinct si leur conservation est requise.
Les anciens cookies et états de jeu en mémoire sont réinitialisés à cette migration.
Les variables `TODOLIST_DATA_PATH` et `PATTERN_STORAGE_DIR` activent explicitement les
anciens fichiers sur un hébergement classique ; elles sont refusées en mode conteneur.

Le DQN Snake est optionnel. Entraîner hors des workers web et placer le `.npz` validé
sous `app/projects/snake/models/` avant le build, puis définir `SNAKE_DQN_PATH` vers ce
fichier. Ainsi, le même modèle est disponible sur chaque plateforme. Sans checkpoint,
l'API RL répond 409 avec une instruction d'entraînement. Aucun entraînement automatique
ni stockage durable dans `/tmp` n'est prévu.

## Azure ACR et Container Apps

`staging.bicep` décrit ACR sans compte administrateur, une identité managée avec AcrPull,
un environnement Container Apps, l'application HTTP et un job manuel de migration.
PostgreSQL est externe : le provisionner séparément et fournir une URI TLS
`postgresql+psycopg://user:password@host:5432/database?sslmode=require`.
Les ressources visées doivent être dédiées à staging.

Pour le premier déploiement, créer ACR et publier `portfolio:<commit>` avant de déployer
le template complet (par exemple avec `az acr create` puis `az acr build`). Fournir les
paramètres privés via un fichier de paramètres hors du dépôt ou le gestionnaire de
secrets de votre CI. Le template accepte des paramètres sécurisés ; ne pas les fournir
en clair dans l'historique du shell. Démarrer le job de migration et attendre son succès
avant de donner accès au site : la readiness reste indisponible tant que le schéma manque.

Le workflow `container-staging.yml` s'exécute sur PR et `staging`. Son job Azure reste
désactivé jusqu'à `AZURE_CONTAINER_DEPLOY_ENABLED=true`. Configurer :

| Type | Noms |
|---|---|
| Variables GitHub | `AZURE_CONTAINER_DEPLOY_ENABLED`, `AZURE_ACR_NAME`, `AZURE_RESOURCE_GROUP`, `AZURE_CONTAINER_APP_NAME`, `AZURE_MIGRATION_JOB_NAME` |
| Secrets de l'environnement `staging` | `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` |

Créer une identité Azure pour GitHub avec une fédération OIDC ciblant l'environnement
GitHub `staging`. Lui accorder uniquement les droits nécessaires pour construire dans ACR
et mettre à jour l'application et son job. Les secrets applicatifs sont configurés dans
Container Apps/Bicep, jamais dans l'image. Le workflow publie le tag du commit, exécute le
job de migration une seule fois, puis met à jour l'application et contrôle sa readiness.
Le workflow PythonAnywhere existant continue indépendamment.

## Vercel et autres plateformes

Vercel détecte `Dockerfile.vercel` à la racine. Son contenu est identique au Dockerfile
portable ; la CI vérifie cette égalité. Importer le dépôt et configurer `PORT=8080`,
`DATABASE_URL`, `SECRET_KEY` et `ADMIN_API_TOKEN` dans les environnements concernés.
Pour respecter le circuit staging, désactiver les publications automatiques de production
et configurer la branche/environnement souhaité avant l'import.
Appliquer les migrations dans une étape CI dédiée avant publication, ou partager le schéma
avec Azure après le succès de son job. Ne jamais lancer deux jobs de migration simultanés
sur la même base. Le support Container Images/VCR de Vercel est actuellement en bêta ;
les conteneurs suivent les limites de durée et l'autoscaling des Functions.
Vercel construit et publie dans VCR : il ne récupère pas directement notre image privée ACR.

Render ou une autre plateforme acceptant Docker peut construire `Dockerfile`, utiliser le
même port et les mêmes variables. Prévoir une commande de pré-déploiement pour Alembic
si sa base est indépendante. Vérifier le support du registre privé avant de choisir
le déploiement depuis ACR plutôt que depuis le dépôt.

`/health/live` vérifie le processus ; `/health/ready` vérifie la présence de la table des
sessions et l'accès SQL. Les logs partent vers stdout/stderr. Configurer les probes de la
plateforme. Pour les en-têtes HTTPS derrière un proxy, renseigner `FORWARDED_ALLOW_IPS`
uniquement selon les garanties du fournisseur ; aucune confiance globale n'est activée.

Références : [Azure](https://learn.microsoft.com/en-us/azure/container-apps/github-actions),
[identité managée ACR](https://learn.microsoft.com/en-us/azure/container-apps/managed-identity-image-pull),
[Vercel Container Images](https://vercel.com/docs/functions/container-images),
[Render Docker](https://render.com/docs/docker).
