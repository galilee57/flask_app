"""Explicit, atomic CLI imports for Codex research sessions."""
import json
from hmac import compare_digest
from pathlib import Path

import click
from flask import current_app
from flask.cli import with_appcontext

from app.extensions import db
from .analysis import import_analysis, validate_analysis


@click.command("positioning-import")
@click.argument("source", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--diagnostic", "diagnostic_id")
@click.option("--parent", "parent_id")
@click.option("--apply", is_flag=True, help="Persist the validated revision; default is validation only.")
@click.option("--admin-token", envvar="POSITIONING_ADMIN_TOKEN", default="", help="Required for production writes; prefer the environment variable.")
@with_appcontext
def import_command(source, diagnostic_id, parent_id, apply, admin_token):
    if source.stat().st_size > 5_000_000:
        raise click.ClickException("Import exceeds 5 MB")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
        validate_analysis(payload)
        if not apply:
            click.echo(f"Valid: {len(payload['reviews'])} portfolios; no database changes.")
            return
        expected = current_app.config.get("ADMIN_API_TOKEN") or ""
        if current_app.config.get("REQUIRE_ADMIN_API_TOKEN") and (not expected or not compare_digest(expected, admin_token)):
            raise click.ClickException("Administrator write token required")
        run, created = import_analysis(payload, diagnostic_id, parent_id)
        db.session.commit()
        click.echo(f"{'Created' if created else 'Already imported'}: run {run.id}")
        click.echo(f"/projects/professional_positioning/diagnostics/{run.diagnostic_id}/dashboard?run={run.id}")
    except (ValueError, KeyError, TypeError) as exc:
        db.session.rollback()
        raise click.ClickException(f"Invalid analysis: {exc}") from exc


@click.command("positioning-context")
@click.argument("diagnostic_id", required=False)
@click.option("--output", required=True, type=click.Path(dir_okay=False, path_type=Path))
@with_appcontext
def context_command(diagnostic_id, output):
    from .analysis import export_context
    destination = output.resolve()
    # Context includes private URLs and comments: keep it outside static/Git assets.
    if not destination.is_relative_to(Path(current_app.instance_path).resolve()):
        raise click.ClickException("Private context must be written under the instance directory")
    if diagnostic_id is None:
        from .models import AnalysisRun
        latest = db.session.scalars(
            db.select(AnalysisRun).order_by(AnalysisRun.created_at.desc())
        ).first()
        if latest is None:
            raise click.ClickException("No analysis available")
        diagnostic_id = latest.diagnostic_id
    try:
        payload = export_context(diagnostic_id)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    import os
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        os.fchmod(handle.fileno(), 0o600)
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    click.echo(f"Private context saved: {destination}")
