---
title: 🌍 Puissance 4 et algorithme déterministe
summary: Version Française
---

**Puissance 4 et intelligence artificielle**

Ce projet introduit une nouveauté par rapport aux résolutions du **Sudoku** ou du **Taquin** : il s'agit d'un **jeu à deux adversaires**.

Les règles sont simples et entièrement connues. Le jeu est **déterministe**, c'est-à-dire qu'aucun événement aléatoire n'intervient pendant une partie. Il est donc possible d'anticiper les conséquences de chaque coup.

Une approche basée sur le **Reinforcement Learning** serait envisageable. Cependant, pour atteindre un bon niveau de jeu, il faudrait générer et analyser des millions, voire des milliards de parties. Cette méthode est donc peu adaptée à un projet pédagogique.

**L'algorithme Minimax**

L'intelligence artificielle repose ici sur l'algorithme **Minimax**.
Le principe consiste à construire un **arbre des coups possibles** jusqu'à une certaine profondeur. L'algorithme simule alternativement les coups de l'IA et ceux de son adversaire afin d'anticiper les conséquences de chaque décision.

▶︎ L'IA cherche à **MAXimiser** ses chances de gagner.
▶︎ Elle suppose que son adversaire cherche à **MINimiser** ces mêmes chances.

Le nom **Minimax** provient directement de cette stratégie.

**L'évaluation heuristique**

Il n'est généralement pas possible d'explorer l'intégralité de l'arbre de recherche. Une fonction d'évaluation, appelée **heuristique**, permet donc d'estimer la qualité d'une position.

Cette heuristique attribue des scores selon différents critères :

▶︎ aligner deux pions ;
▶︎ aligner trois pions ;
▶︎ contrôler la colonne centrale ;
▶︎ bloquer une menace adverse ;
▶︎ créer une position gagnante ;
▶︎ éviter une défaite immédiate.

La qualité de cette fonction d'évaluation détermine en grande partie les performances de l'intelligence artificielle.

**Complexité du problème**

Le Puissance 4 a été entièrement résolu mathématiquement. On estime qu'il existe environ **4 × 10¹² positions différentes**.

Explorer exhaustivement cet espace est irréaliste sur une machine personnelle. Le nombre de positions à analyser augmente de façon exponentielle avec la profondeur de recherche.

**Optimisation : l'élagage alpha-bêta**

Pour accélérer les calculs, on utilise une version optimisée de Minimax appelée **Alpha-Bêta** (_Alpha-Beta Pruning_).

Cette technique permet d'éliminer de nombreuses branches de l'arbre qui ne pourront jamais conduire à une meilleure solution. Le temps de calcul est ainsi fortement réduit sans modifier le résultat final.

**Pourquoi ne pas utiliser MCTS ?**

Une autre famille d'algorithmes, le **Monte Carlo Tree Search (MCTS)**, pourrait être utilisée pour renforcer l'intelligence artificielle.

Le MCTS est particulièrement efficace lorsque :

▶︎ l'espace de recherche est immense ;
▶︎ la fonction d'évaluation est difficile à concevoir ;
▶︎ le jeu possède une très grande complexité stratégique.

Il est notamment utilisé dans des jeux comme le **Go**.

Dans le cas du Puissance 4, un **Minimax avec élagage alpha-bêta**, associé à une bonne heuristique et à une profondeur de recherche suffisante, offre déjà d'excellentes performances tout en restant relativement simple à comprendre et à implémenter.
