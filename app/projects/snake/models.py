from datetime import datetime
from app.extensions import db


class SnakeStat(db.Model):
    __tablename__ = "snake_stats"

    id = db.Column(db.Integer, primary_key=True)

    mode = db.Column(db.String(20), nullable=False)
    # human, astar, astar_nn

    score = db.Column(db.Integer, nullable=False)
    steps_since_fruit = db.Column(db.Integer, nullable=False)
    total_steps = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SnakeResult(db.Model):
    """One completed game; legacy per-fruit SnakeStat rows stay separate."""
    __tablename__ = "snake_result"
    id = db.Column(db.String(64), primary_key=True)
    mode = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_steps = db.Column(db.Integer, nullable=False)
    end_reason = db.Column(db.String(40), nullable=False)
    seed = db.Column(db.Integer)
    model_hash = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "mode": self.mode, "score": self.score,
                "total_steps": self.total_steps, "end_reason": self.end_reason,
                "seed": self.seed, "model_hash": self.model_hash,
                "created_at": self.created_at.isoformat()}
