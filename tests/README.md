# Tests du portfolio

La suite contient **86 cas Pytest** : les **19 cas déjà présents**, conservés,
plus **67 cas ajoutés** lors de la remise en place de l'environnement de développement.
Les paramètres FR/EN et les différentes autorisations comptent chacun comme un cas.

## Installation et lancement

Exécuter les commandes depuis la racine du projet :

```bash
python3 -m venv .venv  # uniquement si l'environnement n'existe pas encore
source .venv/bin/activate
python -m pip install -r requirements.lock -r requirements-dev.txt
python -m pip check
python -m pytest -q
```

Le serveur Flask n'a pas besoin d'être lancé : les tests utilisent son client interne.
Python 3.14 a été utilisé pour la validation. `pytest.ini` configure le chemin
Python et la découverte des tests dans ce dossier.

Pour cibler un sujet ou afficher chaque cas :

```bash
python -m pytest tests/test_portfolio.py -v
python -m pytest tests/test_todolist_persistence.py -q
python -m pytest tests/test_security_and_api.py -q
python -m pytest --collect-only -q
```

## Couverture des 19 cas existants

| Fichier | Cas | Vérifications |
| --- | ---: | --- |
| `test_configuration.py` | 3 | Production par défaut, rejet d'une configuration inconnue, paramètres de sécurité. |
| `test_factory_registry.py` | 4 | Enregistrement des blueprints et de leurs préfixes, catalogue de projets, contexte des pages avec et sans projet. |
| `test_game_of_life_patterns.py` | 2 | Enregistrement d'un motif soumis à autorisation dans un dossier temporaire et validation du nom. |
| `test_migration_graph.py` | 1 | Graphe Alembic avec une seule tête attendue. Ce test ne déroule pas les migrations sur une base. |
| `test_security_and_api.py` | 4 | Routes de diagnostic masquées hors debug, en-têtes de sécurité, autorisations et opérations sur programmes et tâches. |
| `test_snake_security.py` | 1 | Refus d'un mouvement enregistrant des statistiques avant toute mutation du jeu, puis acceptation avec le bon jeton. |
| `test_todolist_api.py` | 4 | Création, lecture, modification, suppression, validation des entrées, tâche absente et jeton administrateur non configuré. |

## Nouveaux tests

### Portfolio : 57 cas dans `test_portfolio.py`

- **52 cas** : 26 pages explicites en français et en anglais (accueil, présentation,
  expériences et projets). Chaque page doit répondre HTTP 200 en HTML, posséder
  un élément `main` et servir ses ressources locales référencées par `src` ou
  les liens de feuilles de style et d'icônes. Une route supprimée reste donc détectable.
- **1 cas** : la feuille Tailwind compilée est servie en CSS et contient les
  éléments attendus du thème et les utilitaires. Les scripts vides réservés à de
  futurs développements, comme `projet_test.js`, sont autorisés.
- **2 cas** : français par défaut, passage à l'anglais, mémorisation du choix,
  langue inconnue ignorée et isolation entre deux visiteurs.
- **1 cas** : une page inconnue renvoie HTTP 404.
- **1 cas** : Markdown et Pygments produisent effectivement du code coloré.

### Persistance : 10 cas dans `test_todolist_persistence.py`

- **1 cas** : une tâche créée par l'API est relue par une nouvelle instance du
  dépôt de données, depuis le fichier temporaire.
- **6 cas** : création, modification et suppression refusées avec un jeton absent
  ou erroné ; le fichier est comparé octet par octet pour vérifier son intégrité.
- **2 cas** : stockage JSON corrompu ou de structure invalide signalé sans altérer
  le fichier existant.
- **1 cas** : requête dépassant la limite de taille rejetée par HTTP 413 sans
  création d'un fichier de tâches.

## Isolation et sécurité des tests

Les fixtures de `conftest.py` utilisent `create_app("testing")`, une base SQLite
**en mémoire** et les répertoires temporaires de Pytest pour les tâches et motifs.
Les tables sont créées puis supprimées à chaque test. Le jeu Snake global est
réinitialisé avant et après chaque cas. Aucun jeton de production n'est nécessaire.

Les connexions socket sortantes sont bloquées pendant les tests. Pour ajouter un
scénario utilisant une API externe, remplacer son client par un mock avec
`monkeypatch` ; ne pas appeler le service réel. Le client de test Flask fonctionne
sans réseau. Les tests ne migrent ni ne modifient la base locale du portfolio.

## Compilation Tailwind et limites

La vérification Python porte sur le CSS présent dans le dépôt. Pour vérifier la
chaîne Node.js complète après une installation ou un changement de styles :

```bash
npm ci
npm run build:css
python -m pytest tests/test_portfolio.py -q
```

`npm run watch:css` active la recompilation pendant le développement.
`python -m pip check` vérifie la cohérence des dépendances Python installées.

Ces tests ne pilotent pas de navigateur, n'exécutent pas le JavaScript des jeux,
ne contrôlent pas le rendu visuel ou responsive, les URL externes, les images
chargées par CSS ou les ressources chargées dynamiquement par JavaScript.
Les deux langues sont testées pour le rendu, mais cela ne constitue pas une
vérification exhaustive des traductions. Ils ne prouvent pas non plus que toutes
les fonctionnalités métier de chaque projet sont couvertes.

Le fichier `test_routes_musculation.http` contient des requêtes manuelles pour un
client HTTP d'éditeur ; il n'est pas exécuté par Pytest. Vérifier sa destination
avant utilisation et privilégier la suite isolée ci-dessus.

## Résultat de validation

Dernière exécution lors de l'ajout : **86 tests réussis**. Quatre avertissements
existants concernent `datetime.utcnow()` et `Query.get()` dans les chemins
SQLAlchemy. Ils restent visibles ; la suite ne les masque pas.

Pour ajouter une régression, créer une fonction `test_<comportement>` dans un
fichier `test_*.py`, utiliser les fixtures et vérifier un résultat observable
(code HTTP, contenu, état persistant). Lors de l'ajout d'une migration, actualiser
la tête attendue de `test_migration_graph.py` après vérification du graphe.
