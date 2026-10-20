---
title: Équilibre · Proies et prédateurs
summary: Version française
---

Une simulation à agents dans une prairie fermée : les lapins consomment la végétation, les prédateurs chassent et les plantes repoussent. Chaque animal dispose de son énergie et de son comportement. Ce modèle pédagogique illustre des équilibres émergents ; il ne prédit pas un écosystème réel et n’utilise pas d’apprentissage automatique.

### Explorer la prairie
La simulation démarre automatiquement. **Pause** suspend le temps, **Un pas** avance d’une étape et le sélecteur règle la vitesse. Touchez un animal pour inspecter son âge, son énergie et son comportement. Glissez sur la prairie pour déplacer la caméra ; utilisez la molette pour zoomer et **Vue globale** pour retrouver le cadrage initial. Le changement d’onglet met la simulation en pause.

### Construire une expérience
Réglez les populations initiales, la végétation, le nombre de terriers et leur capacité, puis choisissez une graine et cliquez sur **Recommencer l’expérience**. À graine et actions identiques, l’expérience est reproductible. Les vitesses, la repousse et la dépense énergétique changent immédiatement ; vous pouvez aussi ajouter des animaux, afficher les trajectoires et la perception de l’animal sélectionné. La population est limitée à 650 individus.

### Comprendre les refuges
Les terriers ont des capacités réglables individuellement, sans expulser les occupants. Les lapins abrités restent comptés parmi les proies et dépensent de l’énergie. Ils ressortent quand leur énergie atteint 45 points ou que le danger s’éloigne. La reproduction consomme de l’énergie ; faim, prédation et vieillesse peuvent conduire à l’extinction.

### Lire et exporter les résultats
Le graphique présente proies, prédateurs, végétation disponible et lapins abrités. Masquez des séries, suivez les dernières minutes ou fixez une période avec les curseurs. L’historique conserve les 3 600 dernières secondes simulées. **CSV** exporte cet historique avec des colonnes stables en anglais. Tout s’exécute dans le navigateur, sans sauvegarde serveur ; recharger la page recommence l’expérience.

### Réalisation
Simulation en TypeScript et Canvas, intégrée à Flask avec une interface responsive et des textes français/anglais. Codé avec Codex.
