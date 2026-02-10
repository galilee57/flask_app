---
title: 🧬 Projet – Game of Life 3D (Three.js)
summary: Version Française
---

**Ce projet est une version 3D du Game of Life, un automate cellulaire.**

C'est un système composé de cellules disposées sur une grille, dont l’état évolue au fil du temps selon des règles simples et locales.
Il s'inspire du design de la chaine YouTube dont le lien est dans le footer.

🔍 **Automate cellulaire ?**

Un automate cellulaire repose sur :
→ une grille (ici en 3D),
→ des états discrets (vivant / mort),
→ une règle de transition basée uniquement sur le voisinage.

À chaque itération, toutes les cellules sont mises à jour en appliquant ces règles, sans “contrôle central”.

🌐 **Pourquoi la 3D change tout ...**

En 3D, on passe d’un simple damier à un volume : chaque cellule a davantage de voisines, ce qui crée des dynamiques plus riches et des structures plus “organiques”. On observe des phénomènes d’émergence encore plus surprenants : motifs stables, oscillations, croissance ou extinction selon les paramètres.

🎨 **Rendu et interaction avec Three.js**

Le projet utilise Three.js pour visualiser la simulation en temps réel :
→ chaque cellule vivante est représentée sous forme de cube / voxel
→ la scène 3D permet d’explorer le système (caméra, zoom, rotation)
l→ a simulation met en valeur le lien entre logique de calcul (automate) et rendu graphique (WebGL)

💡 **Intérêt du projet**

Ce projet est intéressant car il montre comment des règles locales très simples peuvent générer une complexité globale, et il constitue une excellente base pour aller vers des systèmes de simulation plus avancés (écosystèmes, diffusion, comportements collectifs, etc.).

Il est une première approche de la 3D ... qui finalement est peut-être plus facile à rendre responsive et lisible que la 2D.
Car une librairie telle que Three.js possède toutes les features pour rendre agréable la manipulation d'objets.
