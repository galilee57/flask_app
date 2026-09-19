# Tétris local

Route : `/projects/tetris/`. Le moteur, le rendu et les records fonctionnent dans
le navigateur, sans API ni base de données. Les records humain et IA sont séparés
et sauvegardés avec `localStorage` (en mémoire si le stockage est indisponible).
Les vitesses sont conservées séparément durant la session : gravité humaine de
800 ms à 80 ms ; IA de 2 s à 0,2 s par action (1,6 s par défaut). Le choix et
le résultat restent affichés pendant trois intervalles. La descente IA est
animée case par case. Le mode manuel suspend la progression automatique et
« Étape suivante » avance une opération, y compris pendant la pause.
Le panneau affiche les trois meilleurs placements distincts et leurs critères
réels, avec une cible en pointillés sur le plateau. Les points ne sont pas multipliés par la vitesse.

## Lancement et validation

```sh
FLASK_CONFIG=development .venv/bin/flask --app wsgi run --port 5055
node --test tests/tetris_engine.test.cjs
.venv/bin/python -m pytest tests/test_tetris.py -q
```

Les styles Tailwind 4 sont compilés localement, sans CDN. Après modification du template :

```sh
npx @tailwindcss/cli -i app/projects/tetris/static/css/input.css -o app/projects/tetris/static/css/tailwind.css --minify
```

## Futur réseau neuronal

Le mode IA utilise actuellement une heuristique (hauteur, trous, irrégularité,
lignes complétées), pas un NN. Le moteur est indépendant du DOM et exportable
avec CommonJS pour les tests ou un futur environnement d'entraînement.

`window.TetrisAI.setPolicy(policy, name)` branche un agent synchrone. Il reçoit
une copie `{board, piece, next, score, lines, over}` : grille 20 × 10 de `null`
ou lettres de pièces, pièce `{type, matrix, x, y}` et type suivant. Il retourne
au maximum 40 actions parmi `left`, `right`, `rotate`, `drop`. Une décision place
une pièce : les actions avant le premier `drop` sont animées une par une, puis
la pièce descend case par case avec les mêmes points qu’une chute immédiate.
`analyze(snapshot)` expose les candidats classés et leurs métriques ;
`AIPlayback` gère l’exécution progressive indépendamment du DOM. Les agents
personnalisés gardent ce contrat d’actions, mais aucun critère explicatif ne
leur est attribué sans données fournies par l’agent. Les mouvements impossibles sont ignorés par le moteur.
Une politique invalide ou une exception met la partie en pause. Pour un modèle
asynchrone, ajouter un adaptateur dédié avant de connecter son inférence.

`getState()` fournit une copie de l'observation et `resetPolicy()` restaure
l'heuristique. Changer de politique remet la partie à zéro. Les records des agents
partagent la catégorie IA. Rotations avec corrections horizontales simples,
sans système SRS complet ni délai de verrouillage.
