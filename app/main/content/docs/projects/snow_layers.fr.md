---
title: Snow Layers · Les hivers des massifs français
summary: Explorer les hauteurs de neige, saison après saison
---

**Snow Layers**, codé avec Codex, explore l’évolution de l’enneigement à travers un catalogue non exhaustif de 46 stations françaises.

### Mode d’emploi
Choisissez une station sur la carte ou dans la liste, puis une saison dans le panneau noir. La courbe rouge représente la hauteur de neige en centimètres ; la bande bleue et sa ligne montrent l’amplitude et la moyenne des autres saisons disponibles. Les points dévoilent leur date et leur valeur au survol ou au focus clavier.

La comparaison affiche les moyennes de décembre à avril de deux stations et les statistiques par altitude : basse montagne (moins de 1 200 m), moyenne montagne (1 200 à 1 800 m), haute montagne (plus de 1 800 m). Les boutons masquent ou affichent chaque série. Une saison partielle ne représente pas un hiver complet ; les stations disponibles varient selon les imports.

### Comprendre les données
Sans données importées, Méribel propose une **démonstration simulée**, explicitement signalée. Les autres stations restent vides. Les données importées viennent de la [réanalyse ERA5-Land distribuée par Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api) : ce sont des hauteurs **modélisées**, pas des relevés de capteurs en station. Les hauteurs horaires en mètres sont converties en centimètres puis moyennées par jour. Coordonnées et altitudes du catalogue sont approximatives.

### Disponibilité
Les séries importées sont conservées dans la base PostgreSQL du portfolio, dans des tables dédiées. La provenance est mutualisée pour limiter le stockage ; les données quotidiennes de décembre à avril restent disponibles. En production, les imports nécessitent un jeton administrateur ; la consultation reste publique. Aucune collecte n’est déclenchée par la simple visite. La carte utilise Leaflet et les fonds OpenStreetMap ; la liste reste utilisable si la carte ne charge pas. L’interface exploratoire est en français ; cette fiche existe aussi en anglais.

### Crédits
Photo alpine d’illustration : [Romain Malaunay, Unsplash](https://unsplash.com/photos/cXrhDuOZBiI), La Plagne-Tarentaise. Elle ne représente pas nécessairement la station sélectionnée. Données : Open-Meteo / ERA5-Land ; cartographie : © OpenStreetMap contributors.
