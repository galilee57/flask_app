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
