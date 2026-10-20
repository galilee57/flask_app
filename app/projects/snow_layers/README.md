# Snow Layers · Lab

Le blueprint `/projects/snow_layers` utilise la même base `DATABASE_URL` que
le portfolio, via Flask-SQLAlchemy. Les tables normalisées `snow_stations`,
`snow_sources`, `snow_imports` et `snow_daily_observations` sont gérées par
Alembic (révision `d14e8b73a902`). La table `stations` du projet Trains n’est
pas modifiée. Aucune base SQLite n’est créée à la visite d’une page.

## Installation et import

Appliquer les migrations, puis importer l’archive SQLite normalisée
(décembre–avril) préparée avec `scripts/compact_snow_layers.py` :

```sh
flask --app wsgi db upgrade
flask --app wsgi snow-import --source CHEMIN/snow_layers_normalized_winter.sqlite
```

L’import ouvre la source en lecture seule, vérifie son intégrité et ses clés
étrangères, conserve les identifiants, vérifie chaque colonne après insertion
et confirme que son SHA-256 n’a pas changé. Une relance ignore les lignes
identiques ; un conflit annule l’intégralité de la transaction. Les identifiants
ne sont pas remappés : si la destination contient déjà des données différentes,
le conflit doit être résolu explicitement. `--dry-run` vérifie puis annule les
insertions. Les séquences PostgreSQL sont ajustées après import pour permettre
les prochains ajouts. Les archives et sauvegardes restent dans `instance/`,
ignoré par Git. Aucun import de données n’est lancé par une migration.

L’ancienne variable `SNOW_LAYERS_DATABASE_URL` n’est plus utilisée. La base
initiale et les copies optimisées restent indépendantes et inchangées.
L’import distant se fait uniquement dans le cadre du workflow staging documenté.

## API et données

GET `/api/stations`, `/api/snow-depth?station=meribel` et
`/api/comparison?station=meribel&station=tignes` conservent leurs contrats JSON.
Les moyennes saisonnières sont agrégées en SQL ; les séries quotidiennes ne sont
chargées que pour la station demandée. Les dates du graphique historique sont
alignées par mois/jour, y compris les années bissextiles.

POST `/api/snow-depth/import` accepte `{"station":"tignes","season":"2024-2025"}`.
En production, envoyer `X-Admin-Token` via un client administrateur ; aucun jeton
n’est exposé dans la page. Les nouvelles observations utilisent la provenance
normalisée. Les dates d’import originales sans fuseau sont conservées en UTC.
La démonstration Méribel reste le repli si aucune série n’est importée.

## Interface et crédits

Le CSS du prototype est isolé dans `@scope (.snow-app)` ; les ajustements
mobile-first sont en fin de fichier. L’interface d’exploration reste française ;
les fiches Infos suivent la langue du portfolio. Leaflet et les tuiles OSM
nécessitent Internet. Réanalyse : Open-Meteo / ERA5-Land.

Photo : Romain Malaunay, La Plagne-Tarentaise, Unsplash
https://unsplash.com/photos/cXrhDuOZBiI (licence Unsplash).

## Déploiement avec historique

L’export public `data/winter_history.jsonl.gz` (environ 4 Mo) est livré avec
l’application. Après `db upgrade`, exécuter `flask --app wsgi snow-seed`.
Le SHA-256 et chaque valeur importée sont vérifiés. La migration
`e25f9c84b013` crée le suivi des imports : les déploiements suivants ne
réécrivent pas les observations, même si elles ont été actualisées ensuite.
Le workflow PythonAnywhere staging et la commande pre-deploy Railway exécutent
cette étape. Aucune base de production n’est versionnée.
