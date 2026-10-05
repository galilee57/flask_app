"""Normalized snow history in the application's shared database."""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, ForeignKeyConstraint, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class SnowStation(db.Model):
    __tablename__ = "snow_stations"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    elevation_m: Mapped[float] = mapped_column(Float)


class SnowSource(db.Model):
    __tablename__ = "snow_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)


class SnowImport(db.Model):
    __tablename__ = "snow_imports"
    __table_args__ = (
        UniqueConstraint("source_id", "source_url", "imported_at", name="uq_snow_import_provenance"),
        UniqueConstraint("id", "source_id", name="uq_snow_import_source"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("snow_sources.id"))
    source_url: Mapped[str] = mapped_column(String(500))
    # UTC, stored without timezone to preserve the original SQLite timestamps.
    imported_at: Mapped[datetime] = mapped_column(DateTime)


class SnowObservation(db.Model):
    __tablename__ = "snow_daily_observations"
    __table_args__ = (
        UniqueConstraint("station_id", "observed_on", "source_id", name="uq_snow_daily_station_date_source"),
        ForeignKeyConstraint(["import_id", "source_id"],
                             ["snow_imports.id", "snow_imports.source_id"],
                             name="fk_snow_daily_import_source"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[int] = mapped_column(ForeignKey("snow_stations.id"))
    observed_on: Mapped[date] = mapped_column(Date, index=True)
    snow_depth_cm: Mapped[float] = mapped_column(Float)
    source_id: Mapped[int] = mapped_column(ForeignKey("snow_sources.id"))
    import_id: Mapped[int] = mapped_column()


class SnowSeedRun(db.Model):
    __tablename__ = "snow_seed_runs"

    digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
