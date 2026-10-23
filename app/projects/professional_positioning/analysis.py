"""Validate, append and compare sourced analyses without ranking people."""
import hashlib
import json
from uuid import uuid4

from app.extensions import db
from .models import (
    AnalysisRun, Diagnostic, MemoryEntry, PortfolioReview, Profile,
    ReviewObservation, WorkItem,
)
from .services import consultation, text, url

STATUSES = {"demonstrated", "claimed", "not_documented", "not_assessable"}
METHODS = {"web_open", "browser_dom", "local_render", "repository"}


def bilingual(value):
    if not isinstance(value, dict):
        raise ValueError("translation")
    return {lang: text(value, lang, 12000) for lang in ("fr", "en")}


def validate_analysis(data):
    if not isinstance(data, dict) or data.get("schema_version") != 2:
        raise ValueError("schema_version")
    text(data, "import_key", 160)
    text(data, "actor", 160)
    text(data, "title", 160)
    text(data, "context", 12000)
    rubric = data.get("rubric")
    if not isinstance(rubric, list) or not 1 <= len(rubric) <= 30:
        raise ValueError("rubric")
    keys = set()
    for c in rubric:
        key = text(c, "key", 60)
        if key in keys:
            raise ValueError("duplicate_criterion")
        keys.add(key)
        bilingual(c["label"])
        bilingual(c["definition"])
    for field in ("summary", "limitations"):
        if not isinstance(data.get(field), list) or not data[field]:
            raise ValueError(field)
        for item in data[field]:
            bilingual(item)
    reviews = data.get("reviews")
    if not isinstance(reviews, list) or not 2 <= len(reviews) <= 100:
        raise ValueError("reviews")
    origins = set()
    portfolios = 0
    for review in reviews:
        origin = url(review, "origin_url")
        if origin in origins:
            raise ValueError("duplicate_origin")
        origins.add(origin)
        if review.get("kind") not in {"portfolio", "reference"}:
            raise ValueError("kind")
        portfolios += review["kind"] == "portfolio"
        for field in ("name", "role_label", "scope"):
            text(review, field, 4000 if field == "scope" else 160)
        if review.get("comparability") not in {"target", "exact", "adjacent"}:
            raise ValueError("comparability")
        sources = review.get("sources")
        if not isinstance(sources, list) or not sources:
            raise ValueError("sources")
        source_keys = set()
        for source in sources:
            key = text(source, "key", 60)
            if key in source_keys:
                raise ValueError("duplicate_source")
            source_keys.add(key)
            url(source)
            text(source, "excerpt", 2000)
            consultation(source)
            if source.get("method") not in METHODS:
                raise ValueError("method")
            if source.get("kind") not in {"self_report", "artifact", "scope"}:
                raise ValueError("source_kind")
        observations = review.get("observations")
        if not isinstance(observations, list) or {o.get("criterion") for o in observations} != keys or len(observations) != len(keys):
            raise ValueError("observations")
        for o in observations:
            if o.get("status") not in STATUSES or o.get("confidence") not in {"low", "medium", "high"}:
                raise ValueError("status_or_confidence")
            bilingual(o["finding"])
            bilingual(o["confidence_reason"])
            refs = o.get("source_keys")
            if not isinstance(refs, list) or not refs or not set(refs) <= source_keys:
                raise ValueError("observation_sources")
            if o["status"] in {"demonstrated", "claimed"}:
                evidence = [s for s in sources if s["key"] in refs]
                if all(s["kind"] == "scope" for s in evidence):
                    raise ValueError("positive_without_evidence")
                if o["status"] == "demonstrated" and not any(s["kind"] == "artifact" for s in evidence):
                    raise ValueError("demonstrated_without_artifact")
    if portfolios != 1:
        raise ValueError("one_portfolio_required")
    for action in data.get("actions", []):
        if action.get("criterion") not in keys or action.get("priority", "medium") not in {"high", "medium", "low"}:
            raise ValueError("action")
        text(action, "title", 200)
        text(action, "body", 8000)
    return data


def import_analysis(data, diagnostic_id=None, parent_id=None):
    """Append a complete immutable run; caller commits atomically."""
    validate_analysis(data)
    digest = hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    existing = db.session.scalar(db.select(AnalysisRun).where(AnalysisRun.import_key == data["import_key"]))
    if existing:
        if existing.payload_hash != digest or (diagnostic_id and existing.diagnostic_id != diagnostic_id):
            raise ValueError("import_key_conflict")
        return existing, False
    if diagnostic_id:
        diagnostic = db.session.get(Diagnostic, diagnostic_id)
        if not diagnostic or diagnostic.role != "ai_solutions_engineering":
            raise ValueError("diagnostic")
    else:
        diagnostic = Diagnostic(id=str(uuid4()), title=data["title"], role="ai_solutions_engineering", context=data["context"], version="2")
        db.session.add(diagnostic)
        db.session.flush()
    previous = db.session.scalars(db.select(AnalysisRun).where(AnalysisRun.diagnostic_id == diagnostic.id).order_by(AnalysisRun.created_at.desc())).first()
    if previous and not parent_id:
        raise ValueError("parent_required_for_amendment")
    if parent_id and (not previous or previous.id != parent_id):
        raise ValueError("parent_must_be_latest")
    memory_ids = data.get("memory_entry_ids", [])
    if not isinstance(memory_ids, list) or len(set(memory_ids)) != len(memory_ids):
        raise ValueError("memory_entry_ids")
    for memory_id in memory_ids:
        entry = db.session.get(MemoryEntry, memory_id)
        if not entry or entry.diagnostic_id != diagnostic.id:
            raise ValueError("memory_entry_scope")
    run = AnalysisRun(id=str(uuid4()), diagnostic_id=diagnostic.id,
                      parent_id=previous.id if previous else None,
                      import_key=data["import_key"], payload_hash=digest,
                      actor=data["actor"], memory_entry_ids=memory_ids, rubric=data["rubric"],
                      summary=data["summary"], limitations=data["limitations"])
    db.session.add(run)
    db.session.flush()
    for review in data["reviews"]:
        profile = db.session.scalar(db.select(Profile).where(Profile.diagnostic_id == diagnostic.id, Profile.url == review["origin_url"]))
        if profile is None:
            profile = Profile(id=str(uuid4()), diagnostic_id=diagnostic.id,
                              name=review["name"], url=review["origin_url"],
                              kind=review["kind"], rationale=review["scope"])
            db.session.add(profile)
            db.session.flush()
        elif profile.kind != review["kind"]:
            raise ValueError("profile_kind_conflict")
        record = PortfolioReview(id=str(uuid4()), run_id=run.id, profile_id=profile.id,
                                 origin_url=review["origin_url"], role_label=review["role_label"],
                                 comparability=review["comparability"], scope=review["scope"], sources=review["sources"])
        db.session.add(record)
        db.session.flush()
        for o in review["observations"]:
            db.session.add(ReviewObservation(id=str(uuid4()), review_id=record.id, **o))
    for action in data.get("actions", []) if previous is None else []:
        if action.get("criterion") not in {c["key"] for c in run.rubric}:
            raise ValueError("action_criterion")
        db.session.add(WorkItem(id=str(uuid4()), diagnostic_id=diagnostic.id,
                               criterion=action["criterion"], title=text(action, "title", 200),
                               body=text(action, "body", 8000), status="todo",
                               priority=action.get("priority", "medium")))
    db.session.flush()
    return run, True


def run_view(run):
    records = db.session.execute(db.select(PortfolioReview, Profile).join(Profile).where(PortfolioReview.run_id == run.id).order_by(Profile.kind, Profile.name)).all()
    observations = db.session.scalars(db.select(ReviewObservation).join(PortfolioReview).where(PortfolioReview.run_id == run.id)).all()
    by_review = {}
    for o in observations:
        by_review.setdefault(o.review_id, {})[o.criterion] = o
    reviews = [{"review": r, "profile": p, "observations": by_review.get(r.id, {})} for r, p in records]
    references = [r for r in reviews if r["profile"].kind == "reference"]
    target = next(r for r in reviews if r["profile"].kind == "portfolio")
    comparison = []
    for criterion in run.rubric:
        key = criterion["key"]
        positive = [r for r in references if r["observations"][key].status in {"claimed", "demonstrated"}]
        comparison.append({"criterion": criterion, "target": target["observations"][key],
                           "positive": positive, "count": len(positive), "total": len(references),
                           "unassessable": sum(r["observations"][key].status == "not_assessable" for r in references)})
    return {"reviews": reviews, "references": references, "target": target, "comparison": comparison}


def export_context(diagnostic_id):
    """Complete private context for the next Codex analysis, including citations."""
    diagnostic = db.session.get(Diagnostic, diagnostic_id)
    if diagnostic is None:
        raise ValueError("diagnostic")
    runs = db.session.scalars(db.select(AnalysisRun).where(AnalysisRun.diagnostic_id == diagnostic_id).order_by(AnalysisRun.created_at)).all()
    history = []
    for run in runs:
        view = run_view(run)
        history.append({
            "id": run.id, "parent_id": run.parent_id,
            "created_at": run.created_at.isoformat(), "actor": run.actor,
            "rubric": run.rubric, "summary": run.summary,
            "limitations": run.limitations, "memory_entry_ids": run.memory_entry_ids,
            "reviews": [
                {"profile_id": r["profile"].id, "name": r["profile"].name,
                 "kind": r["profile"].kind, "origin_url": r["review"].origin_url,
                 "role_label": r["review"].role_label,
                 "comparability": r["review"].comparability,
                 "scope": r["review"].scope, "sources": r["review"].sources,
                 "observations": [
                     {"criterion": o.criterion, "status": o.status,
                      "finding": o.finding, "confidence": o.confidence,
                      "confidence_reason": o.confidence_reason,
                      "source_keys": o.source_keys}
                     for o in r["observations"].values()
                 ]}
                for r in view["reviews"]
            ],
        })
    memory = db.session.scalars(db.select(MemoryEntry).where(MemoryEntry.diagnostic_id == diagnostic_id).order_by(MemoryEntry.created_at)).all()
    actions = db.session.scalars(db.select(WorkItem).where(WorkItem.diagnostic_id == diagnostic_id)).all()
    return {
        "diagnostic_id": diagnostic.id, "title": diagnostic.title,
        "context": diagnostic.context, "latest_run": runs[-1].id if runs else None,
        "runs": history,
        "memory": [{"id": n.id, "run_id": n.run_id, "kind": n.kind,
                    "criterion": n.criterion, "body": n.body, "actor": n.actor,
                    "evidence": n.evidence, "created_at": n.created_at.isoformat()}
                   for n in memory],
        "actions": [{"id": a.id, "criterion": a.criterion, "title": a.title,
                     "body": a.body, "status": a.status, "priority": a.priority}
                    for a in actions],
    }
