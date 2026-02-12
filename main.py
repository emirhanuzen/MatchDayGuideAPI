# main.py (EN TEPE KISMI - BURAYI GÜNCELLE)
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # <--- BU EKSİKTİ
from sqlalchemy.orm import Session
from datetime import datetime, timedelta # <--- BU EKSİKTİ
from typing import List
from passlib.context import CryptContext
from jose import JWTError, jwt # <--- BU EKSİKTİ

import models, schemas, database
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Tüm adreslere izin ver (Geliştirme aşaması için)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Şifreleme Araçları
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# --- VERİTABANI BAĞLANTISI (Dependency) ---
# Her fonksiyona "Al sana veritabanı anahtarı" diyen kısım.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- YARDIMCI FONKSİYONLAR ---
def get_password_hash(password):
    return pwd_context.hash(password)


# --- AYARLAR (Sabitler) ---
SECRET_KEY = "cok_gizli_bir_anahtar_bunu_degistir"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# --- ŞİFRE DOĞRULAMA (Verify) ---
# Kullanıcının girdiği şifre (plain) ile veritabanındaki (hashed) tutuyor mu?
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# --- FEDAİ (Token Doğrulama) ---
# Bu fonksiyon her korumalı sayfada çalışacak.
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Hata mesajını baştan hazırlayalım (Standart prosedür)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Giriş yapılamadı (Token geçersiz veya süresi dolmuş)",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Token şifresini çöz (Decode)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 2. İçindeki kullanıcı adını (sub) al
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception  # Token sahteyse veya süresi dolmuşsa hata ver

    # 3. Veritabanında bu kullanıcıyı bul
    user = db.query(models.User).filter(models.User.username == username).first()

    if user is None:
        raise credentials_exception

    return user  # Kimliğini tespit ettik, içeri alıyoruz!

# --- TOKEN OLUŞTURMA (Create Token) ---
# Giriş yapan kullanıcıya verilecek "Giriş Kartı"nı basar.
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    # Süre belirle (Yoksa 15 dk ver)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    # Bitiş süresini veriye ekle
    to_encode.update({"exp": expire})

    # JWT kütüphanesi ile şifrele ve paketle
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ==============================
# BURASI SENİN "BİLMİYORUM" DEDİĞİN YER
# ==============================

@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Önce veritabanına sor: Bu kullanıcı adı var mı?
    # SQL Karşılığı: SELECT * FROM users WHERE username = '...'
    db_user = db.query(models.User).filter(models.User.username == user.username).first()

    if db_user:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten alınmış!")

    # 2. Şifreyi şifrele (Hashle)
    hashed_pw = get_password_hash(user.password)

    # 3. Yeni Kullanıcıyı Hazırla (Python Nesnesi olarak)
    # SQL Karşılığı: INSERT INTO users (...) VALUES (...) için hazırlık
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        role="user"
    )

    # 4. Veritabanına Ekle
    db.add(new_user)  # Listeye ekle
    db.commit()  # Kaydet (Enter tuşuna basmak gibi)
    db.refresh(new_user)  # ID'si oluştu, veriyi geri çekip new_user'ı güncelle

    return new_user


# --- GİRİŞ YAP (LOGIN) ---
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. ADIM: Kullanıcıyı veritabanında ara
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    # 2. ADIM: Kullanıcı yoksa veya şifre yanlışsa HATA ver
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre yanlış",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. ADIM: Token (Giriş Kartı) oluştur
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # 4. ADIM: Kartı teslim et
    return {"access_token": access_token, "token_type": "bearer"}
@app.post("/stadium/create", response_model=schemas.StadiumResponse)
def create_stadium(stadium: schemas.StadiumCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)):
    new_stadium = models.Stadium(
        name=stadium.name,
        city=stadium.city,
        lat=stadium.lat,
        lon=stadium.lon,
    )
    db.add(new_stadium)
    db.commit()
    db.refresh(new_stadium)
    return new_stadium

@app.post("/location/create", response_model=schemas.LocationResponse)
def create_location(location: schemas.LocationCreate,db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    stadium = db.query(models.Stadium).filter(models.Stadium.id == location.stadium_id).first()
    if not stadium:
        raise HTTPException(status_code=400, detail="Eşleşen Stadyum bulunmadı!")

    new_location = models.Location(
    name=location.name,
    category=location.category,
    description=location.description,
     stadium_id=location.stadium_id,
     lat=location.lat,
        lon=location.lon,
    )
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location
@app.get("/stadiums/{stadium_id}/locations", response_model=List[schemas.LocationResponse])
def get_locations(stadium_id: int, db: Session = Depends(get_db)):
    locations = db.query(models.Location).filter(models.Location.id == stadium_id).all()
    return locations
@app.get("/stadiums/List", response_model=List[schemas.StadiumResponse])
def get_locations( db: Session = Depends(get_db)):
    stadiums = db.query(models.Stadium).all()
    return stadiums
@app.put("/stadiums/{stadium_id}",response_model=schemas.StadiumResponse)
def update_stadium(stadium_id: int,stadium_data=schemas.StadiumCreate,db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    db_stadium=db.query(models.Stadium).filter(models.Stadium.id == stadium_id).first()
    if not db_stadium:
        raise HTTPException(status_code=404, detail="Böyle bir stadyum yok!")
    db_stadium.name = stadium_data.name
    db_stadium.city = stadium_data.city
    db_stadium.lat = stadium_data.lat
    db_stadium.lon = stadium_data.lon
    db.commit()
    db.refresh(db_stadium)
    return db_stadium


@app.delete("/stadiums/{stadium_id}")
def delete_stadium(
        stadium_id: int,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    db_stadium = db.query(models.Stadium).filter(models.Stadium.id == stadium_id).first()

    if not db_stadium:
        raise HTTPException(status_code=404, detail="Silinecek stadyum bulunamadı")

    db.delete(db_stadium)
    db.commit()
    return {"mesaj": f"{stadium_id} ID'li stadyum başarıyla silindi."}

@app.put("/location/{location_id}",response_model=schemas.LocationResponse)
def uptade_location(location_id: int,location_data: schemas.LocationCreate,db: Session = Depends(get_db),get_current_user: models.User = Depends(get_current_user)):
    location = db.query(models.Location).filter(models.Location.id == location_id).first()
    if not location:
        if not location:
            raise HTTPException(status_code=404, detail="Böyle bir lokayon yok!")
        location.name = location_data.name
        location.description = location_data.description
        location.stadium_id = location_data.stadium_id
        location.category = location_data.category
        location.lat = location_data.lat,
        location.lon= location_data.lon,

        db.commit()
        db.refresh(location)
        return location
@app.delete("/location/{location_id}",response_model=schemas.LocationResponse)
def delete_location(
        location_id: int,db:Session=Depends(get_db),current_user: models.User = Depends(get_current_user)):
    location_db = db.query(models.Location).filter(models.Location.id == location_id).first()
    if not location_db:
        if not location_db:
            raise HTTPException(status_code=404, detail="Böyle bir lokasyon yok!")
    db.delete(location_db)
    db.commit()
    db.refresh(location_db)
    return location_db

import math

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000 # Dünya yarıçapı (metre)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lon2 - lon1)
    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


@app.get("/stadiums/{stadium_id}/guide")
def stadium_guide(
        stadium_id: int,
        user_lat: float,
        user_lon: float,
        category: str = None,  # WC, Yemek vb.
        db: Session = Depends(get_db)
):
    # 1. Seçilen stadyumdaki mekanları getir
    query = db.query(models.Location).filter(models.Location.stadium_id == stadium_id)

    # 2. Eğer kategori seçildiyse (Yemek, WC vs.) sadece onları getir
    if category:
        query = query.filter(models.Location.category == category)

    locations = query.all()

    # 3. Mesafe hesapla ve listeye ekle
    guide_results = []
    for loc in locations:
        distance = calculate_distance(user_lat, user_lon, loc.lat, loc.lon)
        guide_results.append({
            "id": loc.id,
            "name": loc.name,
            "category": loc.category,
            "description": loc.description,
            "distance_meters": round(distance, 1),  # Örn: 45.2 metre
            "lat": loc.lat,
            "lon": loc.lon
        })

    # 4. En yakından en uzağa sırala (Müşteri önce en yakındaki WC'yi görsün)
    return sorted(guide_results, key=lambda x: x["distance_meters"])