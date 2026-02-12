# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Veritabanı dosyamızın adı (sqlite:/// zorunlu ön ektir)
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

# 1. MOTOR (Engine): Veritabanını çalıştıran güç
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 2. OTURUM FABRİKASI (SessionLocal): Her istekte yeni bir bağlantı açar
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. TEMEL SINIF (Base): Modellerimizin (Tabloların) atası
Base = declarative_base()

# --- Dependency (Bağımlılık) ---
# Bunu main.py'de kullanacağız. "İşin bitince veritabanını kapat" demektir.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()