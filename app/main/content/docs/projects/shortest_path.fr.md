---
title: Découvrir le plus court chemin
summary: Version française
---

Ce projet adapte le chapitre 2 de **L’intelligence artificielle en pratique avec Python**, de Hugues Bersini et Ken Hasselmann. Il permet de suivre une recherche de chemin dans un graphe non orienté.

### Mode d’emploi
Choisissez un des six graphes du livre (13, 15, 20, 40, 73 ou 244 sommets), un départ, une arrivée et un algorithme. **Lancer** anime la recherche ; **Pause** la suspend ; **Étape suivante** développe un sommet. **Recommencer** remet la recherche à zéro. Modifier un choix prépare une nouvelle recherche. Le délai règle la vitesse d’animation. Le changement d’onglet et l’ouverture de cette fiche suspendent la lecture.

### A\* et Dijkstra
Le coût d’une arête est la distance euclidienne entre ses extrémités. **g** mesure la distance parcourue ; **h** estime la distance restante à vol d’oiseau ; **f = g + h** détermine la priorité de A\*. Dijkstra utilise **h = 0**. Les deux trouvent un chemin de coût minimal ; A\* peut explorer moins de sommets. En cas d’égalité, plusieurs chemins optimaux sont possibles.

### Lire le graphe
Le départ est vert, l’arrivée corail, les sommets à explorer jaunes et les sommets explorés bleus. Le sommet courant est cerclé de blanc. Le chemin final apparaît en blanc, avec son coût et la suite des sommets. Survolez une arête pour lire sa distance. Pour conserver la lisibilité, le graphe de 244 sommets masque les numéros permanents ; les sélecteurs permettent toujours de choisir chaque sommet.

Les distances sont exprimées dans les coordonnées du fichier, pas en kilomètres. Les calculs gardent leur précision et l’affichage arrondit à deux décimales. Un départ identique à l’arrivée produit un coût nul. Une absence de chemin est signalée explicitement.

### Sources et réalisation
Les six jeux de données proviennent du [dépôt AI-book / Shortest_Path](https://github.com/iridia-ulb/AI-book/tree/main/Shortest_Path), © 2021 IRIDIA, ULB, sous licence MIT, conservée avec les données. Le moteur Python et l’interface Flask / SVG sont une nouvelle réalisation **codée avec Codex**. Cette version compare A\* unidirectionnel et Dijkstra ; elle ne traite pas le voyageur de commerce ni la recherche bidirectionnelle. Aucun résultat n’est enregistré et aucun service externe n’est nécessaire à l’exécution.
