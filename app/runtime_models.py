"""Shared deployment storage; created exclusively through Alembic."""
from app.extensions import db


class Todo(db.Model):
    __tablename__ = "todo"
    id = db.Column(db.String(36), primary_key=True)
    text = db.Column(db.Text, nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.String(40), nullable=False)

    def to_dict(self):
        return {key: getattr(self, key) for key in ("id", "text", "done", "created_at")}


class SavedPattern(db.Model):
    __tablename__ = "saved_pattern"
    name = db.Column(db.String(80), primary_key=True)
    payload = db.Column(db.JSON, nullable=False)


class RuntimeSession(db.Model):
    __tablename__ = "runtime_session"
    id = db.Column(db.String(64), primary_key=True)
    payload = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.BigInteger, nullable=False, index=True)
    version = db.Column(db.Integer, nullable=False, default=1)
