import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base, sessionmaker

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./lost_phones.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Phone(Base):
    __tablename__ = "phones"
    id = Column(Integer, primary_key=True, index=True)
    imei = Column(String(15), unique=True, index=True, nullable=False)
    serial_number = Column(String(50))
    brand = Column(String(50))
    model = Column(String(100))
    color = Column(String(30))
    storage = Column(String(20))
    purchase_date = Column(String(20))
    store_name = Column(String(100))
    store_location = Column(String(200))
    price = Column(String(30))
    receipt_number = Column(String(50))
    warranty_expiry = Column(String(20))
    owner_name = Column(String(100))
    owner_phone = Column(String(20))
    owner_email = Column(String(100))
    status = Column(String(20), default="registered")  # registered/lost/found/recovered
    notes = Column(Text)
    photo_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    phone_id = Column(Integer, index=True)
    imei = Column(String(15), index=True)
    reporter_name = Column(String(100))
    reporter_phone = Column(String(20))
    reporter_email = Column(String(100))
    report_type = Column(String(20))  # lost/found
    location = Column(String(200))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
