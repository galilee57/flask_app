"""Database-backed sessions with signed opaque cookies and bounded lifetime."""
import hashlib
import secrets
import time

import click
from flask import session, jsonify
from flask.sessions import SessionInterface, SecureCookieSession
from itsdangerous import BadSignature, URLSafeSerializer
from sqlalchemy import create_engine, delete, insert, select, text, update
from flask.json.tag import TaggedJSONSerializer

from app.extensions import db
from app.storage.runtime_models import RuntimeSession


class SharedSession(SecureCookieSession):
    def __init__(self, data=None, sid=None, version=0):
        super().__init__(data)
        self.sid = sid or secrets.token_hex(32)
        self.version = version
        self.connection = None


class DatabaseSessionInterface(SessionInterface):
    serializer = TaggedJSONSerializer()

    def engine(self, app):
        return app.extensions.get("session_engine", db.engine)

    def signer(self, app):
        return URLSafeSerializer(app.secret_key, salt="database-session-v1")

    def open_session(self, app, request):
        if request.path.startswith("/health/"):
            return SharedSession()
        cookie = request.cookies.get(self.get_cookie_name(app))
        sid = None
        if cookie:
            try:
                sid = self.signer(app).loads(cookie)
            except BadSignature:
                pass
        if not isinstance(sid, str) or len(sid) != 64:
            return SharedSession()
        connection = self.engine(app).connect()
        try:
            # Serialize requests for the same visitor across workers/platforms.
            if connection.dialect.name == "postgresql":
                key = int.from_bytes(hashlib.sha256(sid.encode()).digest()[:8], "big", signed=True)
                connection.execute(text("SET LOCAL lock_timeout = '5s'"))
                connection.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": key})
            row = connection.execute(select(RuntimeSession.__table__).where(
                RuntimeSession.id == sid, RuntimeSession.expires_at > int(time.time())
            )).mappings().first()
            if row is None:
                connection.close()
                return SharedSession()
            result = SharedSession(self.serializer.loads(row["payload"]), sid, row["version"])
            result.connection = connection
            return result
        except Exception:
            connection.close()
            raise

    def save_session(self, app, session, response):
        response.vary.add("Cookie")
        connection = session.connection
        try:
            if not session.modified:
                return
            if connection is None:
                connection = self.engine(app).connect()
            table = RuntimeSession.__table__
            if not session:
                connection.execute(delete(table).where(table.c.id == session.sid))
                response.delete_cookie(self.get_cookie_name(app), path=self.get_cookie_path(app),
                                       domain=self.get_cookie_domain(app))
            else:
                values = dict(payload=self.serializer.dumps(dict(session)),
                              expires_at=int(time.time()) + app.config["SESSION_TTL_SECONDS"],
                              version=session.version + 1)
                if session.version:
                    result = connection.execute(update(table).where(
                        table.c.id == session.sid, table.c.version == session.version
                    ).values(**values))
                    if result.rowcount != 1:
                        connection.rollback()
                        response.status_code = 409
                        response.set_data('{"error":"Session modifiée, réessayez."}')
                        response.content_type = "application/json"
                        return
                else:
                    connection.execute(insert(table).values(id=session.sid, **values))
                response.set_cookie(self.get_cookie_name(app), self.signer(app).dumps(session.sid),
                                    max_age=app.config["SESSION_TTL_SECONDS"],
                                    httponly=self.get_cookie_httponly(app),
                                    secure=self.get_cookie_secure(app),
                                    samesite=self.get_cookie_samesite(app),
                                    path=self.get_cookie_path(app), domain=self.get_cookie_domain(app))
            connection.commit()
        finally:
            if connection is not None:
                connection.close()
            session.connection = None


def configure_deployment(app):
    app.session_interface = DatabaseSessionInterface()
    with app.app_context():
        if db.engine.dialect.name == "postgresql":
            # Session locks must not consume the route handlers' connection pool.
            app.extensions["session_engine"] = create_engine(
                db.engine.url, pool_pre_ping=True, pool_size=10, max_overflow=10,
                pool_timeout=10)
    from app.storage.storage_import import register_storage_import
    register_storage_import(app)
    from app.storage.sqlite_import import register_sqlite_import
    register_sqlite_import(app)

    @app.teardown_request
    def close_session_connection(error):
        connection = getattr(session, "connection", None)
        if connection is not None:
            connection.close()
            session.connection = None

    @app.get("/health/live")
    def live():
        return jsonify(status="ok")

    @app.get("/health/ready")
    def ready():
        try:
            db.session.execute(select(RuntimeSession.id).limit(1))
        except Exception:
            db.session.rollback()
            app.logger.exception("Database readiness failed")
            return jsonify(status="unavailable"), 503
        return jsonify(status="ok")

    @app.cli.command("sessions-prune")
    def prune():
        """Remove expired sessions; schedule daily outside the web process."""
        result = db.session.execute(delete(RuntimeSession).where(
            RuntimeSession.expires_at <= int(time.time())))
        db.session.commit()
        click.echo(f"{result.rowcount} sessions supprimées")
