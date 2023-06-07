from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from process_fire.config import db_url

engine = create_engine(
    db_url
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()