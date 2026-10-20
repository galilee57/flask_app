---
title: Comprendre GPT from scratch
summary: Un petit modèle de langage codé manuellement avec PyTorch
---

### Un GPT codé manuellement
Ce projet construit un modèle autorégressif caractère par caractère : tokenizer, embeddings, attention causale multi-têtes, connexions résiduelles, normalisation et blocs Transformer. Le moteur du modèle est **codé manuellement** avec PyTorch ; l’intégration au portfolio a été réalisée avec Codex.

### Utilisation
Choisissez un modèle et saisissez un début de texte compatible avec son vocabulaire. Cliquez sur **Générer** : le modèle prolonge le prompt, il ne répond pas nécessairement à une instruction comme un assistant conversationnel. Le prompt apparaît en gris et la continuation en noir. Pour les modèles « char », un token est un caractère ; pour les modèles BPE, il représente un fragment de texte. La longueur est limitée à 500 nouveaux tokens et le prompt à 1 000 caractères.

Une température basse favorise les caractères déjà probables ; une température élevée rend les tirages plus variés. La graine permet de reproduire les tirages dans un même environnement logiciel. Elle ne garantit pas des résultats identiques entre versions ou matériels. Le contexte indique combien de tokens précédents le modèle utilise à chaque prédiction.

### Langues
La langue de l’interface est indépendante de celle du corpus. Les expériences actuelles utilisent du texte français ; des expériences anglaises pourront être ajoutées. Certains vocabulaires ne contiennent ni majuscules ni accents. Les caractères inconnus sont signalés sans modifier silencieusement votre texte.

### Courbes d’entraînement
La courbe bleue représente la perte d’entraînement, la courbe orange la perte de validation. L’axe horizontal compte les mises à jour ; la perte est l’entropie croisée en logarithme naturel. Le point cerclé indique la meilleure évaluation, dont les poids sont utilisés pour générer. Le tableau donne les mesures exactes. Ces données sont enregistrées lors des entraînements locaux ; le site ne lance aucun entraînement.

Une perte plus faible indique une meilleure prédiction sur le texte évalué. Des corpus ou vocabulaires différents ne permettent pas un classement direct. Le corpus généraliste synthétique contient des structures répétées : une faible perte ne prouve pas une capacité générale de raisonnement. Les textes générés peuvent être incohérents ou incorrects.

### Exécution
La génération s’effectue sur le serveur Flask, sur CPU, avec les checkpoints locaux. Les modèles sont chargés à la demande ; un seul est conservé en cache par processus. Le prompt sert uniquement à la génération et n’est pas enregistré par l’application. Aucun service externe de génération n’est appelé.
