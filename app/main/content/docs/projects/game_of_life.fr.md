---
title: 🧬 Projet – Game of Life
summary: Version Française
---

**Ce projet est une implémentation du Game of Life, imaginé par John Conway.**

Il s’agit d’un automate cellulaire, c’est-à-dire un système composé de cellules disposées sur une grille, dont l’état évolue au fil du temps selon des règles simples et locales.

🔍 **Qu’est-ce qu’un automate cellulaire ?**

Un automate cellulaire repose sur trois principes fondamentaux :
→ une grille de cellules (souvent 2D)
→ un état discret pour chaque cellule (vivante ou morte)
→ des règles locales qui déterminent l’état futur d’une cellule en fonction de ses voisines.

Chaque itération applique les mêmes règles à l’ensemble de la grille, sans contrôle central.
Dans le Game of Life, les règles sont volontairement minimalistes :
→ une cellule survit ou meurt selon le nombre de voisines vivantes
→ une cellule morte peut “naître” si les conditions sont réunies

💡 **Pourquoi ce projet est intéressant ?**

Malgré des règles extrêmement simples, le système génère des comportements complexes et imprévisibles : desstructures stables, des oscillateurs, des motifs mobiles ou des strctures qui interagissent.
C’est un excellent exemple de complexité émergente, où des phénomènes riches apparaissent sans programmation explicite du comportement global.

Ce projet permet de :
→ comprendre comment des systèmes complexes peuvent émerger de règles locales
→ explorer les notions de simulation, d’itération et d’états
→ manipuler des grilles, des voisins, et des mises à jour synchronisées
→ faire le lien entre informatique, mathématiques et modélisation de systèmes vivants

🧠 **Intérêt plus large**

Le Game of Life est souvent utilisé comme porte d’entrée vers la modélisation de systèmes complexes, la simulation, la théorie des systèmes et la réflexion sur l’auto-organisation.
Ce projet s’inscrit ainsi naturellement dans une démarche orientée simulation, en continuité avec des projets plus ambitieux à venir.

_La difficulté est qu'il nécessite des grilles importantes pour permettre la formation et le mouvement de grandes structures._
Il est ainsi peu compatibke avec des écrans de smartphones : j'ai fait le choix de le rendre responsive en réduisant le nombre de cases plutôt que la taille de la grille qui aurait rendu la leture inconfortable.
