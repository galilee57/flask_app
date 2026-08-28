
from flask import jsonify, render_template, request
from .forms import ExerciseForm, WorkoutPlanForm
from .models import Programme, ProgrammeExercice
from app.extensions import db
from app.security import enforce_admin_api_token
from . import bp
from pathlib import Path
import json

# --- Helpers to load data files --- #

def _data_file(filename: str) -> Path:
    root = Path(bp.root_path)
    data_dir = root / "static" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / filename

# Load exercices from a JSON file
def load_exercices(filename):
    filepath = _data_file(filename)
    with filepath.open(encoding="utf-8") as f:
        return json.load(f)

# Load Reps Evaluation data from a JSON file
def load_reps_profile():
    data = load_exercices("reps_evaluation.json")
    max_reps = data.get("max_reps", 30)
    values = data.get("values", [])
    return max_reps, values

def coeffs_for_reps(reps: int, max_reps: int, values: list[dict]) -> dict:
    """
    Trouve les coefficients correspondant au nombre de répétitions.
    """
    if reps is None or reps <= 0:
        return {'force': 0.0, 'endurance': 0.0, 'hypertrophie': 0.0  }
    
    if reps >= max_reps:
        reps = max_reps

    chosen = None
    for row in values:
        r = row.get("reps")
        if r is None:
            continue
        if r == reps:
            chosen = row
            break
        if r < reps:
            chosen = row # on prend la dernière inférieure

    if not chosen and values:
        chosen = values[0]
    
    return {
        'force': chosen.get('force', 0.0),
        'hypertrophie': chosen.get('hypertrophie', 0.0),
        'endurance': chosen.get('endurance', 0.0)
    }


def validate_programme_payload(payload):
    """Validate and normalize input before creating a database transaction."""
    if not isinstance(payload, dict):
        return None, None, "JSON manquant ou invalide"

    name = payload.get("name")
    exercices = payload.get("exercices")
    if not isinstance(name, str) or not (name := name.strip()) or len(name) > 100:
        return None, None, "Le champ 'name' est obligatoire et limité à 100 caractères"
    if not isinstance(exercices, list) or not 1 <= len(exercices) <= 100:
        return None, None, "La liste 'exercices' doit contenir entre 1 et 100 exercices"

    normalized = []
    for exercice in exercices:
        if not isinstance(exercice, dict):
            return None, None, "Chaque exercice doit être un objet JSON"
        exercice_id = exercice.get("exercice_id")
        try:
            reps = int(exercice.get("reps"))
            weight = int(exercice.get("weight"))
        except (TypeError, ValueError):
            return None, None, "Les répétitions et le poids doivent être des entiers"
        if not isinstance(exercice_id, str) or not (exercice_id := exercice_id.strip()) or len(exercice_id) > 200:
            return None, None, "Chaque exercice doit avoir un 'exercice_id' valide"
        if not 1 <= reps <= 500 or not 0 <= weight <= 1_000:
            return None, None, "Les répétitions ou le poids sont hors limites"
        normalized.append({"exercice_id": exercice_id, "reps": reps, "weight": weight})
    return name, normalized, None

# --- Definition des routes --- #
@bp.get("/")
def home():
    exercise_form = ExerciseForm()
    workout_form = WorkoutPlanForm()
    return render_template(
        "index_musculation.html", 
        exercise_form=exercise_form, 
        workout_form=workout_form
        )

# API pour récupérer la liste des exercices
@bp.get("/api/exercices")
def api_exercices():
    exercices = load_exercices("exercices.json")
    return jsonify(exercices)

# API pour récupérer les évaluations de répétitions
@bp.get("/api/reps_evaluation")
def api_reps_evaluation():
    data = load_exercices("reps_evaluation.json")
    return jsonify(data)

# API pour créer un nouveau programme
@bp.route("/api/programmes", methods=["POST"])
def create_programme():
    """
    Crée un nouveau programme à partir d'un JSON envoyé par le front.
    """
    enforce_admin_api_token()
    name, exercices_data, error = validate_programme_payload(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    # 1) Créer le programme
    programme = Programme(name=name)
    db.session.add(programme)
    db.session.flush()  # pour avoir programme.id sans faire encore un commit

    # 2) Créer les lignes d'exercices
    for ex in exercices_data:
        pe = ProgrammeExercice(
            programme_id=programme.id,
            exercice_id=ex["exercice_id"],
            reps=ex["reps"],
            weight=ex["weight"],
        )
        db.session.add(pe)

    # 3) Valider en base
    db.session.commit()

    return jsonify({
        "success": True,
        "programme_id": programme.id,
        "name": programme.name
    }), 201

# --- API pour récupérer la liste des programmes existants --- #
@bp.route('/api/programmes', methods=['GET'])
def list_programmes():
    """
    Retourne la liste des programmes existants.
    """
    programmes = Programme.query.order_by(Programme.created_at.desc()).all()
    
    data = [
        {
            "id": p.id,
            "name": p.name,
            "exercices_count": len(p.exercices)
        }
        for p in programmes
    ]

    return jsonify(data)

# API pour récupérer un programme spécifique
@bp.route('/api/programmes/<int:programme_id>', methods=['GET', 'PUT', 'DELETE'])
def programme_detail(programme_id):
    """
    GET    -> détails d'un programme spécifique
    PUT    -> mise à jour d'un programme (nom + exercices)
    DELETE -> suppression du programme
    """
    programme = Programme.query.get_or_404(programme_id)

    # --------- GET ---------
    if request.method == "GET":
        data = {
            "id": programme.id,
            "name": programme.name,
            "exercices": [
                {
                    "id": ex.id,
                    "exercice_id": ex.exercice_id,
                    "reps": ex.reps,
                    "weight": ex.weight
                }
                for ex in programme.exercices
            ]
        }
        return jsonify(data)

    # --------- PUT ---------
    if request.method == "PUT":
        enforce_admin_api_token()
        name, exercices_data, error = validate_programme_payload(request.get_json(silent=True))
        if error:
            return jsonify({"error": error}), 400

        # 1) mettre à jour le nom
        programme.name = name

        # 2) supprimer les anciennes lignes (cascade sur relationship)
        programme.exercices.clear()

        # 3) recréer les nouvelles
        for ex in exercices_data:
            pe = ProgrammeExercice(
                programme_id=programme.id,
                exercice_id=ex["exercice_id"],
                reps=ex["reps"],
                weight=ex["weight"],
            )
            db.session.add(pe)

        db.session.commit()
        return jsonify({"success": True, "message": "Programme mis à jour"}), 200

    # --------- DELETE ---------
    if request.method == "DELETE":
        enforce_admin_api_token()
        db.session.delete(programme)
        db.session.commit()
        return jsonify({"success": True, "message": "Programme supprimé"}), 200
    
# --- API pour calculer les coefficients selon les répétitions --- #
@bp.route("/api/programmes/<int:programme_id>/analyse", methods=["GET"])
def analyse_programme(programme_id):
    """
    Analyse un programme :
    - volume = reps * weight pour chaque exercice
    - applique les coefficients issus de reps_evaluation.json
    - agrège des scores par catégorie (force / hypertrophie / endurance)
    """
    programme = Programme.query.get_or_404(programme_id)

    max_reps, values = load_reps_profile()

    total_force = 0.0
    total_hypertrophie = 0.0
    total_endurance = 0.0

    per_exercice = []

    for ex in programme.exercices:
        reps = ex.reps or 0
        weight = ex.weight or 0
        volume = reps * weight

        coeffs = coeffs_for_reps(reps, max_reps, values)
        force_coef = coeffs["force"]
        hyp_coef = coeffs["hypertrophie"]
        endu_coef = coeffs["endurance"]

        force_score = volume * force_coef
        hyp_score = volume * hyp_coef
        endu_score = volume * endu_coef

        total_force += force_score
        total_hypertrophie += hyp_score
        total_endurance += endu_score

        per_exercice.append({
            "exercice_id": ex.exercice_id,  # nom de l'exercice
            "reps": reps,
            "weight": weight,
            "volume": volume,
            "coeffs": coeffs,
            "scores": {
                "force": force_score,
                "hypertrophie": hyp_score,
                "endurance": endu_score,
            },
        })

    data = {
        "programme_id": programme.id,
        "name": programme.name,
        "totals": {
            "force": total_force,
            "hypertrophie": total_hypertrophie,
            "endurance": total_endurance,
        },
        "per_exercice": per_exercice,
    }

    return jsonify(data)
