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
