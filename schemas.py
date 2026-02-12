from pydantic import BaseModel

# ==========================
# 1. KULLANICI (USER)
# ==========================

# Kayıt olurken ne istiyoruz?
class UserCreate(BaseModel):
    username: str
    email: str | None = None
    password: str  # Şifre burada ZORUNLU

# Kullanıcıya ne gösteriyoruz? (Şifre YOK, ID VAR)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    role: str

    # Pydantic v2: use model_config to allow creating from ORM/attribute objects
    model_config = {"from_attributes": True}


# ==========================
# 2. STADYUM (STADIUM)
# ==========================

# Stadyum eklerken ne istiyoruz?
class StadiumCreate(BaseModel):
    name: str
    city: str
    lat: float
    lon: float

# Kullanıcıya stadyumu gösterirken ne veriyoruz? (+ID ekleniyor)
class StadiumResponse(BaseModel):
    id: int
    name: str
    city: str
    lat: float
    lon: float

    # Pydantic v2: use model_config to allow creating from ORM/attribute objects
    model_config = {"from_attributes": True}


# ==========================
# 3. MEKAN (LOCATION)
# ==========================

# Mekan eklerken ne istiyoruz?
class LocationCreate(BaseModel):
    name: str
    category: str
    description: str | None = None
    stadium_id: int  # Hangi stadyuma ait olduğunu bilmeliyiz
    lat: float
    lon: float

# Kullanıcıya mekanı gösterirken ne veriyoruz? (+ID ekleniyor)
class LocationResponse(BaseModel):
    id: int
    name: str
    category: str
    description: str | None = None
    stadium_id: int
    lat: float
    lon: float

    # Pydantic v2: use model_config to allow creating from ORM/attribute objects
    model_config = {"from_attributes": True}