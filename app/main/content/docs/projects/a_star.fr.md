---
title: 🧩 Projet – Jeu du Taquin (Algorithme A*)
summary: Version Française
---

**Ce projet est une application interactive qui permet de résoudre le jeu du taquin (8-puzzle) à l’aide de l’algorithme A\*.**
L’objectif est de réorganiser les tuiles pour atteindre l’état final en un minimum de coups.

La particularité du projet est la visualisation du processus de résolution, incluant l’exploration des états et la construction de l’arbre de recherche.

⚙️ **Fonctionnement technique**

Représentation de l’état
→ Le plateau est modélisé sous forme de tableau (liste de 9 éléments).
→ La case vide est représentée par 0.

Génération des états voisins
→ À partir d’un état, les mouvements possibles sont calculés (haut, bas, gauche, droite).
→ Chaque mouvement génère un nouvel état du taquin.

Algorithme A\*
→ Utilisation d’une file de priorité (heap) pour explorer les états.
→ Fonction de coût :  
 g(n) = nombre de coups effectués  
 h(n) = distance de Manhattan  
 f(n) = g(n) + h(n)

→ L’algorithme sélectionne toujours l’état avec le coût total minimal.

Reconstruction de la solution
→ Une fois l’état final atteint, le chemin est reconstruit à partir des parents.
→ La solution correspond à la suite des états jusqu’à l’objectif.

Interface utilisateur dynamique
→ Le plateau est généré dynamiquement en JavaScript.
→ L’utilisateur peut mélanger, éditer ou résoudre le taquin.

Visualisation de l’arbre
→ Les nœuds explorés sont affichés par profondeur (g).
→ Chaque état est représenté sous forme de mini-grille.
→ L’utilisateur peut afficher/masquer l’arbre et rejouer la solution.

Validation & interaction
→ Vérification si un taquin est résoluble (parité des inversions).
→ Feedback utilisateur (message, animation, score implicite via nombre de coups).

💡 **Intérêt du projet**

Ce projet met en valeur :
→ l’implémentation d’un algorithme de recherche (A\*)
→ l’utilisation d’une heuristique admissible (distance de Manhattan)
→ la manipulation de structures de données (heap, graph implicite)
→ la visualisation pédagogique d’un algorithme
→ la gestion d’interactions utilisateur (édition, animation, replay)

Il combine ainsi algorithmique, interface interactive et visualisation d’un processus de recherche.
