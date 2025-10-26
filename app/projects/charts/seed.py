# app/projects/charts/seed.py
from datetime import date, time
from .models import db, Station, Train, Trip, Stop

def seed():
    if Station.query.count() > 0:
        return

    # Ligne simple A—D
    sA = Station(name="A", km=0.0)
    sB = Station(name="B", km=12.5)
    sC = Station(name="C", km=28.0)
    sD = Station(name="D", km=45.0)
    db.session.add_all([sA,sB,sC,sD])

    t1 = Train(code="T101", label="Omnibus matin", color="#4e79a7")
    t2 = Train(code="T201", label="Rapide matin",  color="#f28e2b")
    db.session.add_all([t1, t2])
    db.session.flush()

    trip_date = date.today()
    tr1 = Trip(train_id=t1.id, service_date=trip_date)
    tr2 = Trip(train_id=t2.id, service_date=trip_date)
    db.session.add_all([tr1, tr2])
    db.session.flush()

    # T101 (omnibus)
    db.session.add_all([
        Stop(trip_id=tr1.id, station_id=sA.id, seq=1, arrival=time(8,00), departure=time(8,00)),
        Stop(trip_id=tr1.id, station_id=sB.id, seq=2, arrival=time(8,15), departure=time(8,16)),
        Stop(trip_id=tr1.id, station_id=sC.id, seq=3, arrival=time(8,40), departure=time(8,41)),
        Stop(trip_id=tr1.id, station_id=sD.id, seq=4, arrival=time(9,05), departure=time(9,05)),
    ])

    # T201 (rapide)
    db.session.add_all([
        Stop(trip_id=tr2.id, station_id=sA.id, seq=1, arrival=time(8,20), departure=time(8,20)),
        Stop(trip_id=tr2.id, station_id=sC.id, seq=2, arrival=time(8,48), departure=time(8,48)),
        Stop(trip_id=tr2.id, station_id=sD.id, seq=3, arrival=time(9,02), departure=time(9,02)),
    ])

    db.session.commit()
