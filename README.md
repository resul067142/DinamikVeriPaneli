# 📊 Dinamik Veri Yönetim Paneli

Türkiye'nin 81 ilinin verilerini yönetebileceğiniz, dinamik sütun başlıklarına sahip modern bir Django web uygulaması.

## 🚀 Özellikler

- **Kullanıcı Yönetimi**: Kayıt ol, giriş yap, çıkış yap
- **CRUD İşlemleri**: Veri ekleme, silme, güncelleme, listeleme
- **Dinamik Sütun Başlıkları**: Sütun isimleri admin panelinden değiştirilebilir
- **Modern UI**: Tailwind CSS ile responsive tasarım
- **Başlangıç Verisi**: 81 il otomatik olarak yüklenir
- **Güvenlik**: Login required koruması
- **Mesaj Sistemi**: Başarılı/hatalı işlem bildirimleri
- **REST API**: Tam kapsamlı API desteği
- **Celery Tasks**: Arka plan görevleri ve otomatik yedekleme
- **Cache Sistemi**: Redis ile performans optimizasyonu
- **Export Özellikleri**: CSV, Excel, PDF export
- **İstatistikler**: Detaylı raporlama ve analiz
- **Error Handling**: 404, 500 hata sayfaları
- **Logging**: Kapsamlı log sistemi
- **Testing**: Unit ve integration testler

## 🛠️ Teknolojiler

- **Backend**: Python 3.8+, Django 4.2 LTS
- **Veritabanı**: SQLite (varsayılan), PostgreSQL 12+ (opsiyonel)
- **Frontend**: HTML + Tailwind CSS
- **API**: Django REST Framework
- **Cache**: Redis
- **Task Queue**: Celery
- **Paket Yöneticisi**: pip
- **Testing**: pytest, coverage
- **Code Quality**: black, flake8, isort

## 📋 Gereksinimler

- Python 3.8+
- pip
- Redis (Celery ve cache için)
- PostgreSQL 12+ (opsiyonel)

## 🚀 Kurulum

### 1. Projeyi klonlayın
```bash
git clone <repository-url>
cd 81tablo4
```

### 2. Sanal ortam oluşturun (önerilen)
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows
```

### 3. Environment variables ayarlayın
```bash
cp env_example.txt .env
# .env dosyasını düzenleyin
```

### 4. Gerekli paketleri yükleyin
```bash
pip install -r requirements.txt
```

### 5. Redis'i başlatın
```bash
# Linux/Mac
redis-server

# Windows
# Redis Windows versiyonunu indirin ve başlatın
```

### 6. Veritabanını oluşturun
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 7. Süper kullanıcı oluşturun
```bash
python3 manage.py createsuperuser
```

### 8. 81 ilin verilerini yükleyin
```bash
python3 manage.py load_iller
```

### 9. İl sorumlusu kullanıcıları oluşturun
```bash
python3 manage.py create_il_users
```

### 10. Celery worker'ı başlatın
```bash
# Terminal 1: Celery worker
celery -A veri_yonetimi worker --loglevel=info

# Terminal 2: Celery beat (periyodik görevler)
celery -A veri_yonetimi beat --loglevel=info
```

### 11. Sunucuyu başlatın
```bash
python3 manage.py runserver
```

## 🌐 Kullanım

### URL Yapısı
- `/` - Ana sayfa (veri listesi)
- `/login/` - Giriş sayfası
- `/register/` - Kayıt sayfası
- `/veri/ekle/` - Yeni veri ekleme
- `/veri/guncelle/<id>/` - Veri güncelleme
- `/veri/sil/<id>/` - Veri silme
- `/admin/` - Admin paneli
- `/api/` - REST API endpoints

### API Endpoints
- `GET /api/veriler/` - Veri listesi
- `POST /api/veriler/` - Yeni veri oluştur
- `GET /api/veriler/<id>/` - Veri detayı
- `PUT /api/veriler/<id>/` - Veri güncelle
- `DELETE /api/veriler/<id>/` - Veri sil
- `GET /api/istatistikler/` - Sistem istatistikleri
- `GET /api/export/csv/` - CSV export

### Veri Yapısı
- **alan_1**: İl adı
- **alan_2**: Bölge
- **alan_3**: Plaka kodu
- **alan_4**: Nüfus

## 🔧 PostgreSQL Kurulumu (Opsiyonel)

1. `settings.py` dosyasında PostgreSQL ayarlarını aktif edin:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dinamik_veri_paneli',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

2. SQLite ayarlarını yorum satırı yapın.

## 📁 Proje Yapısı

```
81tablo4/
├── dinamik_veri_paneli/     # Ana proje ayarları
├── veri_yonetimi/           # Ana uygulama
│   ├── models.py            # Veri modelleri
│   ├── views.py             # CRUD view'ları
│   ├── api_views.py         # API view'ları
│   ├── serializers.py       # API serializers
│   ├── forms.py             # Form sınıfları
│   ├── admin.py             # Admin panel ayarları
│   ├── celery.py            # Celery konfigürasyonu
│   ├── tasks.py             # Celery tasks
│   └── management/          # Management commands
│       └── commands/
│           ├── load_iller.py # 81 il veri yükleme
│           └── create_il_users.py # İl sorumlusu kullanıcıları
├── templates/               # HTML template'leri
│   ├── base.html           # Ana template
│   ├── 404.html            # 404 hata sayfası
│   ├── 500.html            # 500 hata sayfası
│   └── veri_yonetimi/      # Uygulama template'leri
├── static/                  # Statik dosyalar
├── logs/                    # Log dosyaları
├── backups/                 # Yedek dosyaları
├── exports/                 # Export dosyaları
├── iller.json              # 81 il verisi
├── requirements.txt         # Python paketleri
├── env_example.txt         # Environment variables örneği
└── manage.py               # Django yönetim
```

## 🎨 Özelleştirme

### Sütun Başlıklarını Değiştirme
1. Admin paneline giriş yapın (`/admin/`)
2. "Sütun Ayarları" bölümüne gidin
3. Başlıkları istediğiniz gibi değiştirin
4. Kaydedin

### Yeni Veri Ekleme
1. Giriş yapın
2. "Veri Ekle" butonuna tıklayın
3. Formu doldurun
4. Kaydedin

### API Kullanımı
```bash
# Veri listesi
curl -H "Authorization: Token your-token" http://localhost:8000/api/veriler/

# Yeni veri ekleme
curl -X POST -H "Content-Type: application/json" \
     -d '{"sutun_degerleri": {"1": "34", "2": "İstanbul"}}' \
     http://localhost:8000/api/veriler/
```

## 🧪 Testing

### Testleri çalıştırın
```bash
# Tüm testler
python3 manage.py test

# Belirli test sınıfı
python3 manage.py test veri_yonetimi.tests.ModelTestCase

# Coverage ile test
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Code Quality
```bash
# Code formatting
black .

# Linting
flake8 .

# Import sorting
isort .
```

## 🔒 Güvenlik

- **SECRET_KEY**: Environment variable olarak saklanır
- **DEBUG**: Production'da False olmalı
- **ALLOWED_HOSTS**: Sadece güvenli host'lar
- **CSRF Protection**: Aktif
- **XSS Protection**: Aktif
- **Content Type Sniffing**: Devre dışı
- **Frame Options**: DENY

## 📊 Monitoring ve Logging

### Logging
- Log dosyaları `logs/` dizininde saklanır
- Rotasyon: 30 gün sonra otomatik temizleme
- Log seviyeleri: DEBUG, INFO, WARNING, ERROR

### Celery Tasks
- Otomatik veri yedekleme (her saat)
- İstatistik güncelleme (her 30 dakika)
- Log temizleme (her gün)
- CSV export

### Cache
- Redis cache backend
- İstatistikler 1 saat cache'lenir
- API response'ları cache'lenir

## 🚀 Production Deployment

### Gunicorn ile
```bash
gunicorn dinamik_veri_paneli.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables
```bash
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379/0
```

### SSL/HTTPS
```bash
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## 🐛 Sorun Giderme

### Yaygın Hatalar

1. **ModuleNotFoundError: No module named 'theme'**
   - Tailwind CSS kurulumu tamamlanmamış
   - `python3 manage.py tailwind init` komutunu çalıştırın

2. **Database connection error**
   - PostgreSQL ayarlarını kontrol edin
   - Veritabanının çalıştığından emin olun

3. **Redis connection error**
   - Redis servisinin çalıştığından emin olun
   - `redis-cli ping` ile test edin

4. **Celery worker error**
   - Redis bağlantısını kontrol edin
   - Worker'ı yeniden başlatın

5. **Template not found**
   - `templates/` dizininin doğru konumda olduğunu kontrol edin
   - `settings.py`'de `TEMPLATES` ayarlarını kontrol edin

### Debug Toolbar
Development modunda `/__debug__/` URL'i ile debug toolbar'a erişebilirsiniz.

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit yapın (`git commit -m 'Add some AmazingFeature'`)
4. Push yapın (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## 📞 İletişim

Proje ile ilgili sorularınız için issue açabilirsiniz.

---

**Not**: Bu proje Django 4.2 LTS ile geliştirilmiştir ve Python 3.8+ gerektirir.
