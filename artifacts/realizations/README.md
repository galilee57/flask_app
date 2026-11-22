# Vérification de la section Projets & réalisations

8 novembre 2026. Captures de l’application Flask en configuration de test, avec une base temporaire ; aucune donnée de production utilisée.

`verification.json` contient les 36 contrôles de rendu : catalogue et deux études, FR/EN, largeurs 320, 390, 640, 768, 1024 et 1280 px. Aucun débordement horizontal, média manquant ou ancre cassée ; un H1 par page. Aucune erreur JavaScript.

Interactions vérifiées dans Chromium : sélection, tous, professionnels, thèmes, recherche, état vide, remise à zéro, critères conservés au rechargement, ouverture et fermeture de la fiche d’information. Les critères fonctionnent également sans JavaScript via le formulaire GET. Au clavier, le focus reste dans la fiche ouverte ; Échap la ferme et rend le focus au bouton d’ouverture.

Suite Pytest : 201 tests réussis. Le bundle Tailwind commun est reconstruit. Les fichiers des deux polices du thème, auparavant manquants, sont présents avec leurs licences OFL.

Les captures `*-390.jpg` et `*-1280.jpg` montrent les versions mobile et bureau françaises. La barre de navigation fixe peut apparaître au milieu d’une capture pleine page mobile, car sa position correspond au bas de la fenêtre visible lors de la capture.

Commandes de validation :

```sh
npm run build:css
.venv/bin/pytest -q
git diff --check
```

Les textes modifiables sont décrits dans `app/main/content/docs/realizations/README.md`. Le catalogue recense 17 sujets personnels, 32 dossiers professionnels historiques et 6 sujets numériques professionnels. Seules les deux études relues possèdent un lien vers une page détaillée.

## Mise en attente de la refonte

À la demande de l’utilisateur, les anciennes pages restent l’entrée PRO. La nouvelle version illustrée par ces captures est désormais accessible uniquement par le lien « Aperçu projets » du bandeau admin, avec une session valide. Les études et leurs médias sont protégés de la même manière. Validation après ce changement : 88 tests ciblés réussis.

## État au 22 novembre 2026

Les captures et chiffres ci-dessus décrivent les étapes historiques. Le catalogue actuel contient 84 projets, dont 80 études détaillées, et 336 sources Markdown (versions longues et courtes en français et en anglais). Le tag `display_version` de la fiche française pilote les deux langues. La navigation PRO historique est conservée et l’aperçu reste réservé à la session admin.

Les six illustrations manquantes ont été ajoutées avec leurs briefs et leur provenance. Les galeries sans photographie ou illustration raster supplémentaire sont masquées. Les quatre boutons de sélection ont été retirés ; la recherche et le thème restent disponibles, avec des contrôles de même hauteur (48 px), vérifiés dans Chromium sur mobile, tablette et bureau en FR/EN. WebKit automatisé n’est pas installé dans cet environnement.

Validation avant commit : 229 tests Pytest réussis et compilation Tailwind réussie. Le contrôle du contenu nouvellement ajouté signale des espaces et lignes finales dans les sources Markdown relues ; leur mise en forme éditoriale est conservée. Les captures de contrôles antérieurs restent conservées pour référence.
