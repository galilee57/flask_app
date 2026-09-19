"""Browser messages selected by the shared Jinja t() language helper."""

MESSAGES = {'fr': {'1 · Comparaison et choix du placement': '1 · Comparaison et choix du placement',
        '2 · Déplacement à droite': '2 · Déplacement à droite',
        '2 · Déplacement à gauche': '2 · Déplacement à gauche',
        '2 · Rotation horaire': '2 · Rotation horaire',
        '3 · Descente vers la cible': '3 · Descente vers la cible',
        '4 · Pièce posée, résultat du choix': '4 · Pièce posée, résultat du choix',
        'Agent indisponible : vérifie sa politique avant de reprendre.': 'Agent indisponible : '
                                                                         'vérifie sa politique '
                                                                         'avant de reprendre.',
        'Agent personnalisé': 'Agent personnalisé',
        'Agent personnalisé : actions affichées, critères de décision non fournis.': 'Agent '
                                                                                     'personnalisé '
                                                                                     ': actions '
                                                                                     'affichées, '
                                                                                     'critères de '
                                                                                     'décision non '
                                                                                     'fournis.',
        'Appuie sur Jouer pour commencer': 'Appuie sur Jouer pour commencer',
        'Appuie sur Reprendre pour continuer': 'Appuie sur Reprendre pour continuer',
        'Clavier ou boutons tactiles. Changer de mode remet la partie à zéro.': 'Clavier ou '
                                                                                'boutons tactiles. '
                                                                                'Changer de mode '
                                                                                'remet la partie à '
                                                                                'zéro.',
        'En attente d’une pièce.': 'En attente d’une pièce.',
        'En jeu': 'En jeu',
        'Heuristique de démonstration': 'Heuristique de démonstration',
        'Jouer': 'Jouer',
        'La machine est prête': 'La machine est prête',
        'La politique doit être une fonction.': 'La politique doit être une fonction.',
        'L’IA compare les placements possibles avant de déplacer la pièce.': 'L’IA compare les '
                                                                             'placements possibles '
                                                                             'avant de déplacer la '
                                                                             'pièce.',
        'Mode IA': 'Mode IA',
        'Mode changé. Prêt à jouer.': 'Mode changé. Prêt à jouer.',
        'Mode humain': 'Mode humain',
        'Nouvelle partie.': 'Nouvelle partie.',
        'On fait une pause': 'On fait une pause',
        'Partie en cours.': 'Partie en cours.',
        'Partie en pause.': 'Partie en pause.',
        'Partie terminée': 'Partie terminée',
        'Partie terminée : {score} points, {lines} lignes.': 'Partie terminée : {score} points, '
                                                             '{lines} lignes.',
        'Pause': 'Pause',
        'Pause automatique : onglet masqué.': 'Pause automatique : onglet masqué.',
        'Placement terminé': 'Placement terminé',
        'Prochaine pièce : {piece}': 'Prochaine pièce : {piece}',
        'Prêt': 'Prêt',
        'Rejouer': 'Rejouer',
        'Reprendre': 'Reprendre',
        'Règle la chute automatique des pièces. Le réglage IA est conservé séparément.': 'Règle la '
                                                                                         'chute '
                                                                                         'automatique '
                                                                                         'des '
                                                                                         'pièces. '
                                                                                         'Le '
                                                                                         'réglage '
                                                                                         'IA est '
                                                                                         'conservé '
                                                                                         'séparément.',
        'Terminé': 'Terminé',
        'Un réglage indépendant : 2 s à 0,2 s par action. Le temps de lecture du choix est trois fois plus long.': 'Un '
                                                                                                                   'réglage '
                                                                                                                   'indépendant '
                                                                                                                   ': '
                                                                                                                   '2 '
                                                                                                                   's '
                                                                                                                   'à '
                                                                                                                   '0,2 '
                                                                                                                   's '
                                                                                                                   'par '
                                                                                                                   'action. '
                                                                                                                   'Le '
                                                                                                                   'temps '
                                                                                                                   'de '
                                                                                                                   'lecture '
                                                                                                                   'du '
                                                                                                                   'choix '
                                                                                                                   'est '
                                                                                                                   'trois '
                                                                                                                   'fois '
                                                                                                                   'plus '
                                                                                                                   'long.',
        'Vitesse IA': 'Vitesse IA',
        'Vitesse humain': 'Vitesse humain',
        '{agent}. Le réseau neuronal sera ajouté ultérieurement. Changer de mode remet la partie à zéro.': '{agent}. '
                                                                                                           'Le '
                                                                                                           'réseau '
                                                                                                           'neuronal '
                                                                                                           'sera '
                                                                                                           'ajouté '
                                                                                                           'ultérieurement. '
                                                                                                           'Changer '
                                                                                                           'de '
                                                                                                           'mode '
                                                                                                           'remet '
                                                                                                           'la '
                                                                                                           'partie '
                                                                                                           'à '
                                                                                                           'zéro.',
        '{count} placements distincts comparés. Choix : colonne {column}, {turns} rotation(s), valeur {value}. {lines} ligne(s), {holes} trou(s), hauteur totale {height}, relief {roughness}.': '{count} '
                                                                                                                                                                                                 'placements '
                                                                                                                                                                                                 'distincts '
                                                                                                                                                                                                 'comparés. '
                                                                                                                                                                                                 'Choix '
                                                                                                                                                                                                 ': '
                                                                                                                                                                                                 'colonne '
                                                                                                                                                                                                 '{column}, '
                                                                                                                                                                                                 '{turns} '
                                                                                                                                                                                                 'rotation(s), '
                                                                                                                                                                                                 'valeur '
                                                                                                                                                                                                 '{value}. '
                                                                                                                                                                                                 '{lines} '
                                                                                                                                                                                                 'ligne(s), '
                                                                                                                                                                                                 '{holes} '
                                                                                                                                                                                                 'trou(s), '
                                                                                                                                                                                                 'hauteur '
                                                                                                                                                                                                 'totale '
                                                                                                                                                                                                 '{height}, '
                                                                                                                                                                                                 'relief '
                                                                                                                                                                                                 '{roughness}.',
        '{score} points · Rejouer pour réessayer': '{score} points · Rejouer pour réessayer',
        '{seconds} s / étape': '{seconds} s / étape',
        'À toi de jouer': 'À toi de jouer'},
 'en': {'1 · Comparaison et choix du placement': '1 · Compare and choose a placement',
        '2 · Déplacement à droite': '2 · Move right',
        '2 · Déplacement à gauche': '2 · Move left',
        '2 · Rotation horaire': '2 · Rotate clockwise',
        '3 · Descente vers la cible': '3 · Descend towards the target',
        '4 · Pièce posée, résultat du choix': '4 · Piece locked, decision outcome',
        'Agent indisponible : vérifie sa politique avant de reprendre.': 'Agent unavailable: check '
                                                                         'its policy before '
                                                                         'resuming.',
        'Agent personnalisé': 'Custom agent',
        'Agent personnalisé : actions affichées, critères de décision non fournis.': 'Custom '
                                                                                     'agent: '
                                                                                     'actions '
                                                                                     'shown, '
                                                                                     'decision '
                                                                                     'metrics not '
                                                                                     'provided.',
        'Appuie sur Jouer pour commencer': 'Press Play to start',
        'Appuie sur Reprendre pour continuer': 'Press Resume to continue',
        'Clavier ou boutons tactiles. Changer de mode remet la partie à zéro.': 'Use the keyboard '
                                                                                'or touch '
                                                                                'controls. '
                                                                                'Changing mode '
                                                                                'resets the game.',
        'En attente d’une pièce.': 'Waiting for a piece.',
        'En jeu': 'Playing',
        'Heuristique de démonstration': 'Demo heuristic',
        'Jouer': 'Play',
        'La machine est prête': 'The machine is ready',
        'La politique doit être une fonction.': 'The policy must be a function.',
        'L’IA compare les placements possibles avant de déplacer la pièce.': 'The AI compares '
                                                                             'possible placements '
                                                                             'before moving the '
                                                                             'piece.',
        'Mode IA': 'AI mode',
        'Mode changé. Prêt à jouer.': 'Mode changed. Ready to play.',
        'Mode humain': 'Human mode',
        'Nouvelle partie.': 'New game.',
        'On fait une pause': 'Taking a break',
        'Partie en cours.': 'Game in progress.',
        'Partie en pause.': 'Game paused.',
        'Partie terminée': 'Game over',
        'Partie terminée : {score} points, {lines} lignes.': 'Game over: {score} points, {lines} '
                                                             'lines.',
        'Pause': 'Pause',
        'Pause automatique : onglet masqué.': 'Automatically paused: tab hidden.',
        'Placement terminé': 'Placement complete',
        'Prochaine pièce : {piece}': 'Next piece: {piece}',
        'Prêt': 'Ready',
        'Rejouer': 'Play again',
        'Reprendre': 'Resume',
        'Règle la chute automatique des pièces. Le réglage IA est conservé séparément.': 'Controls '
                                                                                         'automatic '
                                                                                         'piece '
                                                                                         'descent. '
                                                                                         'The AI '
                                                                                         'setting '
                                                                                         'is kept '
                                                                                         'separately.',
        'Terminé': 'Finished',
        'Un réglage indépendant : 2 s à 0,2 s par action. Le temps de lecture du choix est trois fois plus long.': 'An '
                                                                                                                   'independent '
                                                                                                                   'setting: '
                                                                                                                   '2 '
                                                                                                                   's '
                                                                                                                   'to '
                                                                                                                   '0.2 '
                                                                                                                   's '
                                                                                                                   'per '
                                                                                                                   'action. '
                                                                                                                   'Decisions '
                                                                                                                   'stay '
                                                                                                                   'visible '
                                                                                                                   'three '
                                                                                                                   'times '
                                                                                                                   'longer.',
        'Vitesse IA': 'AI speed',
        'Vitesse humain': 'Human speed',
        '{agent}. Le réseau neuronal sera ajouté ultérieurement. Changer de mode remet la partie à zéro.': '{agent}. '
                                                                                                           'A '
                                                                                                           'neural '
                                                                                                           'network '
                                                                                                           'will '
                                                                                                           'be '
                                                                                                           'added '
                                                                                                           'later. '
                                                                                                           'Changing '
                                                                                                           'mode '
                                                                                                           'resets '
                                                                                                           'the '
                                                                                                           'game.',
        '{count} placements distincts comparés. Choix : colonne {column}, {turns} rotation(s), valeur {value}. {lines} ligne(s), {holes} trou(s), hauteur totale {height}, relief {roughness}.': '{count} '
                                                                                                                                                                                                 'distinct '
                                                                                                                                                                                                 'placements '
                                                                                                                                                                                                 'compared. '
                                                                                                                                                                                                 'Choice: '
                                                                                                                                                                                                 'column '
                                                                                                                                                                                                 '{column}, '
                                                                                                                                                                                                 '{turns} '
                                                                                                                                                                                                 'rotation(s), '
                                                                                                                                                                                                 'value '
                                                                                                                                                                                                 '{value}. '
                                                                                                                                                                                                 '{lines} '
                                                                                                                                                                                                 'line(s), '
                                                                                                                                                                                                 '{holes} '
                                                                                                                                                                                                 'hole(s), '
                                                                                                                                                                                                 'total '
                                                                                                                                                                                                 'height '
                                                                                                                                                                                                 '{height}, '
                                                                                                                                                                                                 'bumpiness '
                                                                                                                                                                                                 '{roughness}.',
        '{score} points · Rejouer pour réessayer': '{score} points · Play again to retry',
        '{seconds} s / étape': '{seconds} s / step',
        'À toi de jouer': 'Your turn'}}
