# app/projects/charts/models.py
from app.extensions import db

class Station(db.Model):
    __tablename__ = "stations"
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    km   = db.Column(db.Float, nullable=False)

class Train(db.Model):
    __tablename__ = "trains"
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(120), nullable=False)
    color = db.Column(db.String(7))  # ex: "#007bff"

    # trajet simplifié: départ -> arrivée à une date, avec heures
    date = db.Column(db.Date, nullable=False)
    station_depart_id  = db.Column(db.Integer, db.ForeignKey("stations.id"), nullable=False)
    station_arrivee_id = db.Column(db.Integer, db.ForeignKey("stations.id"), nullable=False)
    heure_depart  = db.Column(db.Time, nullable=False)
    heure_arrivee = db.Column(db.Time, nullable=False)

    station_depart  = db.relationship("Station", foreign_keys=[station_depart_id])
    station_arrivee = db.relationship("Station", foreign_keys=[station_arrivee_id])
