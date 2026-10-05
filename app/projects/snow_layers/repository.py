"""Persistance et lecture des séries de neige pour l'application."""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import select, case, extract, func
from sqlalchemy.orm import Session

from app.projects.snow_layers.models import SnowObservation, SnowStation as Station, SnowSource, SnowImport


MERIBEL = {
    "slug": "meribel",
    "name": "Méribel",
    "latitude": 45.41497,
    "longitude": 6.5650,
    "elevation_m": 1450.0,
}


def get_or_create_station(session: Session, definition: dict) -> Station:
    station = session.scalar(select(Station).where(Station.slug == definition["slug"]))
    if station is None:
        station = Station(**{key: definition[key] for key in MERIBEL})
        session.add(station)
        session.flush()
    return station


def get_or_create_meribel(session: Session) -> Station:
    return get_or_create_station(session, MERIBEL)


def upsert_observations(
    session: Session, *, station: Station, records: list[tuple[date, float]], source: str, source_url: str
) -> int:
    if not records:
        return 0
    source_row = session.scalar(select(SnowSource).where(SnowSource.name == source))
    if source_row is None:
        source_row = SnowSource(name=source)
        session.add(source_row)
        session.flush()
    provenance = SnowImport(source_id=source_row.id, source_url=source_url,
                            imported_at=datetime.now(timezone.utc).replace(tzinfo=None))
    session.add(provenance)
    session.flush()
    existing = {
        row.observed_on: row for row in session.scalars(select(SnowObservation).where(
            SnowObservation.station_id == station.id,
            SnowObservation.source_id == source_row.id,
            SnowObservation.observed_on.in_([day for day, _ in records]),
        ))
    }
    for observed_on, snow_depth_cm in records:
        observation = existing.get(observed_on)
        if observation is None:
            observation = SnowObservation(station_id=station.id, observed_on=observed_on,
                                          source_id=source_row.id)
            session.add(observation)
            existing[observed_on] = observation
        observation.snow_depth_cm = snow_depth_cm
        observation.import_id = provenance.id
    return len(records)


def season_for(day: date) -> str:
    start_year = day.year if day.month >= 7 else day.year - 1
    return f"{start_year}-{start_year + 1}"


def load_seasons(session: Session, station_slug: str = "meribel") -> dict[str, list[dict[str, str | float]]]:
    rows = session.execute(
        select(SnowObservation).join(Station).where(Station.slug == station_slug).order_by(SnowObservation.observed_on)
    ).scalars()
    seasons: dict[str, list[dict[str, str | float]]] = {}
    for observation in rows:
        # Une saison comparative couvre l'hiver météorologique retenu par
        # l'import : décembre à avril. Les gros téléchargements historiques
        # peuvent aussi contenir les mois d'été entre deux hivers.
        if observation.observed_on.month not in (12, 1, 2, 3, 4):
            continue
        seasons.setdefault(season_for(observation.observed_on), []).append(
            {"date": observation.observed_on.isoformat(), "depth_cm": observation.snow_depth_cm}
        )
    return seasons


def load_station_means(session):
    """Aggregate in SQL instead of loading half a million ORM objects."""
    month = extract("month", SnowObservation.observed_on)
    year = extract("year", SnowObservation.observed_on)
    start_year = case((month == 12, year), else_=year - 1)
    rows = session.execute(select(Station.slug, start_year.label("start_year"),
                                  func.avg(SnowObservation.snow_depth_cm))
                           .join(SnowObservation, Station.id == SnowObservation.station_id)
                           .where(month.in_([12, 1, 2, 3, 4]))
                           .group_by(Station.slug, start_year))
    result = {}
    for slug, year, mean in rows:
        year = int(year)
        result.setdefault(slug, {})[f"{year}-{year + 1}"] = round(mean, 1)
    return result
