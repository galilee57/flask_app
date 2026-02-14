---
title: 🌍 Projet – Flags Game (API Countries)
summary: Version Française
---

**Ce projet est un jeu interactif consistant à associer des drapeaux au nom du pays.**
L’objectif est simple : déplacer chaque drapeau vers la bonne zone.

La particularité du projet est l’utilisation d’une API externe pour récupérer dynamiquement les informations pays (nom, drapeau, région, capitale, etc.).

⚙️ **Fonctionnement technique**

Récupération des données via API
→ Les informations sur les pays sont obtenues dynamiquement via une API publique (type REST Countries).
→ Cela permet d’éviter un stockage local statique et garantit des données structurées et normalisées.

Génération dynamique des éléments
→ Les drapeaux sont générés à partir des données reçues (URL d’image du drapeau).
→ Les zones cibles correspondent aux régions ou catégories définies dans la réponse API.

Interaction Drag & Drop
→ Le joueur déplace les drapeaux vers une zone.
→ Une vérification logique compare la région réelle du pays avec la zone choisie.

Validation & feedback
→ Si la correspondance est correcte → validation visuelle / score.
→ Sinon → retour utilisateur (erreur, repositionnement, tentative suivante).

💡 **Intérêt du projet**

Ce projet met en valeur :
→ l’intégration d’une API REST
→ la manipulation de données JSON
→ la génération dynamique d’interface
→ la gestion d’événements (drag & drop)
→ la séparation entre données externes et logique applicative.

Il combine ainsi jeu éducatif, interaction utilisateur et exploitation de données en temps réel.
