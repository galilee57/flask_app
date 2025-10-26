from datetime import datetime, date, time as dtime
from flask import Blueprint, request, render_template
from flask_restful import Api, Resource, abort
from app.extensions import db
from .models import Station, Train
import re
from . import bp

api = Api(bp)

@bp.route("/")
def index():
    return render_template("index_charts.html")

# ---------- helpers ----------
def parse_date(v: str) -> date:
    v = v.strip()
    # 1) ISO: 2025-10-17
    try:
        return datetime.fromisoformat(v).date()
    except Exception:
        pass
    # 2) FR: 17/10/2025
    m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", v)
    if m:
        d, mth, y = map(int, m.groups())
        return date(y, mth, d)
    # 3) Tentative générique: 17-10-2025
    m = re.match(r"^(\d{2})[-\.](\d{2})[-\.](\d{4})$", v)
    if m:
        d, mth, y = map(int, m.groups())
        return date(y, mth, d)
    from flask_restful import abort
    abort(400, message="Date invalide (attendu YYYY-MM-DD ou JJ/MM/AAAA)")

def parse_time(v):
    try:
        h, m, *s = map(int, v.split(":"))
        return dtime(h, m, s[0] if s else 0)
    except:
        abort(400, message="Heure invalide (HH:MM ou HH:MM:SS)")

def station_dto(s): return {"id": s.id, "name": s.name, "km": s.km}

def train_dto(t):
    return {
        "id": t.id,
        "name": t.name,
        "color": t.color,
        "date": t.date.isoformat(),
        "station_depart": {"id": t.station_depart.id, "name": t.station_depart.name, "km": t.station_depart.km},
        "station_arrivee": {"id": t.station_arrivee.id, "name": t.station_arrivee.name, "km": t.station_arrivee.km},
        "heure_depart": t.heure_depart.isoformat(),
        "heure_arrivee": t.heure_arrivee.isoformat(),
    }

# ---------- ressources REST ----------
class StationList(Resource):
    def get(self):
        return {"items": [station_dto(s) for s in Station.query.order_by(Station.km)]}
    def post(self):
        d = request.get_json(force=True)
        if not {"name", "km"} <= d.keys():
            abort(400, message="Champs 'name' et 'km' requis")
        s = Station(name=d["name"], km=float(d["km"]))
        db.session.add(s)
        db.session.commit()
        return station_dto(s), 201

class TrainList(Resource):
    def get(self):
        q = Train.query
        if "date" in request.args:
            q = q.filter(Train.date == parse_date(request.args["date"]))
        return {"items": [train_dto(t) for t in q.order_by(Train.date, Train.id)]}
    def post(self):
        d = request.get_json(force=True)
        required = {"name","color","date","station_depart_id","station_arrivee_id","heure_depart","heure_arrivee"}
        if not required <= d.keys():
            abort(400, message=f"Champs manquants: {', '.join(sorted(required - d.keys()))}")
        t = Train(
            name=d["name"],
            color=d["color"],
            date=parse_date(d["date"]),
            station_depart_id=int(d["station_depart_id"]),
            station_arrivee_id=int(d["station_arrivee_id"]),
            heure_depart=parse_time(d["heure_depart"]),
            heure_arrivee=parse_time(d["heure_arrivee"]),
        )
        db.session.add(t)
        db.session.commit()
        return train_dto(t), 201

class Marey(Resource):
    """Prépare les données pour le diagramme de Marey"""
    def get(self):
        the_date = parse_date(request.args["date"]) if "date" in request.args else date.today()
        trains = Train.query.filter(Train.date == the_date).all()

        datasets = []
        for t in trains:
            x1 = datetime.combine(t.date, t.heure_depart).isoformat()
            x2 = datetime.combine(t.date, t.heure_arrivee).isoformat()
            datasets.append({
                "label": t.name,
                "borderColor": t.color,
                "backgroundColor": t.color,
                "showLine": True,
                "borderWidth": 2,
                "pointRadius": 2,
                "tension": 0,
                "data": [
                    {"x": x1, "y": float(t.station_depart.km)},
                    {"x": x2, "y": float(t.station_arrivee.km)}
                ]
            })
        stations = [station_dto(s) for s in Station.query.order_by(Station.km)]
        return {"datasets": datasets, "stations": stations}

# ---------- Enregistrement ----------
api.add_resource(StationList, "/api/stations")
api.add_resource(TrainList, "/api/trains")
api.add_resource(Marey, "/api/marey")
