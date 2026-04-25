from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config.settings import settings


class Base(DeclarativeBase):
    pass


engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
}

# Neon/serverless Postgres can drop idle SSL connections in local dev.
# Disable connection reuse there to avoid stale pooled connections.
if "neon.tech" in settings.DATABASE_URL:
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_recycle"] = 300

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
