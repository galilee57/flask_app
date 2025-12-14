from datetime import datetime
from app.extensions import db

class Programme(db.Model):
    __tablename__ = 'programmes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    exercices = db.relationship(
        "ProgrammeExercice",
        back_populates="programme",
        cascade="all, delete-orphan",
    )

class ProgrammeExercice(db.Model):
    __tablename__ = 'programme_exercices'
    
    id = db.Column(db.Integer, primary_key=True)
    programme_id = db.Column(db.Integer, db.ForeignKey('programmes.id'), nullable=False)
    
    exercice_id = db.Column(db.String(200), nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    
    programme = db.relationship('Programme', back_populates='exercices')