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