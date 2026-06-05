---
title: 🌍 Puissance 4 et algorithme déterministe
summary: Version Française
---

Ce projet apporte une nouveauté par rapport aux algorithmes du Sudoku et du Taquin. Ici, on entre dans les jeux à deux adversaires.

Les règles sont connues et relativement simples : le jeu est déterministe.
Un algorithme "autonome" type Reinforcement Learning est tout à fait possible, quoi que peu efficace, car il faudrait jouer des millions de parties pour qu'il acquiert une bonne performance.

On utilise ici l'agorithme MIN-MAX qui élabore un arbre des coups d'une certaine profondeur, pour anticiper ses propres coups et ceux de l'adversaire. Une évalutaion HEURISTIQUE permet de prédire les chance de gagner : l'objectif est de MAXimiser ses chances et de MINimiser ceux de l'autre joueur.

La qualité et la précision de l'heuristique déterminent la performance de l'algorithme. On attribuera des points pour le risque d'avoir 2 ou 3 pions alignés, d'être bloqué, de gagner ou de perdre.

Si le jeu a été entièrement résolu, il contient environ 4E12 plateaux différents : si un serveur de calcul peut parcourir l'intégralité de l'arbre, pour une machine personnelle, cela reste inaccessible. La profondeur rend exponentielle le temps de calcul et d'exploration.

Pour accélérer l'algorithme, on utilisera une version dite alpha-bêta qui permet de ne pas explorer des parties inutiles de l'arbre.

En outre, on completera Min-Max par un MCTC (Monte Carlo Tree Search) pour booster / renforcer son comportement.
