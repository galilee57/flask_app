---
title: 🐍 Projet – Snake, A* et apprentissage par renforcement
summary: Version Française
---

**Ce projet revisite le jeu Snake avec un plateau isométrique et trois modes de jeu : contrôle humain, recherche de chemin avec A\* et réseau de neurones entraîné par apprentissage par renforcement.**

L’objectif est de manger des fruits pour faire grandir le serpent, tout en évitant les bords et son propre corps. Chaque fruit rapporte un point. Le projet permet d’observer et de comparer deux façons de programmer une intelligence artificielle : calculer un chemin ou apprendre à choisir ses mouvements.

🎮 **Jeu & interface**

Le jeu repose sur une grille de 20 × 20 cases, dessinée en perspective isométrique dans un Canvas JavaScript. Cette perspective change la représentation visuelle, mais la logique reste celle d’une grille à quatre directions.

→ En mode Human, les touches fléchées dirigent le serpent ; des repères autour du plateau indiquent le déplacement correspondant.\
→ Le curseur règle la vitesse de lent à rapide, même pendant la partie. Le mode humain dispose d’une plage plus lente que les IA.\
→ Jouer lance les déplacements, Stop les suspend et Reset démarre une nouvelle partie.\
→ Sur grand écran, le plateau et les contrôles sont côte à côte ; sur petit écran, ils sont empilés.

🧭 **Mode A\* : calculer un chemin**

À chaque déplacement, A\* cherche un chemin vers le fruit en considérant le corps actuel du serpent comme un obstacle.

→ Une file de priorité sélectionne les cases à explorer.\
→ Le coût combine la longueur du chemin parcouru et la distance de Manhattan jusqu’au fruit.\
→ Le premier déplacement du chemin trouvé détermine la direction du serpent.

Cette approche permet de rejoindre le fruit lorsqu’un chemin est disponible. Elle ne simule toutefois pas l’évolution future du corps : un chemin court peut conduire à une situation dont le serpent ne pourra plus sortir.

🧠 **Mode DQN : apprendre par l’expérience**

Le mode DQN utilise un réseau de neurones NumPy avec **11 entrées, 128 neurones cachés et 3 sorties**. Il reçoit les dangers immédiats, la direction du serpent et la position relative du fruit. Il estime ensuite la valeur de trois actions : continuer tout droit, tourner à droite ou tourner à gauche.

L’entraînement se déroule dans des parties indépendantes du jeu affiché :

→ Le serpent explore des actions, puis utilise progressivement davantage les décisions du réseau.\
→ Les expériences sont stockées dans une mémoire et réutilisées par lots.\
→ Double DQN sépare le choix de l’action suivante de son évaluation par un réseau cible.\
→ L’optimiseur Adam ajuste les paramètres du réseau.

Manger un fruit rapporte une récompense de +10 ; une collision vaut −10 et un déplacement ordinaire −0,01. Un signal supplémentaire fondé sur la distance au fruit guide l’apprentissage. Les parties trop longues sans fruit sont interrompues pendant l’entraînement.

Une fois entraîné, le réseau joue sans exploration aléatoire et sans apprendre pendant la partie web. **Le DQN choisit ses propres actions : il n’appelle pas A\* pour se déplacer.**

📊 **Statistiques & limites**

L’option Enregistrer les stats conserve, à chaque fruit mangé, le mode, le score et les compteurs de déplacements. Le graphique compare le nombre moyen de déplacements cumulés pour atteindre un score donné. Les parties d’entraînement n’alimentent pas ce graphique.

L’état fourni au réseau ne décrit pas tout le corps du serpent. Le DQN peut donc encore se retrouver piégé ou effectuer des détours. Ses performances dépendent de l’entraînement et doivent être évaluées sur plusieurs parties.

💡 **Intérêt du projet**

Ce projet associe recherche heuristique, apprentissage par renforcement, gestion d’état côté Flask, rendu Canvas et statistiques. Il permet d’explorer concrètement la différence entre une stratégie calculée à partir de règles explicites et une stratégie apprise à partir d’expériences et de récompenses.
