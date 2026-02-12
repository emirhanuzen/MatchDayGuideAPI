# models.py (GÜNCEL HALİ)
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship  # <--- YENİ GÜÇ!

import schemas
from database import Base


# --- KULLANICI TABLOSU ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="user")


# --- STADYUM TABLOSU ---
class Stadium(Base):
    __tablename__ = "stadiums"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    city = Column(String)
    lat = Column(Float)
    lon = Column(Float)

    # İLİŞKİ: Bir stadyumun ÇOK mekanı olabilir.
    # Bu satır veritabanında sütun açmaz, Python tarafında kolaylık sağlar.
    locations = relationship("Location", back_populates="stadium")


# --- MEKAN (LOCATION) TABLOSU --- (Bunu unutmuştuk!)
class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)  # Cafe, WC, Giriş Kapısı...
    description = Column(String, nullable=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)

    # EN ÖNEMLİ KISIM: Yabancı Anahtar (Hangi stadyuma ait?)
    stadium_id = Column(Integer, ForeignKey("stadiums.id"))

    # İLİŞKİ: Bu mekan TEK bir stadyuma aittir.
    stadium = relationship("Stadium", back_populates="locations")

