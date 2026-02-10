# Arsenal Smart Match Day Guide 🏟️

Bu dokümantasyon **Türkçe** olarak hazırlanmıştır.  
Proje, Emirates Stadyumu özelinde tasarlanmış olsa da, farklı stadyumlara uyarlanabilir bir akıllı maç günü rehberi mimarisi sunar.

---

## Proje Özeti

**Arsenal Smart Match Day Guide**, stadyum içindeki taraftarları **GPS konumlarına göre** en yakın ve en uygun hizmet noktasına yönlendiren akıllı bir navigasyon sistemidir.  

Seyircinin harita üzerinde tıkladığı **konuma göre**, sistem:

- Bulunduğu stadyumdaki **tuvalet, yemek büfesi, kapı, bar vb.** tüm noktaları veritabanından çeker,
- Her bir nokta için:
  - **Öklid (Euclidean) mesafe** hesaplar,
  - **Doluluk oranını** (yoğunluğu) hesaba katar,
- Ve taraftara **en uygun hedef noktayı** (en kısa + en az yoğun) önerir.

Ön yüz (frontend), **Leaflet.js** tabanlı interaktif bir harita ile bu hedefi görsel olarak gösterir ve kullanıcının tıkladığı nokta ile en uygun hizmet noktası arasına bir **rota çizgisi** çeker.

---

## Özellikler

- **FastAPI ile geliştirilmiş RESTful API**
  - `main.py` içerisinde tanımlanan endpoint'ler ile stadyum ve mekan yönetimi,
  - GPS tabanlı en uygun mekan bulma servisi,
  - JSON tabanlı, hızlı ve modern API yapısı.

- **SQLite veritabanı ile konum ve doluluk yönetimi**
  - `database.db` dosyası üzerinden hafif ve gömülü veritabanı,
  - `stadiums` ve `locations` tabloları ile stadyum ve tüm mekanların yönetimi,
  - `setup_stadium.py` ile otomatik veri üretimi ve sahte (simüle) kayıtlar.

- **Öklid (Euclidean) algoritması ile en yakın mesafe hesaplama**
  - Kullanıcının tıkladığı koordinat (`lat`, `lon`) ile veritabanındaki her mekan arasındaki uzaklık,
  - Basitleştirilmiş, metre cinsinden **Öklid mesafesi** yaklaşımı:
    - \(\Delta lat \approx 111000 \, m\)
    - \(\Delta lon \approx 111000 \, m\)
  - Mesafe + doluluk puanı ile **skor bazlı seçim**:
    - \(\text{puan} = \text{mesafe} + (\text{doluluk} \times 2)\)

- **Leaflet.js ile interaktif harita ve rota çizimi**
  - `index.html` üzerinde:
    - Emirates Stadium merkezli interaktif harita,
    - Mekanların kategoriye göre özel ikonlarla işaretlenmesi (🚻, 🍔, 🚪, 🍺, 👕),
    - Kullanıcı konum tıklaması ile:
      - "Sen Buradasın" işaretçisi,
      - Hedef mekan için yıldızlı işaretçi,
      - İki nokta arasında kırmızı, kesik çizgili rota.

- **Dinamik doluluk oranı simülasyonu**
  - `setup_stadium.py` dosyası ile:
    - Tuvaletler, yemek büfeleri, kapılar ve VIP alanlar için **rastgele fakat mantıklı** koordinatlar,
    - Her mekan için **rastgele doluluk oranı** üretimi (0–100),
    - Farklı kategorilerde onlarca test verisiyle gerçekçi bir maç günü senaryosu.

---

## Kurulum (Installation)

Aşağıdaki adımlar, projeyi yerel ortamınızda çalıştırmanız için yeterlidir.

1. **Repo'yu klonlayın**

   ```bash
   git clone https://github.com/<kullanici-adi>/arsenal-smart-match-day-guide.git
   cd arsenal-smart-match-day-guide
   ```

2. **Sanal ortam (virtualenv / venv) oluşturun**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # (İsteğe bağlı) macOS / Linux
   # source venv/bin/activate
   ```

3. **Gereksinimleri yükleyin**

   ```bash
   pip install -r requirements.txt
   ```

4. **Veritabanını ve simülasyon verilerini kurun**

   Bu adım, `database.db` dosyasını oluşturarak Emirates Stadyumu ve etrafındaki tuvalet, yemek, kapı ve VIP noktalarını hazırlar.

   ```bash
   python setup_stadium.py
   ```

5. **FastAPI sunucusunu başlatın**

   ```bash
   uvicorn main:app --reload
   ```

   - Sunucu varsayılan olarak `http://127.0.0.1:8000` adresinde çalışır.
   - API dokümantasyonlarına şu adreslerden ulaşabilirsiniz:
     - Swagger UI: `http://127.0.0.1:8000/docs`
     - ReDoc: `http://127.0.0.1:8000/redoc`

6. **Ön yüzü (index.html) açın**

   - Proje klasöründeki `index.html` dosyasını bir tarayıcıda açın:
     - Çift tıklayarak veya
     - Tarayıcı adres çubuğuna dosya yolunu vererek (`file:///.../index.html`).
   - Harita yüklendikten sonra:
     - Harita üzerinde **bulunduğunuz konumu temsil eden noktaya tıklayın**,
     - Üstteki açılır menüden (Tuvalet / Yemek / Kapı / Bar / Mağaza) aramak istediğiniz kategoriyi seçin,
     - Sistem backend'e istek atacak ve **en uygun mekanı** bulup:
       - Haritada işaretleyecek,
       - Aranızdaki rotayı çizecek,
       - Ekranın alt kısmındaki bilgi çubuğunda detayları gösterecektir.

---

## Kullanılan Teknolojiler

**Backend**
- **Python**
- **FastAPI**
- **SQLite**

**Frontend**
- **HTML5 / CSS3**
- **JavaScript**
- **Leaflet.js**

**Önerilen Rozetler (Badges)**  
Bu rozetleri isterseniz GitHub üzerinde README başlığı altına ekleyebilirsiniz:

```markdown
![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green?logo=fastapi)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue?logo=sqlite)
![JavaScript](https://img.shields.io/badge/Frontend-JavaScript-yellow?logo=javascript)
![Leaflet](https://img.shields.io/badge/Map-Leaflet-brightgreen)
```

---

## Mimari Genel Bakış

- **`main.py`**
  - FastAPI uygulamasını başlatır.
  - CORS ayarlarını yapılandırır (her origin'e açık).
  - `Stadium` ve `Location` Pydantic modellerini tanımlar.
  - Veritabanı tablolarını (yoksa) oluşturur.
  - Aşağıdaki temel endpoint'leri sağlar:
    - `POST /stadiumsCreate` – Yeni stadyum ekler.
    - `POST /locations/locationscreate` – Yeni mekan ekler.
    - `GET /locations/locationsFind` – Verilen GPS konumuna ve kategoriye göre **en uygun mekanı** bulur.
    - `GET /stadiums/full-map` – Tüm stadyum ve mekanları, haritada çizim için döner.
    - `DELETE /locations/{location_id}` – Belirli bir mekanı siler.
    - `DELETE /stadiums/{stadium_id}` – Stadyumu ve ona bağlı tüm mekanları siler.
    - `PUT /locations/{location_id}` – Mekan bilgisini günceller.
    - `PUT /stadiums/{stadium_id}` – Stadyum bilgisini günceller.

- **`setup_stadium.py`**
  - Var olan `stadiums` ve `locations` tablolarını siler ve yeniden oluşturur.
  - Emirates Stadyumu merkezli bir koordinat sistemi içinde:
    - 20 adet **tuvalet**,
    - 15 adet **yemek / büfe**,
    - 8 adet **giriş kapısı**,
    - 5 adet **VIP lounge / bar**
    için rastgele ama gerçekçi koordinatlar ve doluluk değerleri üretir.
  - Çalıştırıldığında toplam mekan sayısını konsola yazar.

- **`index.html`**
  - Arsenal temalı, modern bir üst bar (header) içerir.
  - Kategori seçimi için bir kontrol paneli (`select`) ve alt bilgi çubuğu barındırır.
  - Leaflet.js ile:
    - Tüm mekanları haritada ikonlarla gösterir (`/stadiums/full-map` endpoint'ini kullanarak),
    - Kullanıcının tıkladığı konumu işaretler,
    - Backend'den alınan en uygun mekan için hedef işaretçisi ve rota çizer.

---

## Ekran Görüntüleri

Bu bölümde proje arayüzünden aldığınız ekran görüntülerini paylaşabilirsiniz.

```markdown
![Ekran Görüntüsü 1](image_path_1.png)
![Ekran Görüntüsü 2](image_path_2.png)
```

> Öneri: `screenshot.png.png` dosyasını veya yeni alacağınız görselleri `screenshots/` klasörüne koyup buradan referans verebilirsiniz.

---

## Geliştirme Fikirleri

- Birden fazla stadyum desteği ve stadyum seçme arayüzü,
+- Gerçek zamanlı doluluk güncellemesi (ör. WebSocket veya periyodik API çağrıları),
 - Kullanıcı konumunu tarayıcı üzerinden otomatik alma (Geolocation API),
 - VIP kullanıcılar için farklı rota / önceliklendirme algoritması,
 - Farklı lig ve takımlar için tema desteği (renk, logo, harita katmanları).

