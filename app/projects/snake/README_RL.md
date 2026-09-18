# Snake DQN

Le mode **AI (DQN / RL)** utilise un réseau NumPy 11 → 128 → 3.
A* reste accessible séparément. La clé historique `astar_nn` est conservée
pour les statistiques, mais ce mode est désormais un DQN autonome.

Depuis le dépôt et avec son environnement activé :

```sh
FLASK_CONFIG=development flask --app wsgi snake snake-train --episodes 1000 --seed 42
```

Le modèle est enregistré dans `instance/snake_dqn.npz`. La configuration
`SNAKE_DQN_PATH` peut fournir un autre chemin. Relancer la commande démarre
un nouvel entraînement et remplace le modèle à la fin. Les parties utilisées
pour apprendre sont indépendantes du jeu web et ne créent aucune statistique
SQL. Aucun entraînement ni exploration aléatoire n'a lieu dans la route web.

Après l'entraînement, sélectionner **AI (DQN / RL)**, Reset, puis Jouer.
Sans modèle, le jeu affiche une erreur explicite. L'enregistrement SQL des
scores conserve l'exigence `X-Admin-Token` existante.

L'apprentissage utilise Double DQN et Adam. Récompenses de base : fruit +10,
collision −10, déplacement −0,01. Une récompense de progression s'ajoute :
`0,99 × potentiel suivant − potentiel actuel`, avec `potentiel = −0,1 × distance
Manhattan au fruit`. Le potentiel est nul à la fin de la partie ; après un
fruit mangé, il est calculé avec le nouveau fruit. Ce signal n'intervient
que dans l'entraînement, et ne change pas les scores du jeu.
Les anciens fichiers restent lisibles, mais il faut réentraîner pour bénéficier
de ces corrections. L'optimiseur n'est pas sauvegardé : il ne s'agit pas
d'une reprise d'entraînement. L'entraînement
termine aussi une partie après 100 × longueur déplacements sans fruit.
Cette limite ne s'applique pas au jeu web. La queue actuelle reste un obstacle,
conformément aux règles initiales. Remplir le plateau termine la partie.

L'état compact (dangers immédiats, direction, position relative du fruit)
ne décrit pas tout le corps. Une bonne performance n'est pas garantie par
1000 parties ; comparer plusieurs graines et les scores sans exploration à
A* avant de conclure à une amélioration. Les statistiques existantes mesurent
les étapes aux fruits, et ne constituent pas un bilan complet par partie.

## Résultats de parties complètes

Les nouvelles comparaisons utilisent `snake_result`. Les anciennes lignes de
`snake_stats` (une ligne par fruit) restent conservées mais ne sont pas mélangées
avec les résultats finaux. L'option d'enregistrement existe uniquement en mode
humain ; le bilan et les comparaisons apparaissent à la fin de la partie.
En production, enregistrer un résultat humain nécessite le jeton administrateur.
Il n'est conservé que dans le champ du navigateur, jamais dans le stockage local.

Après `flask --app wsgi db upgrade`, exécuter une fois :

```sh
flask --app wsgi snake snake-benchmark --seed 42
```

La commande joue une partie A* puis une partie DQN sans accès SQL pendant la
simulation, puis enregistre les deux résultats dans une seule transaction.
`--dry-run` permet de simuler sans écrire. Relancer la même référence n'ajoute
pas de doublon. Le seed, l'empreinte du modèle DQN et le motif de fin sont conservés.
Le nombre de déplacements n'inclut pas la tentative de collision, conformément
au compteur historique du jeu. Les simulations s'arrêtent également après
10 000 déplacements ou 100 × la longueur du serpent sans fruit : ces limites
sont signalées dans le résultat, jamais présentées comme une collision.

Le DQN entraîné localement est inclus sous `models/snake_dqn.npz` pour Railway.
`SNAKE_DQN_PATH` reste prioritaire, puis le modèle de l'instance locale, puis
le modèle inclus. L'entraînement par CLI écrit toujours dans le chemin explicite
ou le dossier instance, sans écraser implicitement le modèle distribué.
