---
title: 📝 Projet – Todo App (Stockage local)
summary: Version Française
---

**Ce projet est une application de gestion de tâches (Todo App) conçue pour être simple, rapide et autonome.**

Les données sont enregistrées dans un fichier local, sans base de données externe, ce qui permet une gestion légère et indépendante.

⚙️ **Fonctionnement**

L’application repose sur trois éléments principaux :
→ Structure des données
→ Chaque tâche est représentée par un objet structuré.
→ Persistance locale

Les tâches sont sauvegardées dans un fichier local.

À chaque modification (ajout, suppression, validation), le fichier est mis à jour afin de conserver l’état courant.
Synchronisation interface ↔ fichier

Au chargement, les données sont lues depuis le fichier et injectées dans l’interface.
Les interactions utilisateur modifient ensuite à la fois l’affichage et le stockage.

💡 **Intérêt du projet**

Ce projet, volontairement simple en apparence, permet de travailler des notions fondamentales :
→ gestion d’état
→ CRUD (Create, Read, Update, Delete)
→ sérialisation / désérialisation des données
→ séparation logique métier / interface
→ persistance sans dépendance externe

Il constitue une base solide pour évoluer vers des architectures plus complexes (base de données, API, authentification, synchronisation distante, etc.).
