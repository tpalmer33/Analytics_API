import sqlmodel
from sqlmodel import SQLModel, Session
import timescaledb

from .config import DATABASE_URL, DB_TIMEZONE

if DATABASE_URL == "":
    # Fail during import so missing configuration is caught before serving requests.
    raise NotImplementedError("DATABASE URL needs to be set")

engine = timescaledb.create_engine(DATABASE_URL, timezone=DB_TIMEZONE)

def init_db():
    """Create tables for registered models, then initialize TimescaleDB hypertables."""
    print("creating database")
    # Model modules must be imported first to register their tables in the metadata.
    SQLModel.metadata.create_all(engine)
    print("creating hypertables")
    # Hypertable setup depends on the underlying SQL tables already existing.
    timescaledb.metadata.create_all(engine)

def get_session():
    """Yield a request-scoped session and close it when dependency cleanup runs."""
    with Session(engine) as session:
        yield session
