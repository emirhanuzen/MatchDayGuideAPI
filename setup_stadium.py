import sqlite3
import random


def setup_simulation():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    print("🧹 Eski veriler temizleniyor...")
    c.execute("DROP TABLE IF EXISTS locations")
    c.execute("DROP TABLE IF EXISTS stadiums")

    # Tabloları Kur
    c.execute("""
              CREATE TABLE stadiums
              (
                  id   INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  city TEXT,
                  lat  REAL,
                  lon  REAL
              )
              """)

    c.execute("""
              CREATE TABLE locations
              (
                  id         INTEGER PRIMARY KEY AUTOINCREMENT,
                  stadium_id INTEGER,
                  name       TEXT,
                  category   TEXT,
                  lat        REAL,
                  lon        REAL,
                  doluluk    INTEGER,
                  is_vip     BOOLEAN
              )
              """)

    print("🏟️ Stadyum Kuruluyor...")
    # Merkez: Emirates Stadyumu
    merkez_lat = 51.5549
    merkez_lon = -0.1084

    c.execute("INSERT INTO stadiums (name, city, lat, lon) VALUES (?, ?, ?, ?)",
              ("Emirates Stadyumu", "Londra", merkez_lat, merkez_lon))
    stadium_id = c.lastrowid

    print("🤖 Yapay Zeka Mekanları Üretiyor...")

    # --- RASTGELE VERİ ÜRETİCİSİ ---
    locations_data = []

    # 1. TUVALETLER (20 Adet Dağıtalım)
    for i in range(1, 21):
        # Merkezin etrafında +/- 0.0015 derece (yaklaşık 150m) sapma yap
        lat = merkez_lat + random.uniform(-0.0015, 0.0015)
        lon = merkez_lon + random.uniform(-0.0020, 0.0020)
        doluluk = random.randint(0, 100)  # Rastgele doluluk
        locations_data.append((stadium_id, f"WC Blok {i}", "Tuvalet", lat, lon, doluluk, False))

    # 2. YEMEK BÜFELERİ (15 Adet)
    bufeler = ["Burger King", "Sosisli", "Fish & Chips", "Vegan Büfe", "Pizza Hut"]
    for i in range(1, 16):
        lat = merkez_lat + random.uniform(-0.0015, 0.0015)
        lon = merkez_lon + random.uniform(-0.0020, 0.0020)
        ad = f"{random.choice(bufeler)} - No:{i}"
        doluluk = random.randint(20, 95)
        locations_data.append((stadium_id, ad, "Yemek", lat, lon, doluluk, False))

    # 3. KAPILAR (8 Ana Kapı)
    kapilar = ["Kuzey", "Güney", "Doğu", "Batı", "Kuzey-Doğu", "Kuzey-Batı", "Güney-Doğu", "Güney-Batı"]
    for kapi in kapilar:
        # Kapıları biraz daha dışarıya atalım (0.0020 sapma)
        lat = merkez_lat + random.uniform(-0.0020, 0.0020)
        lon = merkez_lon + random.uniform(-0.0025, 0.0025)
        locations_data.append((stadium_id, f"{kapi} Kapısı", "Kapı", lat, lon, 10, False))

    # 4. VIP LOUNGE (5 Adet)
    for i in range(1, 6):
        lat = merkez_lat + random.uniform(-0.0010, 0.0010)  # Merkeze yakın
        lon = merkez_lon + random.uniform(-0.0010, 0.0010)
        locations_data.append((stadium_id, f"VIP Lounge {i}", "Bar", lat, lon, 50, True))

    # Hepsini Veritabanına Bas
    c.executemany("""
                  INSERT INTO locations
                      (stadium_id, name, category, lat, lon, doluluk, is_vip)
                  VALUES (?, ?, ?, ?, ?, ?, ?)
                  """, locations_data)

    conn.commit()
    conn.close()
    print(f"✅ İŞLEM TAMAM! Toplam {len(locations_data)} adet mekan haritaya serpildi. 🌍")


if __name__ == "__main__":
    setup_simulation()