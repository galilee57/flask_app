# Proposition — Projets & réalisations

8 novembre 2026 · Proposition éditoriale et de navigation, sans modification des pages Flask.

## Direction proposée

Remplacer l’entrée « Pro » et les six grandes tuiles par « Projets & réalisations » : une sélection visuelle, puis un catalogue filtrable. Les domaines deviennent des filtres ; les réalisations deviennent le point d’entrée.

Le fil conducteur : **comprendre un problème, construire une solution et la faire fonctionner**. Le parcours industriel apporte l’expérience des systèmes réels, des contraintes et des équipes ; les projets personnels rendent visibles la pratique technique, l’apprentissage et la réalisation.

La section [Projects de Sreekar Reddy](https://sreekarreddy.com/portfolio#projects) fournit un modèle utile : sélection mise en avant, filtres, couverture, résumé, points saillants, outils et accès au détail. L’adaptation conserve la palette bordeaux et vert pâle, les polices EB Garamond et Roboto et les composants partagés du portfolio Flask. Les photographies des réalisations prennent la place des images génériques de domaines.

## Proposition d’écran

```text
PROJETS & RÉALISATIONS
De l’industrie aux applications, concevoir et faire fonctionner des solutions.

[Sélection] [Tous] [Professionnels] [Personnels]

[Industrie & exploitation] [Données & IA] [Applications & automatisation]
[Conception & fabrication] [Image & acquisition] [Transmission & apprentissage]

┌─────────────────────────────┐  ┌─────────────────────────────┐
│ Photos Jupiter / Saturne    │  │ Photo de la presse 3D       │
│ Personnel · Image           │  │ Personnel · Fabrication     │
│ De l’observation aux        │  │ De l’imprimante en kit à la  │
│ images planétaires         │  │ fabrication de pièces       │
│ Démarche et réalisation    │  │ Démarche et réalisation      │
│ Outils · Lire l’étude →     │  │ Outils · Lire l’étude →      │
└─────────────────────────────┘  └─────────────────────────────┘

EXPLORER LES AUTRES RÉALISATIONS
Cartes des projets retenus, recherche et filtres

PARCOURS PROFESSIONNEL → chronologie et responsabilités
```

La sélection s’ouvre pour le moment sur les deux études relues. Elle pourra ensuite accueillir quatre autres cas, pour atteindre six cartes : un cas industriel, un cas données/IA, une application et un cas d’automatisation ou de transmission. Cette composition est une recommandation ; ces quatre études ne sont pas annoncées comme déjà relues.

## Les deux cartes immédiatement exploitables

### De l’observation aux images planétaires

**Personnel · Image & acquisition · Conception & fabrication**

Choisir un équipement évolutif, adapter sa mécanique et relier la capture vidéo au traitement d’images.

- Adaptation de la transmission de la monture avec un kit à poulies et courroies.
- Acquisition et traitement d’images planétaires avec FireCapture et Siril.

Visuel : les photographies de Jupiter et Saturne déjà présentes dans l’étude, sans agrandissement excessif. Outils visibles : HEQ-5 Pro, kit Rowan, FireCapture, Siril.

[Lire l’étude — maquette relue](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP001_astronomie_astrophotographie/maquettes/2026-11-08-flask/index.html>) · [Source éditoriale](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP001_astronomie_astrophotographie/maquettes/2026-11-08-flask/etude-de-cas.md>)

### De l’imprimante en kit à la fabrication de pièces

**Personnel · Conception & fabrication**

Relier montage, conception et préparation d’impression dans une pratique personnelle de fabrication 3D.

- Montage d’une imprimante Ultimaker livrée en kit.
- Conception, préparation et impression de pièces.

Visuel : la photographie de la presse ; l’Ultimaker et la sculpture restent dans la galerie de l’étude. Outils visibles : Ultimaker, FreeCAD, Cura. Le texte des études reste celui des Markdown relus ; ces résumés servent uniquement aux cartes d’entrée.

[Lire l’étude — maquette relue](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP002_impression-3d/maquettes/2026-11-08-flask/index.html>) · [Source éditoriale](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP002_impression-3d/maquettes/2026-11-08-flask/etude-de-cas.md>)

## Donner une place cohérente aux autres projets

| Entrée | Projets professionnels | Projets personnels | Ce que le rapprochement rend lisible |
|---|---|---|---|
| Industrie & exploitation | Arrêts, maintenance, production, intégration d’unité, investissements | Rénovation maison, VTT | Organisation, contraintes physiques et décisions techniques |
| Données & IA | Études process, ML, vision, Power BI, PySpark | Flint, agents Python, bibliothèque et perspective RAG | Passage des données à un outil utilisable |
| Applications & automatisation | Applications Flask, flux Power Automate, intégrations | Applications web, App Store, portfolio | Besoin utilisateur, développement et mise en service |
| Conception & fabrication | Mécanique, équipements, essais et diagnostic | Impression 3D, fablab, Raspberry/Arduino, adaptation de la monture | Choix techniques, assemblage et expérimentation |
| Image & acquisition | Vision et classification d’images | Astronomie, photo/vidéo/360°, drone et VR | Acquisition, traitement et restitution |
| Transmission & apprentissage | Formation, facteurs humains, accompagnement et management | Articles, psychologie, musique, apprentissages sportifs | Explication, progression et compréhension des usages |

Un projet peut porter deux thèmes. Le badge « Professionnel » ou « Personnel » reste distinct : les rapprochements expliquent une démarche commune sans confondre les contextes. Musique, sport et psychologie trouveraient plutôt leur place dans une section secondaire « Explorations & apprentissages », accessible depuis le catalogue et la page À propos.

Les réalisations numériques de la liste actuelle `app/main/content/list_projects.fr.txt` complètent l’inventaire historique : études process/ML, Power BI/SPC, Power Automate, PySpark/Kafka/Data Warehouse, vision et applications Flask (conversion, heatmaps, graphes de risques, graphiques process). Avant de créer de nouvelles cartes, rapprocher ces sujets des dossiers existants pour éviter les doublons. Les pages actuelles par domaine peuvent rester accessibles depuis les filtres ou comme ressources complémentaires.

## Les prochaines études à mettre en avant

1. Un cas industriel : préparation d’arrêts (P006) ou analyse charge/capacité (P028), selon le récit retenu.
2. Un cas données/IA : une étude process ou vision issue de la liste professionnelle actuelle.
3. Une application : YouTube-to-Obsidian dans PP006, en distinguant son histoire des autres applications du même dossier.
4. Un cas agent ou automatisation : Flint (PP015), ou un flux professionnel Power Automate.

Une sélection finale de six cas rendrait alors visibles : industrie, données, logiciel, agents/automatisation, acquisition d’images et fabrication. L’ordre pourra être ajusté selon le poste visé.

## Règles de présentation

- Une carte = visuel, origine, titre concret, résumé court, deux points saillants, trois ou quatre outils et un lien explicite.
- Éviter les listes de technologies sans réalisation associée. Les chiffres sont affichés uniquement lorsqu’ils sont retenus dans l’étude correspondante.
- Vue mobile : une colonne et filtres sur plusieurs lignes ; tablette : deux colonnes ; grand écran : trois. Les deux premières cartes peuvent être plus généreuses en grand écran.
- Filtres d’origine et de thème combinables, compteur des résultats et remise à zéro ; état vide explicite. Tous les contrôles utilisables au clavier et au toucher.
- Le catalogue public contient les projets sélectionnés pour diffusion. L’inventaire de travail ci-dessous contient tous les dossiers ; son effectif n’est pas un compteur de projets livrés.
- Pour les dossiers non relus : titres dans cet inventaire de travail, sans faux bouton « Lire l’étude » dans la sélection publique. Les deux liens actifs de cette proposition ciblent les maquettes relues.
- Les futures pages FR/EN reprennent les composants `hero`, `button`, `info_modal`, les tokens et le bundle Tailwind commun. Les études anglaises doivent être traduites avant d’y proposer un accès en anglais.
- Dans les études : un renvoi « Tous les projets » et deux ou trois projets liés. Astronomie → photo/vidéo, fabrication ; impression 3D → fablab, électronique.

## Inventaire utilisé — 17 projets personnels

Les liens de cette liste ouvrent les cadrages de travail. Les deux accès aux maquettes relues figurent plus haut.

| ID | Projet | Dossier source |
|---|---|---|
| PP001 | Astronomie et photographie astronomique | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP001_astronomie_astrophotographie/PP001_cadrage.md>) |
| PP002 | Impression 3D : Ultimaker et conception de pièces | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP002_impression-3d/PP002_cadrage.md>) |
| PP003 | Fablab : formation, drone et fabrication d’objets | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP003_fablab-drone-fabrication/PP003_cadrage.md>) |
| PP004 | Rénovation complète de la maison et aménagement intérieur | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP004_renovation-maison/PP004_cadrage.md>) |
| PP005 | Applications publiées sur l’App Store avec Codex | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP005_applications-appstore-codex/PP005_cadrage.md>) |
| PP006 | Applications web : YouTube-to-Obsidian, tri de photos et autres | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP006_applications-web/PP006_cadrage.md>) |
| PP007 | Portfolio Flask et déploiements | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP007_portfolio-flask-deploiement/PP007_cadrage.md>) |
| PP008 | Rénovation complète et réglages d’un VTT | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP008_renovation-vtt/PP008_cadrage.md>) |
| PP009 | Photo et vidéo : prises de vue, montage, YouTube et VR | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP009_photographie-360-drone-vr/PP009_cadrage.md>) |
| PP010 | Musculation, discipline et apprentissages en alimentation | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP010_musculation-alimentation/PP010_cadrage.md>) |
| PP011 | Numérisation de la bibliothèque et perspective de RAG | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP011_bibliotheque-numerique-rag/PP011_cadrage.md>) |
| PP012 | Musique : piano et guitare | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP012_musique-piano-guitare/PP012_cadrage.md>) |
| PP013 | Raspberry et Arduino : maison et expérimentations IoT | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP013_raspberry-arduino-iot/PP013_cadrage.md>) |
| PP014 | Études de psychologie | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP014_etudes-psychologie/PP014_cadrage.md>) |
| PP015 | Harness Flint avec LLM local et Ollama | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP015_harness-flint-llm-local/PP015_cadrage.md>) |
| PP016 | Agents en Python pur et application de conseil financier | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP016_agents-python-conseil-financier/PP016_cadrage.md>) |
| PP017 | Publication d’articles sur Medium | [Cadrage](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-personnels/PP017_articles-medium/PP017_cadrage.md>) |

## Inventaire utilisé — 32 dossiers professionnels

Ces dossiers décomposent les 25 sujets du catalogue professionnel. Les titres ci-dessous sont les périmètres de l’index de travail, pas des intitulés définitifs de cartes publiques.

| ID | Périmètre | Dossier source |
|---|---|---|
| P013 | Calibrage / R&D — test précédent conservé | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P013_descentes_laminage/P013_collecte.md>) |
| P014 | Préparer la logistique d’un arrêt industriel | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P014_logistique_arret/P014_collecte.md>) |
| P015 | Chantier de nettoyage d’échangeurs — dossier à étayer | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P015_nettoyage_echangeurs/P015_collecte.md>) |
| P016 | Contribuer au suivi en continu de machines tournantes | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P016_suivi_vibratoire/P016_collecte.md>) |
| P017 | Tenir un rôle au poste de commandement lors d’un exercice | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P017_exercice_poi/P017_collecte.md>) |
| P018 | Recette de machines — expérience déclarée à documenter | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P018_recette_machines/P018_collecte.md>) |
| P019 | Contribuer au volet maintenance d’un système de gestion | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P019_gmao_maintenance/P019_collecte.md>) |
| P020 | Expertise mécanique et encadrement — périmètre à préciser | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P020_expertise_mecanique/P020_collecte.md>) |
| P001 | Rédiger le cadre de fonctionnement d’une équipe d’exploitation | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P001_projet_equipe/P001_collecte.md>) |
| P021 | Qualification pour une fonction d’exploitation | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P021_habilitation_exploitation/P021_collecte.md>) |
| P022 | Projet de formation à dimension internationale — à étayer | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P022_projet_formation_international/P022_collecte.md>) |
| P023 | Situations d’urgence en exploitation — cas personnel à identifier | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P023_situations_urgence_exploitation/P023_collecte.md>) |
| P012 | Fiabilisation des interventions — contribution à préciser | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P012_facteurs_humains/P012_collecte.md>) |
| P024 | Accompagner la compréhension d’une opération d’actionnariat | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P024_accompagnement_actionnariat/P024_collecte.md>) |
| P025 | Assumer une responsabilité régionale de maintenance | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P025_maintenance_regionale/P025_collecte.md>) |
| P005 | Structurer les données de suivi de maintenance | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P005_reporting_maintenance/P005_collecte.md>) |
| P006 | Planifier la préparation d’arrêts de maintenance | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P006_preparation_arrets/P006_collecte.md>) |
| P007 | Préparer l’intégration d’une nouvelle unité à l’exploitation | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P007_integration_unite/P007_collecte.md>) |
| P026 | Projet de stockage industriel — périmètre à confirmer | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P026_projet_stockage/P026_collecte.md>) |
| P027 | Amélioration de productivité — résultat à reconstituer | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P027_amelioration_productivite/P027_collecte.md>) |
| P029 | Reconstruction d’un banc de contrôle — preuves à réunir | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P029_reconstruction_banc/P029_collecte.md>) |
| P030 | Assumer une responsabilité de production | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P030_responsabilite_production/P030_collecte.md>) |
| P031 | Prendre la responsabilité d’un atelier industriel | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P031_responsabilite_departements/P031_collecte.md>) |
| P028 | Analyser la charge et la capacité d’un atelier | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P028_charge_capacite_tth/P028_collecte.md>) |
| P003 | Préparer une demande d’investissement industriel | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P003_dossier_investissement_four/P003_collecte.md>) |
| P008 | Examiner un écart de traitement thermique — rôle à préciser | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P008_homogeneite_traitements/P008_collecte.md>) |
| P032 | Rationalisation de maintenance — transformation à documenter | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P032_rationalisation_maintenance/P032_collecte.md>) |
| P033 | Préparer le diagnostic d’un dysfonctionnement de four | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P033_diagnostic_four/P033_collecte.md>) |
| P002 | Piloter un chantier d’amélioration sur les réfractaires | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P002_mcp_refractaires/P002_collecte.md>) |
| P004 | Investiguer des défauts d’incrustation en coulée continue | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P004_incrustations_coulee/P004_collecte.md>) |
| P009 | Préparer des essais de nuances à coût optimisé | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P009_nuances_cout_optimise/P009_collecte.md>) |
| P034 | Préparer un plan de maintenance préventive | [Dossier](</Users/fix.emmanuelyahoo.fr/Library/Mobile Documents/com~apple~CloudDocs/AA - Documents Man/AA1 - PROJECTS/Codex/02_Projects/diagnostic_projets_pros/projets-professionnels/P034_maintenance_preventive/P034_collecte.md>) |

## Périmètre d’une future intégration

Remplacer le menu `experiences_menu.html` par cette entrée de réalisations, alimentée par des métadonnées de cartes séparées des textes d’études. Conserver les URL existantes de domaines, intégrer les deux études relues comme pages de détail, puis ajouter les nouveaux cas au fil de leur relecture. Aucun texte de contrôle privé n’accompagne ces pages.

Cette proposition conserve les sources éditoriales et les maquettes existantes. Aucune route, aucun template et aucune publication n’ont été modifiés.
