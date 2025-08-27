# 🚀 Dinamik Veri Paneli (Dynamic Data Panel)

**Modern, esnek ve kullanıcı dostu veri yönetim sistemi**

[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0+-38B2AC.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 İçindekiler

- [🎯 Proje Hakkında](#-proje-hakkında)
- [✨ Özellikler](#-özellikler)
- [🛠️ Teknolojiler](#️-teknolojiler)
- [🚀 Kurulum](#-kurulum)
- [📱 Kullanım](#-kullanım)
- [🔧 Yapılandırma](#-yapılandırma)
- [📊 Veri Yapısı](#-veri-yapısı)
- [👥 Kullanıcı Yönetimi](#-kullanıcı-yönetimi)
- [🎨 UI/UX Özellikleri](#-uiux-özellikleri)
- [📈 API ve Entegrasyon](#-api-ve-entegrasyon)
- [🔒 Güvenlik](#-güvenlik)
- [📝 Katkıda Bulunma](#-katkıda-bulunma)
- [📄 Lisans](#-lisans)

## 🎯 Proje Hakkında

**Dinamik Veri Paneli**, kurumların ve organizasyonların veri yönetimi ihtiyaçlarını karşılamak üzere tasarlanmış modern bir web uygulamasıdır. Sistem, dinamik sütun yapısı sayesinde farklı veri türlerini esnek bir şekilde yönetebilir ve görselleştirebilir.

### 🎯 Ana Amaçlar

- **Esnek Veri Yönetimi**: Dinamik sütun yapısı ile her türlü veri formatını destekler
- **Görsel Veri Analizi**: İnteraktif grafikler ve istatistikler ile veri görselleştirme
- **Kullanıcı Dostu Arayüz**: Modern ve responsive tasarım
- **Güvenli Erişim**: Rol tabanlı kullanıcı yönetimi
- **Özelleştirilebilir**: Logo, başlık ve tema özelleştirme

## ✨ Özellikler

### 🔧 Temel Özellikler
- ✅ **Dinamik Sütun Sistemi**: Sütunları ekleme, düzenleme, silme
- ✅ **Veri Girişi ve Düzenleme**: Kolay veri yönetimi
- ✅ **Kullanıcı Yönetimi**: Rol tabanlı yetkilendirme
- ✅ **Responsive Tasarım**: Mobil ve masaüstü uyumlu
- ✅ **Gerçek Zamanlı Güncelleme**: Anlık veri değişiklikleri

### 🎨 Görsel Özellikler
- 🎨 **Modern UI/UX**: Tailwind CSS ile şık tasarım
- 📊 **İnteraktif Grafikler**: Veri görselleştirme
- 🎯 **Progress Bar'lar**: İlerleme durumu gösterimi
- 🌈 **Renkli Tema**: Gradient ve modern renk paleti
- 📱 **Mobil Uyumlu**: Tüm cihazlarda mükemmel görünüm

### 🔐 Güvenlik Özellikleri
- 🔒 **Kullanıcı Kimlik Doğrulama**: Güvenli giriş sistemi
- 👥 **Rol Tabanlı Yetkilendirme**: Admin ve kullanıcı rolleri
- 🛡️ **CSRF Koruması**: Güvenli form işleme
- 🔐 **Şifre Güvenliği**: Güçlü şifre politikaları

## 🛠️ Teknolojiler

### Backend
- **Django 4.2+**: Güçlü Python web framework
- **Python 3.8+**: Modern Python programlama dili
- **SQLite**: Hafif veritabanı (production'da PostgreSQL önerilir)
- **Django ORM**: Veritabanı işlemleri

### Frontend
- **Tailwind CSS**: Utility-first CSS framework
- **JavaScript (ES6+)**: Modern JavaScript
- **HTML5**: Semantic HTML
- **Responsive Design**: Mobil-first yaklaşım

### Veritabanı
- **SQLite**: Geliştirme ortamı
- **PostgreSQL**: Production ortamı (önerilen)
- **Django Migrations**: Veritabanı şema yönetimi

### Geliştirme Araçları
- **Git**: Versiyon kontrolü
- **Django Admin**: Yönetim paneli
- **Django Debug Toolbar**: Geliştirme araçları

## 🚀 Kurulum

### 📋 Gereksinimler

- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)
- Git
- Modern web tarayıcısı

### 🔧 Adım Adım Kurulum

#### 1. Repository'yi Klonlayın
```bash
git clone https://github.com/resul067142/DinamikVeriPaneli.git
cd DinamikVeriPaneli
```

#### 2. Sanal Ortam Oluşturun
```bash
# Python venv kullanarak
python3 -m venv venv

# Sanal ortamı aktifleştirin
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

#### 4. Veritabanını Hazırlayın
```bash
# Django migrations'ları çalıştırın
python manage.py makemigrations
python manage.py migrate

# Varsayılan verileri yükleyin
python manage.py loaddata iller.json
```

#### 5. Süper Kullanıcı Oluşturun
```bash
python manage.py createsuperuser
```

#### 6. Sunucuyu Başlatın
```bash
python manage.py runserver
```

#### 7. Tarayıcıda Açın
```
http://localhost:8000
```

### 🐳 Docker ile Kurulum (Opsiyonel)

```bash
# Docker Compose ile
docker-compose up -d

# Veya Docker ile
docker build -t dinamik-veri-paneli .
docker run -p 8000:8000 dinamik-veri-paneli
```

## 📱 Kullanım

### 🏠 Ana Sayfa
- **Genel İstatistikler**: Türkiye geneli cihaz durumu
- **İl Bazlı Veriler**: Her il için detaylı bilgiler
- **Grafikler**: 4 farklı istatistik grafiği
- **Yönetim Kartları**: Ekip üyeleri ve iletişim bilgileri

### 📊 Veri Listesi
- **Tablolar**: Tüm verilerin listesi
- **Filtreleme**: Sütun bazında arama
- **Sıralama**: Çoklu sıralama seçenekleri
- **Düzenleme**: Veri ekleme, düzenleme, silme

### ⚙️ Sütun Yönetimi
- **Sütun Ekleme**: Yeni veri alanları oluşturma
- **Sütun Düzenleme**: Mevcut sütunları güncelleme
- **Sütun Silme**: Gereksiz sütunları kaldırma
- **Sıralama**: Sütun görüntüleme sırası

### 👥 Kullanıcı Yönetimi
- **Kullanıcı Ekleme**: Yeni kullanıcılar oluşturma
- **Rol Atama**: Admin ve kullanıcı rolleri
- **Yetki Yönetimi**: Detaylı izin sistemi

### 🎨 Uygulama Ayarları
- **Logo Değiştirme**: App logo yükleme
- **Başlık Düzenleme**: Uygulama adı değiştirme
- **Açıklama**: Uygulama açıklaması güncelleme

## 🔧 Yapılandırma

### 📁 Proje Yapısı
```
DinamikVeriPaneli/
├── dinamik_veri_paneli/          # Ana proje ayarları
│   ├── settings.py               # Django ayarları
│   ├── urls.py                   # Ana URL yapılandırması
│   └── wsgi.py                   # WSGI uygulaması
├── veri_yonetimi/                # Ana uygulama
│   ├── models.py                 # Veritabanı modelleri
│   ├── views.py                  # Görünüm fonksiyonları
│   ├── forms.py                  # Form sınıfları
│   ├── admin.py                  # Admin paneli
│   └── urls.py                   # Uygulama URL'leri
├── templates/                     # HTML şablonları
│   ├── base.html                 # Ana şablon
│   └── veri_yonetimi/            # Uygulama şablonları
├── static/                        # Statik dosyalar
├── media/                         # Kullanıcı yüklemeleri
└── requirements.txt               # Python bağımlılıkları
```

### ⚙️ Django Ayarları

#### settings.py Önemli Ayarlar
```python
# Veritabanı
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Statik dosyalar
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media dosyalar
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Dil ve saat dilimi
LANGUAGE_CODE = 'tr-tr'
TIME_ZONE = 'Europe/Istanbul'
```

### 🔐 Güvenlik Ayarları
```python
# Güvenlik ayarları
SECRET_KEY = 'your-secret-key-here'
DEBUG = False  # Production'da False olmalı
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# HTTPS ayarları (production)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## 📊 Veri Yapısı

### 🗄️ Ana Modeller

#### AnaVeri Modeli
```python
class AnaVeri(models.Model):
    il_adi = models.CharField(max_length=100, verbose_name="İl Adı")
    kurulacak_cihaz_sayisi = models.IntegerField(default=0)
    kurulan_cihaz_sayisi = models.IntegerField(default=0)
    arizali_cihaz_sayisi = models.IntegerField(default=0)
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    
    @property
    def tamamlanma_yuzdesi(self):
        if self.kurulacak_cihaz_sayisi > 0:
            return round((self.kurulan_cihaz_sayisi / self.kurulacak_cihaz_sayisi) * 100, 1)
        return 0
```

#### Sütun Modeli
```python
class Sütun(models.Model):
    ad = models.CharField(max_length=100, verbose_name="Sütun Adı")
    sıra = models.IntegerField(default=0, verbose_name="Görüntüleme Sırası")
    aktif = models.BooleanField(default=True, verbose_name="Aktif")
    tip = models.CharField(max_length=20, choices=TIP_SECENEKLERI, default='dinamik')
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
```

#### VeriDeger Modeli
```python
class VeriDeger(models.Model):
    veri = models.ForeignKey(AnaVeri, on_delete=models.CASCADE, related_name='degerler')
    sutun = models.ForeignKey(Sütun, on_delete=models.CASCADE)
    deger = models.TextField(verbose_name="Veri Değeri")
```

### 🔄 Veri İlişkileri
- **AnaVeri** ↔ **VeriDeger**: One-to-Many
- **Sütun** ↔ **VeriDeger**: One-to-Many
- **User** ↔ **UserProfile**: One-to-One

## 👥 Kullanıcı Yönetimi

### 🔐 Kullanıcı Rolleri

#### Süper Admin
- ✅ Tüm yetkilere sahip
- ✅ Kullanıcı yönetimi
- ✅ Sistem ayarları
- ✅ Veri yönetimi

#### Admin
- ✅ Veri ekleme/düzenleme/silme
- ✅ Sütun yönetimi
- ✅ Kısıtlı kullanıcı yönetimi

#### Kullanıcı
- ✅ Veri görüntüleme
- ✅ Kendi verilerini düzenleme
- ✅ Sınırlı erişim

### 👤 Kullanıcı Profili
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tc_kimlik = models.CharField(max_length=11, unique=True, verbose_name="TC Kimlik No")
    telefon = models.CharField(max_length=15, blank=True, verbose_name="Telefon")
    adres = models.TextField(blank=True, verbose_name="Adres")
```

## 🎨 UI/UX Özellikleri

### 🎨 Tasarım Prensipleri
- **Modern ve Minimal**: Temiz ve şık arayüz
- **Responsive**: Tüm cihazlarda mükemmel görünüm
- **Accessible**: Erişilebilirlik standartlarına uygun
- **Intuitive**: Sezgisel kullanıcı deneyimi

### 🌈 Renk Paleti
- **Primary**: Mavi tonları (#3B82F6)
- **Secondary**: Mor tonları (#8B5CF6)
- **Success**: Yeşil tonları (#10B981)
- **Warning**: Turuncu tonları (#F59E0B)
- **Error**: Kırmızı tonları (#EF4444)

### 📱 Responsive Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### 🎭 Animasyonlar
- **Hover Effects**: Buton ve kart hover animasyonları
- **Transitions**: Smooth geçiş efektleri
- **Loading States**: Yükleme durumu göstergeleri

## 📈 API ve Entegrasyon

### 🔌 REST API Endpoints

#### Veri Endpoints
```python
# Veri listesi
GET /api/veriler/
POST /api/veriler/
GET /api/veriler/{id}/
PUT /api/veriler/{id}/
DELETE /api/veriler/{id}/

# Sütun yönetimi
GET /api/sutunlar/
POST /api/sutunlar/
GET /api/sutunlar/{id}/
PUT /api/sutunlar/{id}/
DELETE /api/sutunlar/{id}/
```

#### Kullanıcı Endpoints
```python
# Kullanıcı yönetimi
GET /api/kullanicilar/
POST /api/kullanicilar/
GET /api/kullanicilar/{id}/
PUT /api/kullanicilar/{id}/
DELETE /api/kullanicilar/{id}/
```

### 🔄 Celery Entegrasyonu
```python
# Asenkron görevler
@shared_task
def veri_isleme_task(veri_id):
    # Veri işleme mantığı
    pass

@shared_task
def rapor_olusturma_task():
    # Rapor oluşturma mantığı
    pass
```

## 🔒 Güvenlik

### 🛡️ Güvenlik Önlemleri

#### Kimlik Doğrulama
- **Django Authentication**: Güvenli kullanıcı girişi
- **Session Management**: Güvenli oturum yönetimi
- **Password Policies**: Güçlü şifre politikaları

#### Yetkilendirme
- **Role-Based Access Control**: Rol tabanlı erişim kontrolü
- **Permission System**: Detaylı izin sistemi
- **CSRF Protection**: Cross-Site Request Forgery koruması

#### Veri Güvenliği
- **SQL Injection Protection**: Django ORM ile koruma
- **XSS Protection**: Cross-Site Scripting koruması
- **Input Validation**: Giriş verisi doğrulama

### 🔐 Güvenlik Ayarları
```python
# Güvenlik ayarları
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

## 🚀 Deployment

### 🌐 Production Sunucu

#### Gunicorn ile
```bash
# Gunicorn kurulumu
pip install gunicorn

# Sunucu başlatma
gunicorn --bind 0.0.0.0:8000 dinamik_veri_paneli.wsgi:application
```

#### Nginx ile
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location /static/ {
        alias /path/to/your/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/your/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 🐳 Docker ile Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=your-secret-key
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=dvp_db
      - POSTGRES_USER=dvp_user
      - POSTGRES_PASSWORD=dvp_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

## 📝 Katkıda Bulunma

### 🤝 Katkı Süreci

1. **Fork** yapın
2. **Feature branch** oluşturun (`git checkout -b feature/AmazingFeature`)
3. **Commit** yapın (`git commit -m 'Add some AmazingFeature'`)
4. **Push** yapın (`git push origin feature/AmazingFeature`)
5. **Pull Request** oluşturun

### 📋 Katkı Kuralları

- **Code Style**: PEP 8 Python standartlarına uyun
- **Documentation**: Yeni özellikler için dokümantasyon ekleyin
- **Testing**: Testler yazın ve çalıştırın
- **Commit Messages**: Açıklayıcı commit mesajları yazın

### 🐛 Bug Report

Bug bildirimi için:
1. **Issue** oluşturun
2. **Reproduction steps** ekleyin
3. **Expected vs Actual behavior** belirtin
4. **Environment details** ekleyin

## 📄 Lisans

Bu proje **MIT License** altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

- **Django Community**: Harika framework için
- **Tailwind CSS**: Modern CSS framework için
- **Contributors**: Projeye katkıda bulunan herkese

## 📞 İletişim

- **GitHub**: [@resul067142](https://github.com/resul067142)
- **Email**: resul067142@gmail.com
- **Project Link**: [https://github.com/resul067142/DinamikVeriPaneli](https://github.com/resul067142/DinamikVeriPaneli)

---

⭐ **Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!** ⭐

**Dinamik Veri Paneli** - Modern veri yönetimi çözümü 🚀

## 🚀 Hızlı Başlangıç - Proje Çalıştırma

### 📋 Basit Proje Çalıştırma Aşamaları

#### 1. **Proje Dizinine Git**
```bash
cd /Users/Admin/Desktop/81tablo4
```

#### 2. **Virtual Environment'ı Aktif Et**
```bash
source venv/bin/activate
```

#### 3. **Django Development Server'ı Başlat**
```bash
python manage.py runserver
```

#### 4. **Tek Satırda Çalıştırma (Önerilen)**
```bash
cd /Users/Admin/Desktop/81tablo4 && source venv/bin/activate && python manage.py runserver
```

### 🌐 Erişim Bilgileri
- **URL:** http://127.0.0.1:8000/ veya http://localhost:8000/
- **Port:** 8000

### ⚠️ Önemli Notlar
- Server'ı durdurmak için terminal'de `CONTROL-C` tuşlarına basın
- Virtual environment aktif olduğunda terminal prompt'unda `(venv)` görünür
- İlk çalıştırmada gerekli bağımlılıklar yüklenmiş olmalı

### 🔧 Ek Komutlar

#### Veritabanı İşlemleri
```bash
# Migrations oluştur
python manage.py makemigrations

# Migrations uygula
python manage.py migrate

# Superuser oluştur
python manage.py createsuperuser
```

#### Statik Dosyalar
```bash
# Statik dosyaları topla
python manage.py collectstatic
```

#### Shell
```bash
# Django shell'i aç
python manage.py shell
```

---

## 📝 Katkıda Bulunma
