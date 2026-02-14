---
title: 🧠 Projet – Memory Game (CSS + JavaScript)
summary: Version Française
---

**Ce projet est un jeu de Memory (jeu de paires) développé à partir d’une formation Domestika, que j’ai utilisé comme base pour pratiquer à la fois la logique de jeu et l’intégration front.**

⚙️ **Fonctionnement**

Le principe est simple : retourner deux cartes, vérifier si elles correspondent, puis soit les verrouiller (paire trouvée), soit les retourner à nouveau après un court délai.

Le code met en place :
→ une gestion d’état claire (cartes retournées, paires validées, blocage temporaire des clics)
→ une logique de comparaison des cartes (id, dataset, ou valeur)
→ un mélange des cartes au lancement pour rendre chaque partie différente
→ un système de progression (nombre de coups / temps / score, selon l’implémentation)

🎨 **Intégration & CSS**

Ce projet m’a permis de travailler :
→ la mise en page responsive
→ les transitions / animations CSS (flip de carte, effets visuels)
→ des interactions simples mais propres côté UI (retours visuels, états correct/incorrect)

💡 **Intérêt du projet**

Même si le jeu est accessible, il est très formateur : il combine DOM, événements, états, timing (setTimeout) et styling.
C’est un bon exercice pour consolider des bases solides en front avant d’aller vers des projets plus complexes.
