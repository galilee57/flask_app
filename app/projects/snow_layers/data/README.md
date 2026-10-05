# Historique météo public

Export JSON Lines compressé de la copie normalisée décembre–avril, 46 stations,
528 770 observations. Source : Open-Meteo Archive / ERA5-Land.
Licence des données : CC BY 4.0 — https://open-meteo.com/en/licence
Les moyennes journalières en centimètres dérivent des hauteurs horaires modélisées.
Période : décembre 1950 à avril 2026, décembre–avril uniquement.
Chaque lot de provenance conserve la requête source et la date de collecte.
Le catalogue est approximatif et non exhaustif. Pas de données personnelles,
secrets, sessions ni copie de la base applicative dans cet export.

L’empreinte et les comptes attendus sont dans manifest.json. Le déploiement
exécute `flask --app wsgi snow-seed` après les migrations. Une table de suivi
empêche les réimports après une première importation réussie.
