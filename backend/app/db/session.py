from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()
engine: Engine = create_engine(
    settings.resolved_database_url,
    pool_pre_ping=True,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
