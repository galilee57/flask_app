---
title: 🌍 Projet – Algorithmes de résolution
summary: Version Française
---

# 🧠 Algorithmes de résolution du Sudoku

Contrairement au jeu du taquin — pour lequel le résultat final est connu — ce qui importe ici n’est pas le chemin, mais la solution finale.

Cependant, le choix de l’algorithme reste fondamental afin d’optimiser :
• les performances,
• la complexité d’implémentation,
• la qualité de l’exploration.

---

# 🧬 Approche génétique

L’algorithme génétique constitue une approche particulièrement adaptée.

Le principe consiste à :
• générer des candidats en remplissant les cases vides,
• évaluer leur qualité grâce à une fonction de coût,
• appliquer des mutations lorsque les combinaisons échouent.

La fonction de coût permet de mesurer le nombre de conflits, la validité des lignes, des colonnes et des blocs.

---

# ⚠️ Le problème des optimums locaux

La principale difficulté du Sudoku — surtout lorsque peu de chiffres sont connus au départ — est l’existence d’optimums locaux.

Ces configurations semblent prometteuses mais empêchent l’algorithme de progresser vers la solution globale. Le défi consiste donc à équilibrer :
• **Exploration** : Aspect aléatoire, découverte de nouvelles pistes, diversité
• **Exploitation** : Aspect déterministe, conservation des meilleurs candidats, Optimisation

L’exploitation permet de conserver des candidats prometteurs afin de pouvoir y revenir en cas de blocage.

---

# 🔁 Backtracking local

L’algorithme implémenté autorise également un **backtracking local**.

Cela signifie qu’il peut :
• revenir en arrière,
• abandonner une branche non prometteuse,
• repartir depuis un meilleur candidat.

Cette approche hybride évite le **backtracking naïf**, particulièrement lent car il explore systématiquement tous les chemins possibles.

---

# 🎯 Heuristique de sélection

L’algorithme commence par rechercher :
• la case présentant la meilleure heuristique,
• c’est-à-dire la case la plus contrainte.

Cette stratégie réduit fortement le nombre de possibilités à explorer.

---

# 🧪 Hybridation des méthodes

L’approche utilisée combine plusieurs techniques :
• heuristiques,
• génération génétique,
• élitisme,
• mutations,
• backtracking local.

Le mécanisme génétique fonctionne ainsi :

• génération de plusieurs candidats,
• conservation des meilleurs individus (_élitisme_),
• croisement des meilleurs candidats,
• introduction de génomes aléatoires afin de maintenir la diversité.

Cette diversité est essentielle pour éviter les optimums locaux.

---

# 🧩 Particularité du Sudoku

Le Sudoku possède une caractéristique importante : une seule erreur dans une case peut invalider toute la grille.
Cela produit des minimums locaux très profonds dont il est difficile de s’extraire.

Le problème devient alors autant :
• un problème de recherche,
• qu’un problème d’équilibre entre exploration et exploitation.
