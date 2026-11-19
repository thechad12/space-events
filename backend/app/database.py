from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings


def _normalize_db_url(url: str) -> str:
    # Hosted Postgres providers (Prisma Postgres, Heroku, Neon...) often hand out
    # "postgres://" URLs, which SQLAlchemy 2.x no longer accepts.
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://"):]
    return url


engine = create_engine(_normalize_db_url(settings.DATABASE_URL), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
