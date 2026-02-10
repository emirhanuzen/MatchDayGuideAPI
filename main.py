from fastapi import FastAPI
from pydantic import BaseModel, Field
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- İZİNLER (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Herkese kapım açık
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- MODELLER (Veri Kalıpları) ---
class Stadium(BaseModel):
    name: str  # Örn: Emirates Stadyumu
    city: str  # Örn: Londra
    lat: float  # Örn: 51.5549
    lon: float  # Örn: -0.1084


class Location(BaseModel):
    stadium_id: int
    name: str
    category: str
    lat: float  # X yerine Enlem
    lon: float  # Y yerine Boylam
    doluluk: int = Field(ge=0, le=100, description="0-100 arası yüzde")
    VIP: bool


# --- VERİTABANI KURULUMU ---
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # 1. Tablo: STADYUMLAR (GPS Destekli)
    c.execute("""
              CREATE TABLE IF NOT EXISTS stadiums
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  name
                  TEXT,
                  city
                  TEXT,
                  lat
                  REAL,
                  lon
                  REAL
              )
              """)

    # 2. Tablo: MEKANLAR (GPS Destekli)
    c.execute("""
              CREATE TABLE IF NOT EXISTS locations
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  stadium_id
                  INTEGER,
                  name
                  TEXT,
                  category
                  TEXT,
                  lat
                  REAL,
                  lon
                  REAL,
                  doluluk
                  INTEGER,
                  is_vip
                  BOOLEAN
              )
              """)
    conn.commit()
    conn.close()


# Uygulama başlarken tabloları kur (Eğer yoksa)
init_db()


@app.get("/")
def read_root():
    return {"Durum": "Global GPS Stadyum API Çalışıyor! 🌍"}


# --- 1. ADIM: Stadyum Ekleme ---
@app.post("/stadiumsCreate")
def create_stadium(stadium: Stadium):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO stadiums (name, city, lat, lon) VALUES (?, ?, ?, ?)",
              (stadium.name, stadium.city, stadium.lat, stadium.lon))
    conn.commit()
    stadium_id = c.lastrowid
    conn.close()
    return {"mesaj": f"{stadium.name} eklendi!", "stadium_id": stadium_id}


# --- 2. ADIM: Mekan Ekleme ---
@app.post("/locations/locationscreate")
def create_location(location: Location):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
              INSERT INTO locations
                  (stadium_id, name, category, lat, lon, doluluk, is_vip)
              VALUES (?, ?, ?, ?, ?, ?, ?)
              """, (location.stadium_id, location.name, location.category, location.lat, location.lon, location.doluluk,
                    location.VIP))
    conn.commit()
    conn.close()
    return {"mesaj": f"{location.name} başarıyla eklendi!"}


# --- 3. ADIM: GPS TABANLI EN YAKIN BULMA ---
@app.get("/locations/locationsFind")
def locationsFind(lat: float, lon: float, category: str, stadium_id: int):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Kategori Filtreleme
    if category == "Hepsi":
        sql = "SELECT * FROM locations WHERE stadium_id = ?"
        params = (stadium_id,)
    else:
        sql = "SELECT * FROM locations WHERE stadium_id = ? AND category = ?"
        params = (stadium_id, category)

    c.execute(sql, params)
    mekanlar = c.fetchall()
    conn.close()

    if not mekanlar:
        return {"error": "Bu kategoride mekan yok!"}

    en_iyi_mekan = None
    en_dusuk_puan = float('inf')

    for mekan in mekanlar:
        # Veri hatası varsa atla
        if mekan["lat"] is None or mekan["lon"] is None:
            continue

        # --- GPS MESAFE HESABI (Metre Cinsinden) ---
        # 1 Derece Enlem ≈ 111,000 metredir.
        lat_fark = (mekan["lat"] - lat) * 111000
        lon_fark = (mekan["lon"] - lon) * 111000

        mesafe = (lat_fark ** 2 + lon_fark ** 2) ** 0.5

        # Doluluk Cezası
        doluluk = mekan["doluluk"] if mekan["doluluk"] is not None else 0

        # Puanlama: Mesafe + (Doluluk * 2)
        puan = mesafe + (doluluk * 2)

        if puan < en_dusuk_puan:
            en_dusuk_puan = puan
            en_iyi_mekan = {
                "ad": mekan["name"],
                "lat": mekan["lat"],
                "lon": mekan["lon"],
                "mesafe": int(mesafe),
                "doluluk": f"%{doluluk}",
                "puan": int(puan)
            }

    return en_iyi_mekan


# --- LISTELEME (Lat/Lon dahil) ---
@app.get("/stadiums/full-map")
def get_full_map():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Stadyum ve Mekanları Birleştir
    c.execute("""
              SELECT s.name     as stadyum_adi,
                     s.city     as sehir,
                     l.name     as mekan_adi,
                     l.category as tur,
                     l.doluluk,
                     l.lat,
                     l.lon,
                     l.is_vip
              FROM stadiums s
                       LEFT JOIN locations l ON s.id = l.stadium_id
              """)

    data = c.fetchall()
    conn.close()

    sonuc_listesi = []
    for satir in data:
        sonuc_listesi.append({
            "stadyum": satir["stadyum_adi"],
            "sehir": satir["sehir"],
            "mekan": satir["mekan_adi"],
            "tur": satir["tur"],
            "lat": satir["lat"],
            "lon": satir["lon"],
            "doluluk_orani": f"%{satir['doluluk']}",
            "ozel_giris": "EVET" if satir["is_vip"] else "HAYIR"
        })

    return {"tum_harita": sonuc_listesi}


# --- SİLME FONKSİYONLARI ---
@app.delete("/locations/{location_id}")
def delete_location(location_id: int):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM locations WHERE id = ?", (location_id,))
    kayit = c.fetchone()
    if kayit is None:
        conn.close()
        return {"hata": "Mekan bulunamadı!"}

    c.execute("DELETE FROM locations WHERE id = ?", (location_id,))
    conn.commit()
    conn.close()
    return {"mesaj": "Mekan silindi! 🗑️"}


@app.delete("/stadiums/{stadium_id}")
def delete_stadium(stadium_id: int):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM stadiums WHERE id = ?", (stadium_id,))
    kayit = c.fetchone()
    if kayit is None:
        conn.close()
        return {"hata": "Stadyum bulunamadı!"}

    # Önce stadyuma bağlı mekanları sil, sonra stadyumu sil
    c.execute("DELETE FROM locations WHERE stadium_id = ?", (stadium_id,))
    c.execute("DELETE FROM stadiums WHERE id = ?", (stadium_id,))
    conn.commit()
    conn.close()
    return {"mesaj": "Stadyum ve içindeki her şey silindi! 🗑️"}


# --- GÜNCELLEME (UPDATE) ---
@app.put("/locations/{location_id}")
def update_location(location_id: int, location: Location):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Lat ve Lon güncelliyoruz
    c.execute("""
              UPDATE locations
              SET name     = ?,
                  category = ?,
                  lat      = ?,
                  lon      = ?,
                  doluluk  = ?,
                  is_vip   = ?
              WHERE id = ?
              """, (location.name, location.category, location.lat, location.lon, location.doluluk, location.VIP,
                    location_id))

    conn.commit()
    conn.close()
    return {"mesaj": f"Mekan (ID: {location_id}) güncellendi! ✨"}


@app.put("/stadiums/{stadium_id}")
def update_stadium(stadium_id: int, stadium: Stadium):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("UPDATE stadiums SET name = ?, city = ?, lat = ?, lon = ? WHERE id = ?",
              (stadium.name, stadium.city, stadium.lat, stadium.lon, stadium_id))
    conn.commit()
    conn.close()
    return {"mesaj": f"Stadyum güncellendi! 🏟️"}