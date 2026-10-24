from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models import Base

engine = create_engine(settings.database_url)
session_factory = sessionmaker(bind=engine, class_=Session)


def create_all_tables(database_engine: Engine) -> None:
    Base.metadata.create_all(bind=database_engine)


def get_session() -> Generator[Session, None, None]:
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
