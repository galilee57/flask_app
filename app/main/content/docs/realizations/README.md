# Modifier les projets et études de cas

Chaque projet possède quatre fichiers, accessibles depuis [l’index de relecture](index-relecture.md). Un [modèle de projet](template.md) décrit leur création et le tag de présentation.

- `<projet>.fr.md` contient le récit français long relu et les métadonnées communes.
- `<projet>.en.md` contient sa traduction anglaise complète.
- `<projet>.short.fr.md` contient la version courte française.
- `<projet>.short.en.md` contient la version courte anglaise.

Les sources sont relues à chaque requête. Enregistrer un Markdown puis recharger la page permet de voir les modifications.

## Choisir la version affichée

Dans le frontmatter de la fiche française longue, choisir une valeur pour `display_version`.

```yaml
display_version: long
```

La valeur `long` affiche le récit détaillé. La valeur `short` affiche la version courte dans les deux langues, sur la carte comme sur la page du projet. Le choix est propre à chaque projet. Les fiches sont initialement réglées sur `long`.

Le contenu court a ses propres titre, résumé, texte, images et projets associés. Les fiches courtes proposées utilisent des formulations plus générales et des passages du récit français, avec des médias et liens associés vides. Les mentions d’organisations, de lieux et les chiffres identifiants sont écartés des passages retenus. Relire les fichiers courts permet d’ajuster le degré de détail et les informations que l’on souhaite montrer.

Les compétences, l’année, le statut, les thèmes et l’origine du projet sont communs aux deux présentations et sont lus depuis la fiche française longue. L’année reste une métadonnée disponible pour l’animation.

## Champs éditables

- `display_version` vaut `long` ou `short` dans la fiche française longue et pilote les deux langues.
- `title` : titre de la carte et de l’étude.
- `summary` : résumé de carte et sous-titre d’étude.
- `origin` : `professional` ou `personal`.
- `themes` : liste parmi `industry`, `data`, `apps`, `making`, `image`, `learning`.
- `skills` : identifiants des compétences mobilisées, affichées sur les cartes et dans les études. Les libellés français et anglais sont définis dans [skills.yml](skills.yml).
- `year` : année de référence du projet, sous forme d’entier, ou `null` si elle reste à renseigner. Cette donnée est disponible pour la future animation.
- `featured` : inclusion dans la sélection.
- `detail` : présence d’une page d’étude. Laisser `false` pour une simple carte sujet.
- `images` : médias, alternatives textuelles et légendes ; chemins relatifs à `app/realizations/static/images/`.

Le titre de page visible vient de `title` du fichier correspondant à la version et à la langue choisies. Le H1 du corps conserve le titre de la source. Les H2 structurent les sections de l’étude, les H3 leurs sous-parties. Les commentaires `<!-- media: identifiant -->` insèrent une image à l’endroit choisi. `emplacements: [ouverture]` place un visuel en tête ; `emplacements: [galerie]` permet de l’ajouter dans la galerie. `nature: illustration` ajoute une mention visible.

Les versions actives des maquettes de `diagnostic_projets_pros` ont été importées le 11 novembre 2026. Les notes de contrôle restent dans les archives. Les cartes personnelles et professionnelles sont classées selon le champ `origin` et répertoriées dans l’index de relecture.

## Accès au catalogue

La navigation PRO ouvre le catalogue public à `/realizations/`. Les fiches détaillées et leurs médias sont accessibles sans connexion. L’ancien lien `/experiences_menu` redirige vers le catalogue, et les pages par domaine restent accessibles à partir de `/experiences/`.

## Cartographie de compétences

Les identifiants de `skills` sont communs aux différents projets. Par exemple, `engineering` désigne l’ingénierie, `management` le management, `project_management` la gestion de projet, `web_development` le développement web, `ai` l’intelligence artificielle et `agentic_ai` l’IA agentique. Chaque compétence peut relier plusieurs projets dans la future cartographie.

Pour modifier une attribution, éditer la liste `skills` du projet. Pour ajouter une compétence, définir son identifiant et ses libellés `fr` et `en` dans `skills.yml`, puis utiliser cet identifiant dans les projets concernés. Les compétences ont été proposées à partir des récits relus. Leur ordre dans le Markdown détermine leur ordre d’affichage.

Le champ `year` est présent dans chaque fiche. L’année 2007 reprend l’obtention de la licence de psychologie, et 2026 correspond au projet Rust. Les autres années sont à compléter. Les cartes exposent `data-year` et `data-skills` pour préparer leur exploitation par l’animation.

Le 21 novembre 2026, les cinq fiches P005, P007, P037, P071 et P073 ont été conservées à la demande de l’utilisateur avec leur statut existant. Le nouveau PP020 est ajouté en fin de catalogue avec le statut « À relire ».


## Versions anglaises et versions courtes

Les versions anglaises longues sont traduites à partir des dernières fiches françaises relues. Les paragraphes, listes, niveaux de titres, chiffres et médias sont contrôlés lors de la génération. Les versions courtes reprennent une sélection de passages français et disposent de leur traduction anglaise.

Modifier ensuite un texte français appelle une relecture de sa traduction anglaise et de ses variantes courtes. La sélection d’une version est immédiate au rechargement. La traduction ou la rédaction des autres versions reste une opération éditoriale.

## Illustrations complémentaires

Les [six illustrations ajoutées le 22 novembre 2026](../../../../../artifacts/realizations/illustration-briefs/README.md) sont rangées par projet dans `app/realizations/static/images/generated/`. Les briefs conservent les prompts exacts, la provenance et les fichiers retenus. Les légendes et alternatives sont éditables dans les fiches longues FR/EN. Les médias des variantes courtes restent indépendants.

## Miniatures et images adaptées aux écrans

Les sources sont classées par provenance puis par fiche, dans `imported/` ou `generated/`. Le dossier commence par l’identifiant de la fiche en minuscules, suivi si nécessaire d’un nom descriptif séparé par des tirets (par exemple `f003` ou `e002-exploitation-centrale-nucleaire`). Les fichiers portent un nom de rôle (`cover`, `detail`, `jupiter`, `camera-photo`, etc.). Les variantes WebP reprennent le dossier du projet dans `responsive/` et ajoutent leur largeur réelle au nom, par exemple `responsive/p071-donnees-grande-echelle/cover-v1-640.webp`. Le manifeste associe chaque source à ses dimensions et variantes. Les cartes utilisent les tailles adaptées à l’écran ; les études peuvent aussi charger les variantes jusqu’à 1440 px. Le navigateur choisit la taille avec `srcset` et `sizes`, et les médias hors écran sont chargés à la demande.

Après un ajout ou une modification d’image, reconstruire les variantes avec Python 3.11 ou plus récent :

```sh
pip install -r requirements-images.txt
python scripts/build_realization_images.py
```

Le script conserve les proportions et l’orientation, ne grossit pas les petites images et préserve les originaux. Les SVG restent vectoriels. Après avoir ajouté, renommé ou déplacé une source, reconstruire les variantes et le manifeste ; inclure `app/realizations/static/images/responsive/` dans le commit. Aucune bibliothèque d’image supplémentaire n’est nécessaire au serveur. La conversion utilise [Pillow](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#webp).
