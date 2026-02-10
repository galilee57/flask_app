---
title: 💪 Projet Musculation – Calcul Force, Hypertrophie & Endurance
summary: Version Française
---

**Ce projet analyse les séances de musculation à partir de données simples** : le nombre de répétitions, les charges utilisées et le volume total de travail.

Pour chaque exercice, l’application calcule le volume d’entraînement (charge × répétitions × séries), puis interprète la séance en fonction des plages de répétitions généralement associées aux objectifs en musculation :

→ Faibles répétitions avec charges élevées → travail orienté force
→ Répétitions modérées avec volume significatif → travail orienté hypertrophie
→ Répétitions élevées avec charges plus légères → travail orienté endurance musculaire

Ces informations sont ensuite agrégées sur l’ensemble de la séance afin d’estimer la répartition réelle du travail entre force, hypertrophie et endurance.

L’utilisateur peut ainsi :

→ comprendre ce qu’il travaille réellement, au-delà du ressenti
→ comparer différentes séances entre elles
→ ajuster son volume ou ses répétitions pour mieux cibler ses objectifs

Le calcul repose sur une distribution de pondérations centrée sur le nombre de répétitions effectué.
Pour chaque répétition, une part du volume est répartie entre force, hypertrophie et endurance, selon des coefficients normalisés (leur somme est égale à 1).
Cette approche permet de lisser l’analyse et de mieux refléter la réalité physiologique de l’entraînement, où les zones se chevauchent.

Le modèle de charge ↔ répétitions ↔ adaptations proposé dans cette application s’appuie sur le concept bien documenté du repetition continuum, selon lequel différents nombres de répétitions et charges favorisent des adaptations différentes (force, hypertrophie, endurance) dans l’entraînement en résistance. Des revues scientifiques confirment également que le volume total de travail joue un rôle central dans les gains musculaires, ce qui justifie mon approche de distribution pondérée des répétitions plutôt que des seuils fixes.

📚 **Références scientifiques**
Les principes de calcul utilisés dans ce projet s’appuient sur des travaux reconnus en sciences de l’entraînement, notamment sur la relation entre charge, nombre de répétitions, volume total et adaptations physiologiques (force, hypertrophie, endurance).
Schoenfeld, B. J. (2010).
The mechanisms of muscle hypertrophy and their application to resistance training.
Journal of Strength and Conditioning Research, 24(10), 2857–2872.
→ Article de référence expliquant les mécanismes de l’hypertrophie musculaire et le rôle du volume d’entraînement.
Schoenfeld, B. J., Grgic, J., Ogborn, D., & Krieger, J. W. (2017).
Strength and hypertrophy adaptations between low- vs. high-load resistance training.
Journal of Strength and Conditioning Research, 31(12), 3508–3523.
→ Montre que différentes plages de répétitions peuvent produire une hypertrophie similaire lorsque le volume est contrôlé.
Schoenfeld, B. J., & Grgic, J. (2018).
Evidence-based guidelines for resistance training volume to maximize muscle hypertrophy.
Strength and Conditioning Journal, 40(4), 107–112.
→ Met en évidence l’importance du volume total plutôt que de seuils stricts de répétitions.
Campos, G. E. R., et al. (2002).
Muscular adaptations in response to three different resistance-training regimens.
European Journal of Applied Physiology, 88, 50–60.
→ Étude fondatrice illustrant le continuum force – hypertrophie – endurance selon les répétitions et charges.
American College of Sports Medicine (ACSM). (2009).
Progression models in resistance training for healthy adults.
Medicine & Science in Sports & Exercise, 41(3), 687–708.
→ Recommandations officielles sur les plages de répétitions et leur lien avec les adaptations musculaires.
