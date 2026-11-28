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

## Test de prompts avec LFM3 ou OpenAI

La page `/admin/llm` est accessible via **Test LLM** dans le bandeau admin après
connexion sur `/admin`. Elle utilise la session admin et son jeton CSRF. Configure
`ADMIN_PASSWORD_HASH` selon les instructions du README principal. Le formulaire affiche
le fournisseur actif et la réponse en texte brut. Il ne conserve pas d’historique.

### Mac Apple Silicon

Télécharger l’archive macOS arm64 de [llama.cpp b11960](https://github.com/ggml-org/llama.cpp/releases/tag/b11960).
Dans les commandes ci-dessous, remplacer le chemin par celui du binaire extrait.

```bash
LLAMA_SERVER=/chemin/vers/llama-server sh infra/llm/start.sh
```

Le premier lancement télécharge et vérifie le GGUF officiel LFM3‑1.7B `Q4_K_M`
(~1,1 Go) dans `~/.cache/flask-portfolio-llm`. `LLM_CACHE_DIR` permet de choisir
un autre chemin. Le serveur écoute sur `127.0.0.1:8081`. Dans un autre terminal,
avec l’environnement virtuel du projet activé :

```bash
LLM_PROVIDER=local FLASK_CONFIG=development flask --app wsgi llm-prompt 'Explique le RAG en français en une phrase.'
LLM_PROVIDER=local FLASK_CONFIG=development flask --app wsgi --debug run
```

### Docker Compose

Arrêter d’abord le serveur natif s’il occupe le port 8081.

```bash
LLM_PROVIDER=local docker compose --profile llm up --build
```

Le service CPU `llm` télécharge le modèle dans le volume `llm-models`.
Flask utilise `http://llm:8081/v1` et la machine hôte peut vérifier
`http://127.0.0.1:8081/health`. Le premier démarrage peut prendre le temps du
téléchargement. Pour utiliser le serveur natif depuis le conteneur web sous Docker
Desktop, définir `LLM_LOCAL_BASE_URL=http://host.docker.internal:8081/v1` et
démarrer Compose sans activer le profil `llm`.

### Railway staging

Dans `renewed-freedom`, ajouter un service privé nommé `llm` dans le même
environnement que `flask_app`. Connecter le dépôt sur la branche `staging` et
régler le répertoire racine de ce service sur `/infra/llm`. Railway construit le
`Dockerfile` de ce répertoire. Monter un volume sur `/models`. Utiliser une seule
réplique et aucun domaine public ni proxy TCP pour le service d’inférence.

- Service `llm` : fixer `PORT=8081`, configurer le healthcheck HTTP sur `/health`
  et laisser jusqu’à 600 secondes au premier démarrage.
- Service `flask_app` : définir `LLM_PROVIDER=local` et
  `LLM_LOCAL_BASE_URL=http://llm.railway.internal:8081/v1`. Configurer le hash admin
  dans les variables du service pour utiliser la page.
- Après déploiement, vérifier le healthcheck et envoyer un prompt via Flask.
  Mesurer la latence et la RAM avant d’augmenter le contexte (`LLM_CONTEXT_SIZE`,
  4096 tokens par défaut). Le serveur traite une génération à la fois.

Le circuit de déploiement Flask et ses migrations suivent toujours le workflow
staging du dépôt. La disponibilité du LLM est vérifiée indépendamment de
`/health/ready` de Flask.

### Utiliser OpenAI

Définir `LLM_PROVIDER=openai`, `OPENAI_MODEL` avec un modèle Chat Completions
accessible au compte et `OPENAI_API_KEY` dans les variables du serveur ou
le `.env` local. La page et la commande utilisent alors l’API OpenAI et lui
envoient le texte saisi. Le choix reste explicite si un fournisseur est indisponible.

Pour les futurs agents, `app.core.llm.chat_completion` accepte les messages
et les schémas d’outils de Chat Completions. Il renvoie le message assistant,
que l’appelant peut examiner avant d’exécuter un outil et d’en transmettre le
résultat au modèle.

## RAG des projets dans Test LLM

Le RAG indexe les fiches Markdown du Lab et les réalisations du catalogue admin
dans leur version éditoriale active, en français et en anglais. Les vecteurs
sont produits par Qwen3-Embedding-0.6B via un second processus llama.cpp.
La première exécution télécharge son GGUF Q8_0. LFM3 continue à servir le chat
sur son port habituel.

```bash
LLAMA_SERVER=/chemin/vers/llama-server sh infra/llm/start-embeddings.sh
```

Après une modification du corpus, cliquer sur **Reconstruire tout l’index RAG**
dans **Test LLM**, avec une session admin et Flask en mode développement.
Le bouton recalcule tous les passages. Le dernier index reste disponible durant
le calcul et est remplacé seulement après une reconstruction réussie.
Utiliser **Actualiser l’état** pour suivre le résultat.

On peut aussi reconstruire depuis un autre terminal, à la racine du portfolio :

```bash
FLASK_CONFIG=development .venv/bin/flask --app wsgi rag-build
```

Le JSON est enregistré dans `instance/portfolio-rag.json` par défaut. Il contient
les textes privés et leurs vecteurs. Le dossier `instance/` est ignoré par Git.
`RAG_INDEX_PATH` permet de définir un autre fichier privé et
`RAG_EMBEDDING_BASE_URL` de configurer le serveur d’embeddings compatible,
`http://127.0.0.1:8082/v1` par défaut. Utiliser le même modèle pour indexer et
retrouver les passages.

Dans **Test LLM**, choisir **Chercher dans mes projets** dans le champ **Type de recherche**. Flask cherche
par similarité cosinus dans la langue de l’interface et joint jusqu’à cinq
extraits à la question. La page affiche les extraits, leurs références et leurs
scores. Avec `LLM_PROVIDER=local`, embeddings et génération restent sur le Mac.
Avec `LLM_PROVIDER=openai`, la génération transmet à OpenAI la question et les
extraits retenus. Le calcul des embeddings utilise toujours le serveur configuré
pour le RAG. Pour activer ce mode sur un autre hôte, lui fournir un index privé
et un serveur d’embeddings accessible depuis Flask.

**Synthèse des compétences** affiche les effectifs calculés pendant la dernière
reconstruction sur les fiches du Lab et du catalogue. Les versions française
et anglaise comptent comme une seule fiche. Le bilan indique la couverture des
tags existants et jusqu’à trois exemples par compétence. Le contexte
**Synthèse des compétences du catalogue** permet de poser une question à partir
de ces statistiques, tandis que **Chercher dans mes projets** retrouve
des extraits pour les questions ciblées.

**Comparer une offre à mes projets** accepte un descriptif de 4 000 caractères
maximum. La recherche par similarité interroge plusieurs parties de l’offre et
sélectionne jusqu’à six fiches distinctes par similarité. Les formations sont
ajoutées au contexte pour documenter les exigences de diplôme. Le modèle rapproche les exigences
des extraits et des compétences déclarées, puis indique les points partiellement
étayés ou sans preuve dans ces sources. Avec LFM3, l’offre reste en local.

### RAG admin sur Railway avec OpenAI

Utiliser `LLM_PROVIDER=openai`, `OPENAI_MODEL=gpt-6-luna`,
`OPENAI_API_KEY` et `RAG_EMBEDDING_PROVIDER=openai` sur `flask_app`.
OpenAI reçoit les passages lors de l’indexation et les questions lors des
recherches. La génération reçoit le contexte sélectionné. Le catalogue et ses illustrations sont publics. La page de test LLM reste
réservée à la session admin.

Monter un volume privé sur `/rag` et définir
`RAG_INDEX_PATH=/rag/portfolio-rag.json`. Au démarrage Railway, exécuter
`flask --app wsgi rag-build --if-stale` avant Gunicorn. La commande réutilise
l’index si le modèle et le corpus sont identiques. Le volume doit être
accessible à l’utilisateur `flask` du conteneur.
