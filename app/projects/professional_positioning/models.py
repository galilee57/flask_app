"""Private source records and independently serialized public snapshots."""
from datetime import datetime, timezone
from app.extensions import db


def now():
    return datetime.now(timezone.utc)


class Diagnostic(db.Model):
    __tablename__ = "positioning_diagnostics"
    id = db.Column(db.String(36), primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    role = db.Column(db.String(40), nullable=False)
    context = db.Column(db.Text, nullable=False)
    version = db.Column(db.String(20), nullable=False, default="1")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now)


class Profile(db.Model):
    __tablename__ = "positioning_profiles"
    id = db.Column(db.String(36), primary_key=True)
    diagnostic_id = db.Column(db.String(36), db.ForeignKey("positioning_diagnostics.id"), nullable=False)
    name = db.Column(db.String(160), nullable=False)
    url = db.Column(db.Text, nullable=False)
    kind = db.Column(db.String(20), nullable=False)
    rationale = db.Column(db.Text, nullable=False)


class Assessment(db.Model):
    __tablename__ = "positioning_assessments"
    id = db.Column(db.String(36), primary_key=True)
    profile_id = db.Column(db.String(36), db.ForeignKey("positioning_profiles.id"), nullable=False)
    criterion = db.Column(db.String(60), nullable=False)
    finding = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.String(10), nullable=False)
    confidence_reason = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text, nullable=False)
    consulted_at = db.Column(db.DateTime(timezone=True), nullable=False)
    verified_at = db.Column(db.DateTime(timezone=True))
    verified_by = db.Column(db.String(160))
    __table_args__ = (db.UniqueConstraint("profile_id", "criterion"),)


class PublicSnapshot(db.Model):
    __tablename__ = "positioning_snapshots"
    id = db.Column(db.String(36), primary_key=True)
    diagnostic_id = db.Column(db.String(36), db.ForeignKey("positioning_diagnostics.id"), nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    provenance = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now)
    published_at = db.Column(db.DateTime(timezone=True))


class AnalysisRun(db.Model):
    """Append-only analytical revision; source observations belong to this run."""
    __tablename__ = "positioning_analysis_runs"
    id = db.Column(db.String(36), primary_key=True)
    diagnostic_id = db.Column(db.String(36), db.ForeignKey("positioning_diagnostics.id"), nullable=False)
    parent_id = db.Column(db.String(36), db.ForeignKey("positioning_analysis_runs.id"))
    import_key = db.Column(db.String(160), unique=True, nullable=False)
    payload_hash = db.Column(db.String(64), nullable=False)
    memory_entry_ids = db.Column(db.JSON, nullable=False, default=list)
    actor = db.Column(db.String(160), nullable=False)
    rubric = db.Column(db.JSON, nullable=False)
    summary = db.Column(db.JSON, nullable=False)
    limitations = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now)


class PortfolioReview(db.Model):
    __tablename__ = "positioning_portfolio_reviews"
    id = db.Column(db.String(36), primary_key=True)
    run_id = db.Column(db.String(36), db.ForeignKey("positioning_analysis_runs.id"), nullable=False)
    profile_id = db.Column(db.String(36), db.ForeignKey("positioning_profiles.id"), nullable=False)
    origin_url = db.Column(db.Text, nullable=False)
    role_label = db.Column(db.String(160), nullable=False)
    comparability = db.Column(db.String(20), nullable=False)
    scope = db.Column(db.Text, nullable=False)
    sources = db.Column(db.JSON, nullable=False)
    __table_args__ = (db.UniqueConstraint("run_id", "profile_id"),)


class ReviewObservation(db.Model):
    __tablename__ = "positioning_review_observations"
    id = db.Column(db.String(36), primary_key=True)
    review_id = db.Column(db.String(36), db.ForeignKey("positioning_portfolio_reviews.id"), nullable=False)
    criterion = db.Column(db.String(60), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    finding = db.Column(db.JSON, nullable=False)
    confidence = db.Column(db.String(10), nullable=False)
    confidence_reason = db.Column(db.JSON, nullable=False)
    source_keys = db.Column(db.JSON, nullable=False)
    __table_args__ = (db.UniqueConstraint("review_id", "criterion"),)


class WorkItem(db.Model):
    __tablename__ = "positioning_work_items"
    id = db.Column(db.String(36), primary_key=True)
    diagnostic_id = db.Column(db.String(36), db.ForeignKey("positioning_diagnostics.id"), nullable=False)
    criterion = db.Column(db.String(60), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="todo")
    priority = db.Column(db.String(10), nullable=False, default="medium")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now)


class MemoryEntry(db.Model):
    """Comments and supplied evidence are preserved, including action changes."""
    __tablename__ = "positioning_memory_entries"
    id = db.Column(db.String(36), primary_key=True)
    diagnostic_id = db.Column(db.String(36), db.ForeignKey("positioning_diagnostics.id"), nullable=False)
    run_id = db.Column(db.String(36), db.ForeignKey("positioning_analysis_runs.id"))
    work_item_id = db.Column(db.String(36), db.ForeignKey("positioning_work_items.id"))
    criterion = db.Column(db.String(60))
    kind = db.Column(db.String(20), nullable=False)
    body = db.Column(db.Text, nullable=False)
    actor = db.Column(db.String(160), nullable=False)
    evidence = db.Column(db.JSON)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now)
