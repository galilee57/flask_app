# app/projects/charts/seed.py
from datetime import date, time

from app.extensions import db

from .models import Station, Train

def seed():
    if Station.query.count() > 0:
        return

    # Ligne simple A—D
    sA = Station(name="A", km=0.0)
    sB = Station(name="B", km=12.5)
    sC = Station(name="C", km=28.0)
    sD = Station(name="D", km=45.0)
    db.session.add_all([sA, sB, sC, sD])
    db.session.flush()

    service_date = date.today()
    db.session.add_all([
        Train(
            name="Omnibus matin",
            color="#4e79a7",
            date=service_date,
            station_depart_id=sA.id,
            station_arrivee_id=sD.id,
            heure_depart=time(8, 0),
            heure_arrivee=time(9, 5),
        ),
        Train(
            name="Rapide matin",
            color="#f28e2b",
            date=service_date,
            station_depart_id=sA.id,
            station_arrivee_id=sD.id,
            heure_depart=time(8, 20),
            heure_arrivee=time(9, 2),
        ),
    ])

    db.session.commit()
