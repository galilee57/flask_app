"""Application Flask de sélection des stations et d'analyse d'enneigement."""
from __future__ import annotations

from datetime import date
import argparse
import requests
from flask import current_app, jsonify, render_template, request
from sqlalchemy import select, func
from . import bp
from app.core.security import require_admin_api_token
from app.extensions import db

from app.projects.snow_layers.demo_data import DEMO_SEASONS
from app.projects.snow_layers.import_open_meteo import parse_season
from app.projects.snow_layers.models import SnowObservation, SnowStation as Station, SnowImport
from app.projects.snow_layers.open_meteo import SOURCE_NAME, fetch_daily_snow_depth
from app.projects.snow_layers.repository import get_or_create_station, load_seasons, upsert_observations, load_station_means
from app.projects.snow_layers.stations import STATIONS, STATIONS_BY_SLUG, CATALOG_NOTE


def _comparison_payload(session, selected_slugs: list[str]) -> dict:
    """Construit les moyennes saisonnières station et catégorie en centimètres."""
    means = load_station_means(session)
    station_means = {station["slug"]: means.get(station["slug"], {}) for station in STATIONS}
    all_seasons = sorted({season for values in station_means.values() for season in values})
    categories = {}
    for category in ("basse", "moyenne", "haute"):
        members = [station["slug"] for station in STATIONS if station["altitude_category"] == category]
        categories[category] = {}
        for season in all_seasons:
            values = [station_means[slug][season] for slug in members if season in station_means[slug]]
            if values:
                categories[category][season] = {
                    "min": round(min(values), 1), "max": round(max(values), 1),
                    "mean": round(sum(values) / len(values), 1), "count": len(values),
                }
    return {
        "unit": "cm", "seasons": all_seasons,
        "stations": {
            slug: {"name": STATIONS_BY_SLUG[slug]["name"], "category": STATIONS_BY_SLUG[slug]["altitude_category"], "values": station_means[slug]}
            for slug in selected_slugs
        },
        "categories": categories,
    }


@bp.get('/')
def index():
    year = date.today().year - (date.today().month < 5)
    return render_template('snow_layers/index.html', can_import=not current_app.config.get('REQUIRE_ADMIN_API_TOKEN', True), import_seasons=[f'{y-1}-{y}' for y in range(year, year-10, -1)])

@bp.get('/api/stations')
def stations():
    return jsonify(stations=STATIONS, note=CATALOG_NOTE)

@bp.get('/api/snow-depth')
def snow_depth():
    slug = request.args.get('station', 'meribel')
    definition = STATIONS_BY_SLUG.get(slug)
    if definition is None:
        return jsonify(error='Station inconnue.'), 404
    seasons = load_seasons(db.session, slug)
    latest = db.session.scalar(select(func.max(SnowImport.imported_at))
        .select_from(SnowObservation)
        .join(Station, Station.id == SnowObservation.station_id)
        .join(SnowImport, SnowImport.id == SnowObservation.import_id)
        .where(Station.slug == slug))
    is_demo = not seasons and slug == 'meribel'
    return jsonify(station=definition['name'], station_slug=slug,
                   location=definition, unit='cm', is_demo=is_demo,
                   source=SOURCE_NAME if seasons else ('Données de démonstration · simulées' if is_demo else 'Aucune donnée locale pour cette station.'),
                   collected_at=latest.isoformat() if latest else None,
                   seasons=seasons or (DEMO_SEASONS if is_demo else {}))

@bp.get('/api/comparison')
def comparison():
    requested = request.args.getlist('station')
    if len(requested) == 1 and ',' in requested[0]:
        requested = requested[0].split(',')
    selected = [slug for slug in dict.fromkeys(requested) if slug in STATIONS_BY_SLUG]
    if len(selected) != 2:
        return jsonify(error='Sélectionnez exactement deux stations.'), 400
    return jsonify(_comparison_payload(db.session, selected))

@bp.post('/api/snow-depth/import')
@require_admin_api_token
def import_depth():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify(error='Requête JSON attendue.'), 400
    slug, season = body.get('station'), body.get('season')
    definition = STATIONS_BY_SLUG.get(slug) if isinstance(slug, str) else None
    if definition is None:
        return jsonify(error='Station inconnue.'), 404
    try:
        if not isinstance(season, str):
            raise ValueError()
        start, end = parse_season(season)
        if start.year < 1950 or end >= date.today():
            raise ValueError()
    except (ValueError, argparse.ArgumentTypeError):
        return jsonify(error='Choisissez une saison terminée, depuis 1950, au format AAAA-AAAA.'), 400
    cached = load_seasons(db.session, slug).get(season, [])
    if len(cached) == (end-start).days + 1 and cached[0]['date'] == start.isoformat() and cached[-1]['date'] == end.isoformat():
        return jsonify(cached=True, count=len(cached))
    try:
        records, source_url = fetch_daily_snow_depth(
            latitude=definition['latitude'], longitude=definition['longitude'],
            elevation_m=definition['elevation_m'], start_date=start, end_date=end)
        if not records:
            return jsonify(error='Open-Meteo ne renvoie aucune donnée pour cette période.'), 502
    except (requests.RequestException, KeyError, ValueError, TypeError):
        return jsonify(error='Open-Meteo est indisponible. Réessayez plus tard ; les données locales sont conservées.'), 502
    try:
        station = get_or_create_station(db.session, definition)
        upsert_observations(db.session, station=station, records=records, source=SOURCE_NAME, source_url=source_url)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return jsonify(cached=False, count=len(records), partial=len(records) != (end-start).days+1)

