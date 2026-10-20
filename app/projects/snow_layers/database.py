"""Sessions for administrative imports into the shared migrated database."""
from sqlalchemy.orm import sessionmaker
from app.extensions import db


def create_session_factory():
    """Requires an application context; uses DATABASE_URL like the portfolio."""
    return sessionmaker(bind=db.engine, expire_on_commit=False)
