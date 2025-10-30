# Environnement de développement : nenv

source nenv/bin/activate
(ou canda activate nenv)

# Lancement de l'appli en mode debuger

flask --app wsgi --debug run

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

# TODO : utilisation de Taipy pour montrer des tableaux de bord

Le portfolio retrogaming : Certainement l’un des portfolios les plus créatifs que nous avons reçus chez Silkhom ! Conçu par le développeur web front-end Peter Oravec, ce portfolio est pour le moins unique en son genre. À la fois créatif et ludique, son site web est admirablement bien placé sous l’angle du retrogaming et du jeu de rôle. Le concept : le visiteur incarne un petit personnage qui navigue dans un monde varié. Durant la navigation, le petit personnage peut s’arrêter sur des éléments clés du parcours du développeur. On retrouve les technologies maitrisées dans une pièce spécifique, au même titre que ces récompenses, ses expériences, son curriculum vitæ, ses réseaux sociaux, etc.

Ces éléments ne sont pas placés au hasard dans le monde ce qui apporte une bonne cohérence dans l’expérience de navigation. Une map permet de visualiser le monde dans son ensemble pour éviter que les visiteurs se perdent. Côté technique, ce portfolio a été réalisé avec JavaScript, HTML 5, ainsi que Phaser Game Engine. Bien que cela puisse paraître simple et abordable, ce type de portfolio demande une certaine expérience et de solides connaissances en développement.
