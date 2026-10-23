"""Versioned editorial rubric; no inference from missing evidence."""
from datetime import datetime, timezone
from urllib.parse import urlsplit

ROLES = {
    "industrial_ai": "Industrial AI",
    "agentic_ai": "Agentic AI",
    "ai_solutions_engineering": "AI Solutions Engineering",
}
CRITERIA = {
    "industrial_ai": [("problem", "Problème industriel", "Industrial problem"), ("data", "Données terrain", "Field data"), ("validation", "Validation expérimentale", "Experimental validation"), ("deployment", "Contraintes opérationnelles", "Operational constraints"), ("impact", "Impact mesuré", "Measured impact")],
    "agentic_ai": [("tools", "Orchestration et outils", "Orchestration and tools"), ("state", "Gestion de l’état", "State management"), ("evaluation", "Évaluations", "Evaluations"), ("control", "Contrôle des actions", "Action control"), ("operations", "Observabilité et exploitation", "Observability and operations")],
    "ai_solutions_engineering": [("needs", "Cadrage du besoin", "Needs assessment"), ("architecture", "Architecture et intégrations", "Architecture and integrations"), ("prototype", "Prototype", "Prototype"), ("production", "Mise en production", "Production delivery"), ("outcomes", "Résultats et transmission", "Outcomes and handover")],
}


def text(data, key, limit=4000):
    value = data.get(key)
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(key)
    return value.strip()


def url(data, key="url"):
    value = text(data, key, 2048)
    parsed = urlsplit(value)
    if parsed.scheme not in ("https", "http") or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError(key)
    return value


def consultation(data):
    value = datetime.fromisoformat(text(data, "consulted_at", 50).replace("Z", "+00:00"))
    if value.tzinfo is None or value > datetime.now(timezone.utc):
        raise ValueError("consulted_at")
    return value.astimezone(timezone.utc)


def aggregate(diagnostic, profiles, assessments):
    # Public output is constructed from an allowlist, never from source serialization.
    # Counts below five and their denominators are suppressed together.
    references = {p.id for p in profiles if p.kind == "reference"}
    rows = []
    for key, fr, en in CRITERIA[diagnostic.role]:
        count = len({a.profile_id for a in assessments if a.profile_id in references and a.criterion == key and a.verified_at})
        rows.append({"criterion": key, "count": count if count >= 5 else None})
    disclosed = {row["criterion"] for row in rows if row["count"] is not None}
    dates = [
        a.consulted_at.year for a in assessments
        if a.profile_id in references and a.verified_at and a.criterion in disclosed
    ]
    return {"observation_years": [min(dates), max(dates)] if len(references) >= 5 and dates else None, "role": diagnostic.role, "rubric_version": diagnostic.version,
            "minimum_group": 5, "rows": rows,
            "method": "manual_verified_reference_coverage",
            "generated_on": datetime.now(timezone.utc).date().isoformat()}


def freeze_provenance(diagnostic, profiles, assessments):
    """Retain source details privately so later edits cannot rewrite the audit."""
    return {
        "context": diagnostic.context,
        "profiles": [
            {"id": p.id, "name": p.name, "url": p.url,
             "kind": p.kind, "rationale": p.rationale}
            for p in profiles
        ],
        "assessments": [
            {
                "id": a.id,
                "profile_id": a.profile_id,
                "criterion": a.criterion,
                "finding": a.finding,
                "url": a.url,
                "excerpt": a.excerpt,
                "consulted_at": a.consulted_at.isoformat(),
                "confidence": a.confidence,
                "confidence_reason": a.confidence_reason,
                "verified_at": a.verified_at.isoformat() if a.verified_at else None,
                "verified_by": a.verified_by,
            }
            for a in assessments
        ],
    }
