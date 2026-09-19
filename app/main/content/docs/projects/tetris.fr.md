---
title: 🧩 Projet – Tétris et intelligence artificielle explicable
summary: Version Française
---

**Ce projet revisite Tétris pour observer comment une intelligence artificielle choisit ses placements. Deux modes sont disponibles : humain et IA heuristique. Un réseau neuronal sera développé par la suite.**

L’objectif est de compléter des lignes horizontales avec les sept types de pièces. Les lignes pleines disparaissent et libèrent de la place. La partie se termine lorsqu’une nouvelle pièce ne peut plus apparaître.

🎮 **Jeu & interface**

Le plateau de 10 colonnes × 20 lignes est dessiné dans un Canvas JavaScript. Les pièces sont tirées par sacs de sept : chaque type apparaît une fois avant le renouvellement du sac. Un aperçu présente la prochaine pièce et une projection indique où tomberait la pièce courante.

→ Les flèches gauche et droite déplacent la pièce ; la flèche haut la tourne dans le sens horaire.
→ La flèche bas accélère la descente ; Espace pose immédiatement la pièce.
→ Jouer démarre la partie, Pause la suspend, Reprendre la continue et Recommencer remet le plateau à zéro. La touche P permet aussi de mettre en pause.
→ Des boutons tactiles permettent de jouer sans clavier. Changer de mode commence une nouvelle partie.
→ Masquer l’onglet ou ouvrir cette fiche met une partie en cours en pause.

🧭 **Mode IA : comparer des placements**

L’IA actuelle utilise des règles explicites, sans apprentissage ni réseau neuronal. Elle simule les rotations et déplacements horizontaux possibles avant la descente, puis évalue chaque placement distinct. Les critères sont calculés après suppression des lignes complètes :

→ **Lignes** : nombre de lignes complétées par cette pièce.
→ **Hauteur totale** : somme des hauteurs des dix colonnes.
→ **Trous** : nombre de cases vides situées sous un bloc.
→ **Relief** : somme des différences de hauteur entre colonnes voisines.

La valeur d’un placement est **8 × lignes − 0,5 × hauteur totale − 7 × trous − 0,3 × relief**. Une fin de partie ajoute une pénalité de **10 000**. L’IA choisit la valeur la plus élevée ; en cas d’égalité, elle conserve le premier placement exploré. Cette valeur d’évaluation est distincte du score de la partie.

🔎 **Observer les décisions**

Le panneau montre les trois meilleurs placements, leurs critères et leurs valeurs. « Col. » indique la colonne gauche occupée, de 1 à 10 ; « ↻ » indique le nombre de rotations. Une cible en pointillés matérialise le placement retenu sur le plateau.

L’IA laisse un temps de lecture, effectue ses rotations et déplacements, puis descend case par case. Le mode **Avancer manuellement** suspend la progression automatique : chaque clic sur **Étape suivante** affiche une décision ou exécute une action, y compris pendant la pause.

⏱️ **Vitesses indépendantes**

Le curseur humain règle la chute automatique entre 800 et 80 millisecondes par case. Le curseur IA règle les actions entre 2 et 0,2 secondes, avec 1,6 seconde par défaut. Le choix et son résultat restent affichés pendant trois intervalles. Les deux réglages sont conservés séparément pendant la session de la page.

📊 **Scores & records**

Compléter 1, 2, 3 ou 4 lignes rapporte respectivement **100, 300, 500 ou 800 points**. La descente manuelle rapporte 1 point par case et la chute immédiate 2 points par case. La descente animée de l’IA conserve ce barème de 2 points. La vitesse ne multiplie pas les points.

Les records humain et IA sont distincts et stockés dans le navigateur. Ils ne sont pas envoyés à un serveur. Si le stockage local est indisponible, le record reste disponible uniquement pendant la session de la page.

🧠 **Limites & futur réseau neuronal**

L’heuristique évalue la pièce courante sans anticiper une suite de pièces ; elle peut donc faire un choix localement favorable qui compromet la suite. Elle ne recherche pas tous les mouvements possibles sous les blocs. Les rotations utilisent des corrections horizontales simples, sans système SRS complet ni délai de verrouillage.

Le moteur est indépendant de l’interface. Une interface d’agent est prête à recevoir la politique du futur réseau neuronal. Pour un agent personnalisé, les actions peuvent être animées, mais aucun critère de décision n’est présenté comme une explication sans données fournies par cet agent.

💡 **Intérêt du projet**

Le projet associe simulation, recherche heuristique, rendu Canvas, Tailwind CSS 4 et contenu bilingue Flask. Son objectif pédagogique est de rendre les décisions observables et de préparer une comparaison entre des règles explicites et une stratégie apprise.
