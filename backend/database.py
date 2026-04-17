import os
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///laundries.db")

# Railway/Heroku use postgres:// but SQLAlchemy requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

_is_sqlite = DATABASE_URL.startswith("sqlite")
_connect_args = {"check_same_thread": False} if _is_sqlite else {}

Base = declarative_base()


class Laundry(Base):
    __tablename__ = "laundries"

    place_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String)
    city = Column(String)
    region = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    rating = Column(Float)
    reviews_count = Column(Integer, default=0)
    google_maps_url = Column(String)
    phone = Column(String)
    website = Column(String)
    search_term = Column(String)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    excluded = Column(Boolean, default=False)
    excluded_reason = Column(String)


engine = create_engine(DATABASE_URL, connect_args=_connect_args)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
