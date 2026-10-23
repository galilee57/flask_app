from flask import Blueprint

bp = Blueprint("professional_positioning", __name__, template_folder="templates")
public_bp = Blueprint("positioning_public", __name__, template_folder="templates")

from . import routes


@bp.record_once
def register_commands(state):
    from .commands import import_command, context_command
    state.app.cli.add_command(import_command)
    state.app.cli.add_command(context_command)
