"""SQLAlchemy database setup with SQLite foreign-key enforcement."""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings

IS_SQLITE = settings.DATABASE_URL.startswith("sqlite")
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if IS_SQLITE else {})

if IS_SQLITE:
    @event.listens_for(engine, "connect")
    def sqlite_pragmas(connection, _record):
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=WAL")

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
