# Environnement de développement : nenv

source nenv/bin/activate
(ou conda activate nenv)

# Lancement de l'appli en mode debuger

flask --app wsgi --debug run

# Console pythonAnyWhere (utiliser celle à partir de l'env dans Web Menu)

git pull
puis valider par :wq
Reload App (menu Web)

# Lancement de npx pour compilation de tailwind avec watch

npx @tailwindcss/cli \
 -i ./input.css \
 -o ./app/main/static/css/output.css \
 --watch

# Structure de l'application

app : init.py contents blueprints registrations
blueprints basic folder are defined with a generic path '/project/<project_name>'

Each folder contents its own templates and static files.
init.py defines the folder like a blueprint and imports routes.
routes.py defines routes from the folder.

# Environements management

An environment variable has been defined and is managed in config.py: APP_ENV
wgsi.py of Pythonanywhere set its as prod.
Use export APP_ENV=dev before flask run.

# In pythonAnyWhere : this code in wsgi.py to define ENV_VARIABLE

import sys, os
project_path = '/home/Galilee57/flask_app' # <- respecte bien la casse !
if project_path not in sys.path:
sys.path.append(project_path)

from app import create_app
application = create_app()

# Link the environement nenv (in web page) :

/home/Galilee57/.virtualenvs/nenv

# NOTE : example of portfolios

https://www.codewonders.dev
https://dunks1980.com
https://mattfarley.ca/
https://www.rammaheshwari.com/#about

https://lottiefiles.com/free-animations/gaming

Retrogaming : incarner un personnage qui nqvigue dqns un monde varié. Bien les placer pour assurer une coherence et eviter que les visiteurs ne se perdent. Phaser Game Engine.

# TODO : utilisation de Taipy pour montrer des tableaux de bord

# TODO : Ideas for future projects

- Reinforcement AI
- Jeu du Taquin : exploration d'un arbre / notion d'heuristique
- Simulation Modèle Prédateur - proie / isometrique
- Simulation d'une contagion / isometrique
- Machine de Turing
- Pacman
- Configurateur 3D : https://sketchfab.com/3d-models/
- Admin, healthy
