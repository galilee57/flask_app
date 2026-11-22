# Modèle de projet bilingue

Créer les quatre fichiers ci-dessous en remplaçant `ppXXX` par un identifiant unique. Les textes entre crochets sont à rédiger à partir du projet réel. Les quatre versions doivent conserver les mêmes faits et la même attribution du travail.

## `ppXXX.fr.md` — source longue et choix d’affichage

```markdown
---
id: PPXXX
origin: personal
editorial_status: À relire
featured: false
detail: true
display_version: long
title: "[Titre français]"
summary: "[Résumé français]"
themes: [apps]
skills: [project_management]
year: null
images: []
related_ids: []
---

## Le projet

[Besoin, contexte, contraintes et stade atteint.]

## Ma contribution

[Rôle personnel, travail collectif et choix étayés.]

## Résultats et limites

[Livrables, résultats établis et limites.]
```

`display_version: long` affiche l’étude complète. `display_version: short` affiche la version courte, pour la carte et la page, en français comme en anglais. Ce tag est lu uniquement dans la source française longue.

Choisir les identifiants de `skills` dans [skills.yml](skills.yml), le thème dans le [guide](README.md) et renseigner `year` quand l’année est connue. Les métadonnées communes restent dans la source française longue ; les récits peuvent comporter les sections supplémentaires utiles au projet.

## `ppXXX.en.md` — traduction longue

Reprendre les métadonnées du fichier français, sans recopier `display_version`. Traduire intégralement `title`, `summary`, le corps et les textes des images (`alt`, `titre`, `legende`). Conserver les identifiants, chemins de médias, chiffres, liens, compétences, année et structure des titres.

## `ppXXX.short.fr.md` — présentation courte

```markdown
---
id: PPXXX
title: "[Titre français court]"
summary: "[Résumé français court]"
images: []
related_ids: []
---

## Le projet

[Contexte bref, avec les seules informations que l’on souhaite afficher.]

## Ma contribution

[Contribution personnelle en quelques phrases.]

## Résultats

[Résultat essentiel, fidèle à la version longue.]
```

Relire les noms, lieux, dates, chiffres, liens et médias selon le degré d’anonymat souhaité. Les versions courtes peuvent avoir leurs propres images et projets associés ; elles n’héritent pas de ceux de la version longue.

## `ppXXX.short.en.md` — présentation courte anglaise

Reprendre les métadonnées et le contenu de la version courte française, puis traduire `title`, `summary` et le corps en anglais. Utiliser les rubriques `The project`, `My contribution` et `Results`. Conserver `id`, `images` et `related_ids`.

Ajouter enfin les liens vers les quatre fichiers dans [l’index de relecture](index-relecture.md).
