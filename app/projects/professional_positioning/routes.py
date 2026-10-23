from uuid import uuid4
from flask import abort, jsonify, render_template, request, session, url_for
from app.core.admin import is_admin
from app.core.security import require_admin_api_token
from app.extensions import db
from . import bp, public_bp
from .models import Diagnostic, Profile, Assessment, PublicSnapshot, now
from .services import ROLES, CRITERIA, text, url, consultation, aggregate, freeze_provenance


@bp.before_request
def private_access():
    if not is_admin():
        abort(404)


@bp.after_request
def private_headers(response):
    response.headers["Cache-Control"] = "private, no-store"
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    response.vary.add("Cookie")
    return response


@bp.errorhandler(ValueError)
def invalid_input(error):
    db.session.rollback()
    return jsonify(error="invalid_input", field=str(error)), 400


def body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("body")
    return data


def get_diagnostic(identifier):
    return db.get_or_404(Diagnostic, identifier)


@bp.get("/")
def index():
    from flask import redirect
    from .models import AnalysisRun
    latest = db.session.scalars(
        db.select(AnalysisRun).order_by(AnalysisRun.created_at.desc())
    ).first()
    if latest:
        return redirect(url_for("professional_positioning.dashboard", identifier=latest.diagnostic_id))
    return manual_editor()


@bp.get("/manual")
def manual_editor():
    return render_template("positioning_index.html", roles=ROLES, diagnostics=db.session.scalars(db.select(Diagnostic).order_by(Diagnostic.created_at.desc())).all())


@bp.post("/api/diagnostics")
@require_admin_api_token
def create_diagnostic():
    data = body()
    role = text(data, "role", 40)
    if role not in ROLES:
        raise ValueError("role")
    item = Diagnostic(id=str(uuid4()), title=text(data, "title", 160), role=role, context=text(data, "context"))
    db.session.add(item)
    db.session.commit()
    return jsonify(url=url_for("professional_positioning.detail", identifier=item.id)), 201


@bp.get("/diagnostics/<identifier>")
def detail(identifier):
    item = get_diagnostic(identifier)
    profiles = db.session.scalars(db.select(Profile).where(Profile.diagnostic_id == item.id)).all()
    assessments = db.session.scalars(db.select(Assessment).join(Profile).where(Profile.diagnostic_id == item.id)).all()
    snapshots = db.session.scalars(db.select(PublicSnapshot).where(PublicSnapshot.diagnostic_id == item.id)).all()
    return render_template("positioning_detail.html", item=item, profiles=profiles, assessments=assessments, criteria=CRITERIA[item.role], roles=ROLES, snapshots=snapshots)


@bp.post("/api/diagnostics/<identifier>/profiles")
@require_admin_api_token
def add_profile(identifier):
    get_diagnostic(identifier)
    data = body()
    kind = text(data, "kind", 20)
    if kind not in ("portfolio", "reference"):
        raise ValueError("kind")
    if kind == "portfolio" and db.session.scalar(db.select(Profile).where(Profile.diagnostic_id == identifier, Profile.kind == kind)):
        raise ValueError("portfolio_exists")
    canonical_url = url(data)
    if db.session.scalar(db.select(Profile).where(Profile.diagnostic_id == identifier, Profile.url == canonical_url)):
        raise ValueError("duplicate_profile")
    item = Profile(id=str(uuid4()), diagnostic_id=identifier, kind=kind, name=text(data, "name", 160), url=canonical_url, rationale=text(data, "rationale"))
    db.session.add(item)
    db.session.commit()
    return jsonify(id=item.id), 201


@bp.post("/api/diagnostics/<identifier>/assessments")
@require_admin_api_token
def assess(identifier):
    diagnostic = get_diagnostic(identifier)
    data = body()
    profile = db.get_or_404(Profile, text(data, "profile_id", 36))
    if profile.diagnostic_id != identifier:
        abort(404)
    criterion = text(data, "criterion", 60)
    confidence = text(data, "confidence", 10)
    if criterion not in {c[0] for c in CRITERIA[diagnostic.role]} or confidence not in ("low", "medium", "high"):
        raise ValueError("criterion_or_confidence")
    item = db.session.scalar(db.select(Assessment).where(Assessment.profile_id == profile.id, Assessment.criterion == criterion))
    if item is None:
        item = Assessment(id=str(uuid4()), profile_id=profile.id, criterion=criterion)
    item.finding = text(data, "finding")
    item.confidence = confidence
    item.confidence_reason = text(data, "confidence_reason")
    item.url = url(data)
    item.excerpt = text(data, "excerpt")
    item.consulted_at = consultation(data)
    # Any edit invalidates the previous human verification.
    item.verified_at = None
    item.verified_by = None
    db.session.add(item)
    db.session.commit()
    return jsonify(id=item.id), 201


@bp.post("/api/assessments/<identifier>/verify")
@require_admin_api_token
def verify(identifier):
    item = db.get_or_404(Assessment, identifier)
    item.verified_at = now()
    item.verified_by = session["admin_username"]
    db.session.commit()
    return jsonify(verified=True)


@bp.post("/api/diagnostics/<identifier>/snapshots")
@require_admin_api_token
def snapshot(identifier):
    diagnostic = get_diagnostic(identifier)
    profiles = db.session.scalars(db.select(Profile).where(Profile.diagnostic_id == identifier)).all()
    assessments = db.session.scalars(db.select(Assessment).join(Profile).where(Profile.diagnostic_id == identifier)).all()
    payload = aggregate(diagnostic, profiles, assessments)
    if not any(row["count"] is not None for row in payload["rows"]):
        raise ValueError("insufficient_verified_group")
    item = PublicSnapshot(
        id=str(uuid4()), diagnostic_id=identifier, payload=payload,
        provenance=freeze_provenance(diagnostic, profiles, assessments),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(url=url_for("professional_positioning.preview", identifier=item.id)), 201


@bp.get("/api/roles")
def roles():
    return jsonify(version="1", roles=ROLES, criteria=CRITERIA)


@bp.get("/api/snapshots/<identifier>/provenance")
def provenance(identifier):
    item = db.get_or_404(PublicSnapshot, identifier)
    return jsonify(item.provenance)


@bp.get("/snapshots/<identifier>")
def preview(identifier):
    item = db.get_or_404(PublicSnapshot, identifier)
    return render_template("positioning_snapshot.html", snapshot=item, payload=item.payload, criteria=CRITERIA[item.payload["role"]], roles=ROLES, preview=True)


@bp.post("/api/snapshots/<identifier>/publish")
@require_admin_api_token
def publish(identifier):
    item = db.get_or_404(PublicSnapshot, identifier)
    if item.published_at is None:
        item.published_at = now()
        db.session.commit()
    return jsonify(url=url_for("positioning_public.infographic", identifier=item.id))


@bp.post("/api/snapshots/<identifier>/withdraw")
@require_admin_api_token
def withdraw(identifier):
    item = db.get_or_404(PublicSnapshot, identifier)
    item.published_at = None
    db.session.commit()
    return jsonify(withdrawn=True)


@public_bp.get("/<identifier>")
def infographic(identifier):
    item = db.get_or_404(PublicSnapshot, identifier)
    if item.published_at is None:
        abort(404)
    # Public rendering receives sanitized fields only, never a source ORM object.
    return render_template("positioning_snapshot.html", payload=item.payload, criteria=CRITERIA[item.payload["role"]], roles=ROLES, preview=False)


@public_bp.after_request
def public_headers(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.get("/dashboard")
def dashboard_home():
    from flask import redirect
    from .models import AnalysisRun
    latest = db.session.scalars(db.select(AnalysisRun).order_by(AnalysisRun.created_at.desc())).first()
    if latest is None:
        return index()
    return redirect(url_for("professional_positioning.dashboard", identifier=latest.diagnostic_id))


@bp.get("/diagnostics/<identifier>/dashboard")
def dashboard(identifier):
    from .models import AnalysisRun, MemoryEntry, WorkItem
    from .analysis import run_view
    diagnostic = get_diagnostic(identifier)
    runs = db.session.scalars(db.select(AnalysisRun).where(AnalysisRun.diagnostic_id == identifier).order_by(AnalysisRun.created_at.desc())).all()
    if not runs:
        return detail(identifier)
    run_id = request.args.get("run", runs[0].id)
    run = next((r for r in runs if r.id == run_id), None)
    if run is None:
        abort(404)
    memory = db.session.scalars(db.select(MemoryEntry).where(MemoryEntry.diagnostic_id == identifier).order_by(MemoryEntry.created_at.desc())).all()
    actions = db.session.scalars(db.select(WorkItem).where(WorkItem.diagnostic_id == identifier).order_by(WorkItem.created_at)).all()
    view = run_view(run)
    previous = db.session.get(AnalysisRun, run.parent_id) if run.parent_id else None
    previous_view = run_view(previous) if previous else None
    old_status = {row["criterion"]["key"]: row["target"].status for row in previous_view["comparison"]} if previous_view else {}
    return render_template("positioning_dashboard.html", item=diagnostic, run=run, runs=runs,
                           memory=memory, actions=actions, old_status=old_status, **view)


@bp.post("/api/diagnostics/<identifier>/memory")
@require_admin_api_token
def add_memory(identifier):
    from .models import AnalysisRun, MemoryEntry
    get_diagnostic(identifier)
    data = body()
    kind = text(data, "kind", 20)
    if kind not in {"comment", "evidence"}:
        raise ValueError("kind")
    run_id = text(data, "run_id", 36)
    run = db.get_or_404(AnalysisRun, run_id)
    if run.diagnostic_id != identifier:
        abort(404)
    criterion = data.get("criterion") or None
    if criterion and criterion not in {c["key"] for c in run.rubric}:
        raise ValueError("criterion")
    evidence = None
    if kind == "evidence":
        evidence = {"url": url(data), "excerpt": text(data, "excerpt", 2000),
                    "consulted_at": consultation(data).isoformat(),
                    "method": "user_supplied", "verification": "pending_review"}
    entry = MemoryEntry(id=str(uuid4()), diagnostic_id=identifier, run_id=run_id,
                        criterion=criterion, kind=kind, body=text(data, "body", 12000),
                        actor=session["admin_username"], evidence=evidence)
    db.session.add(entry)
    db.session.commit()
    return jsonify(id=entry.id), 201


@bp.post("/api/diagnostics/<identifier>/actions")
@require_admin_api_token
def add_action(identifier):
    from .models import AnalysisRun, WorkItem
    get_diagnostic(identifier)
    data = body()
    run = db.session.scalars(db.select(AnalysisRun).where(AnalysisRun.diagnostic_id == identifier).order_by(AnalysisRun.created_at.desc())).first()
    if run is None or data.get("criterion") not in {c["key"] for c in run.rubric}:
        raise ValueError("criterion")
    priority = data.get("priority", "medium")
    if priority not in {"high", "medium", "low"}:
        raise ValueError("priority")
    action = WorkItem(id=str(uuid4()), diagnostic_id=identifier, criterion=data["criterion"],
                      title=text(data, "title", 200), body=text(data, "body", 8000), priority=priority)
    db.session.add(action)
    db.session.commit()
    return jsonify(id=action.id), 201


@bp.post("/api/actions/<identifier>/status")
@require_admin_api_token
def change_action(identifier):
    from .models import MemoryEntry, WorkItem
    action = db.get_or_404(WorkItem, identifier)
    data = body()
    status = text(data, "status", 20)
    if status not in {"todo", "in_progress", "done"}:
        raise ValueError("status")
    if action.status != status:
        db.session.add(MemoryEntry(id=str(uuid4()), diagnostic_id=action.diagnostic_id,
                                  work_item_id=action.id, criterion=action.criterion,
                                  kind="status_change", body=f"{action.status} → {status}",
                                  actor=session["admin_username"]))
        action.status = status
        db.session.commit()
    return jsonify(status=status)


@bp.get("/api/diagnostics/<identifier>/context")
def analysis_context(identifier):
    from .analysis import export_context
    get_diagnostic(identifier)
    return jsonify(export_context(identifier))
