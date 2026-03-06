---
title: Viewer 360 avec Marzipano
summary: Version Française
---

Cette application permet d’explorer des images panoramiques à 360° de manière interactive à l’aide de la bibliothèque JavaScript Marzipano.

Marzipano est un moteur de visualisation panoramique performant basé sur WebGL, conçu pour afficher des panoramas haute résolution directement dans le navigateur. Il utilise un système de tuilage d’images (multi-resolution tiles) qui permet de charger uniquement les parties de l’image nécessaires selon le niveau de zoom et l’orientation de la vue, ce qui améliore fortement les performances.

Architecture du projet
L’application combine plusieurs technologies :
• Flask pour servir l’application web et les ressources.
• JavaScript pour piloter le chargement et l’affichage des panoramas.
• Marzipano pour le rendu interactif des panoramas dans le navigateur.
• Tailwind CSS pour la mise en forme de l’interface.

Fonctionnement 1. Les panoramas sont stockés sous forme d’images multi-résolution découpées en tuiles. 2. Lorsqu’un panorama est sélectionné, l’application initialise une scène Marzipano dans le conteneur d’affichage. 3. Le moteur charge dynamiquement les tuiles nécessaires selon :
• l’orientation de la caméra,
• le niveau de zoom,
• la taille de la fenêtre d’affichage. 4. L’utilisateur peut naviguer dans le panorama grâce aux interactions souris ou tactiles.

Objectif
Ce projet démontre comment intégrer un visualiseur panoramique 360° performant dans une application web, avec une interface simple permettant de sélectionner et parcourir différents panoramas.
