from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from veri_yonetimi.models import AnaVeri, Sütun, VeriDeger, UserProfile, UserLog
import random
import json
from datetime import datetime, timedelta
from faker import Faker

class Command(BaseCommand):
    help = 'Tüm alanlara kapsamlı fake veriler ekler (10\'ar adet)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Her kategoride oluşturulacak veri sayısı (varsayılan: 10)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Mevcut verileri temizle',
        )

    def handle(self, *args, **options):
        self.fake = Faker('tr_TR')  # Türkçe fake data
        count = options['count']
        
        self.stdout.write('🚀 Kapsamlı fake veri oluşturma işlemi başlıyor...')
        
        if options['clear']:
            self.clear_existing_data()
        
        # 1. İller listesi yükle
        self.load_cities()
        
        # 2. Sütunları oluştur
        self.create_columns()
        
        # 3. Kullanıcıları oluştur
        self.create_users(count)
        
        # 4. Ana verileri oluştur
        self.create_ana_veri(count)
        
        # 5. Dinamik sütun değerlerini oluştur
        self.create_veri_deger()
        
        # 6. Kullanıcı loglarını oluştur
        self.create_user_logs(count * 5)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 İşlem tamamlandı! Toplamda {count} adet veri oluşturuldu.'
            )
        )

    def clear_existing_data(self):
        """Mevcut verileri temizle"""
        self.stdout.write('🗑️  Mevcut veriler temizleniyor...')
        VeriDeger.objects.all().delete()
        AnaVeri.objects.all().delete()
        UserLog.objects.all().delete()
        # Kullanıcıları ve sütunları koruyoruz
        self.stdout.write('✅ Mevcut veriler temizlendi.')

    def load_cities(self):
        """Türkiye illerini yükle"""
        self.turkish_cities = [
            'Adana', 'Adıyaman', 'Afyonkarahisar', 'Ağrı', 'Amasya', 'Ankara', 'Antalya', 'Artvin',
            'Aydın', 'Balıkesir', 'Bilecik', 'Bingöl', 'Bitlis', 'Bolu', 'Burdur', 'Bursa',
            'Çanakkale', 'Çankırı', 'Çorum', 'Denizli', 'Diyarbakır', 'Edirne', 'Elazığ', 'Erzincan',
            'Erzurum', 'Eskişehir', 'Gaziantep', 'Giresun', 'Gümüşhane', 'Hakkari', 'Hatay', 'Isparta',
            'Mersin', 'İstanbul', 'İzmir', 'Kars', 'Kastamonu', 'Kayseri', 'Kırklareli', 'Kırşehir',
            'Kocaeli', 'Konya', 'Kütahya', 'Malatya', 'Manisa', 'Kahramanmaraş', 'Mardin', 'Muğla',
            'Muş', 'Nevşehir', 'Niğde', 'Ordu', 'Rize', 'Sakarya', 'Samsun', 'Siirt', 'Sinop',
            'Sivas', 'Tekirdağ', 'Tokat', 'Trabzon', 'Tunceli', 'Şanlıurfa', 'Uşak', 'Van',
            'Yozgat', 'Zonguldak', 'Aksaray', 'Bayburt', 'Karaman', 'Kırıkkale', 'Batman', 'Şırnak',
            'Bartın', 'Ardahan', 'Iğdır', 'Yalova', 'Karabük', 'Kilis', 'Osmaniye', 'Düzce'
        ]
        self.stdout.write(f'📍 {len(self.turkish_cities)} il listesi yüklendi.')

    def create_columns(self):
        """Örnek sütunlar oluştur"""
        self.stdout.write('📊 Sütunlar oluşturuluyor...')
        
        # Mevcut sütunları kontrol et
        if Sütun.objects.exists():
            self.stdout.write('⚠️  Sütunlar zaten mevcut, yenileri ekleniyor...')
        
        columns_data = [
            # Veri Listesi Sütunları
            {'ad': 'İl Adı', 'tip': 'dinamik', 'menu_tipi': 'veri_listesi', 'sıra': 1},
            {'ad': 'Kurulacak Cihaz', 'tip': 'kurulacak', 'menu_tipi': 'veri_listesi', 'sıra': 2},
            {'ad': 'Kurulan Cihaz', 'tip': 'kurulan', 'menu_tipi': 'veri_listesi', 'sıra': 3},
            {'ad': 'Arızalı Cihaz', 'tip': 'arizali', 'menu_tipi': 'veri_listesi', 'sıra': 4},
            {'ad': 'Tamamlanma %', 'tip': 'tamamlanma', 'menu_tipi': 'veri_listesi', 'sıra': 5},
            {'ad': 'Nüfus', 'tip': 'dinamik', 'menu_tipi': 'veri_listesi', 'sıra': 6},
            {'ad': 'Bölge', 'tip': 'dinamik', 'menu_tipi': 'veri_listesi', 'sıra': 7},
            {'ad': 'Ekonomi Kodu', 'tip': 'dinamik', 'menu_tipi': 'veri_listesi', 'sıra': 8},
            
            # Cihaz Türleri Sütunları
            {'ad': 'Cihaz Türü', 'tip': 'cihaz_turleri', 'menu_tipi': 'cihaz_turleri', 'sıra': 1},
            {'ad': 'Kategori', 'tip': 'cihaz_turleri', 'menu_tipi': 'cihaz_turleri', 'sıra': 2},
            {'ad': 'Durum', 'tip': 'cihaz_turleri', 'menu_tipi': 'cihaz_turleri', 'sıra': 3},
            {'ad': 'Kurulum Sayısı', 'tip': 'cihaz_turleri', 'menu_tipi': 'cihaz_turleri', 'sıra': 4},
            {'ad': 'Hedef Sayı', 'tip': 'cihaz_turleri', 'menu_tipi': 'cihaz_turleri', 'sıra': 5},
            {'ad': 'Performans', 'tip': 'cihaz_turleri', 'menu_tipi': 'cihaz_turleri', 'sıra': 6},
            
            # Genel Sütunlar
            {'ad': 'Proje Kodu', 'tip': 'dinamik', 'menu_tipi': 'genel', 'sıra': 1},
            {'ad': 'Sorumlu Ekip', 'tip': 'dinamik', 'menu_tipi': 'genel', 'sıra': 2},
            {'ad': 'Öncelik', 'tip': 'dinamik', 'menu_tipi': 'genel', 'sıra': 3},
            {'ad': 'Son Güncelleme', 'tip': 'dinamik', 'menu_tipi': 'genel', 'sıra': 4},
        ]
        
        created_count = 0
        for col_data in columns_data:
            sutun, created = Sütun.objects.get_or_create(
                ad=col_data['ad'],
                menu_tipi=col_data['menu_tipi'],
                defaults={
                    'tip': col_data['tip'],
                    'sıra': col_data['sıra'],
                    'aktif': True,
                    'gorunur': True,
                    'genislik': '120px',
                    'hizalama': 'center'
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'✅ {created_count} yeni sütun oluşturuldu.')

    def create_users(self, count):
        """Örnek kullanıcılar oluştur"""
        self.stdout.write(f'👥 {count} kullanıcı oluşturuluyor...')
        
        user_roles = ['operator', 'supervisor', 'manager', 'admin']
        regions = ['Marmara', 'Ege', 'Akdeniz', 'İç Anadolu', 'Karadeniz', 'Doğu Anadolu', 'Güneydoğu Anadolu']
        
        created_count = 0
        for i in range(count):
            username = f'user_{self.fake.first_name().lower()}_{i+1}'
            
            # Kullanıcı zaten varsa atla
            if User.objects.filter(username=username).exists():
                continue
            
            role = random.choice(user_roles)
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            
            user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='demo123',
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                is_staff=role in ['admin', 'manager'],
                is_superuser=role == 'admin'
            )
            
            # UserProfile oluştur
            profile = UserProfile.objects.create(
                user=user,
                tc_kimlik=self.generate_fake_tc(),
                sorumlu_iller=', '.join(random.sample(self.turkish_cities, random.randint(1, 5)))
            )
            
            created_count += 1
            self.stdout.write(f'  ✅ {username} ({role}) - {profile.get_sorumlu_iller_display()}')
        
        self.stdout.write(f'✅ {created_count} kullanıcı oluşturuldu.')

    def generate_fake_tc(self):
        """Fake TC kimlik numarası oluştur"""
        # İlk 9 hanesi rastgele, son 2 hane kontrol hanesi (basit algoritma)
        digits = [random.randint(1, 9)]  # İlk hane 0 olamaz
        digits.extend([random.randint(0, 9) for _ in range(8)])
        
        # Basit kontrol hanesi (gerçek algoritma değil)
        check1 = sum(digits[i] for i in range(0, 9, 2)) * 7 - sum(digits[i] for i in range(1, 8, 2))
        digits.append(check1 % 10)
        
        check2 = (sum(digits[:10])) % 10
        digits.append(check2)
        
        return ''.join(map(str, digits))

    def create_ana_veri(self, count):
        """Ana veri kayıtları oluştur"""
        self.stdout.write(f'📋 {count} ana veri kaydı oluşturuluyor...')
        
        regions = {
            'Marmara': ['İstanbul', 'Bursa', 'Kocaeli', 'Tekirdağ', 'Balıkesir'],
            'Ege': ['İzmir', 'Manisa', 'Aydın', 'Muğla', 'Denizli'],
            'Akdeniz': ['Antalya', 'Mersin', 'Adana', 'Hatay', 'Isparta'],
            'İç Anadolu': ['Ankara', 'Konya', 'Kayseri', 'Eskişehir', 'Sivas'],
            'Karadeniz': ['Samsun', 'Trabzon', 'Ordu', 'Giresun', 'Rize'],
            'Doğu Anadolu': ['Erzurum', 'Van', 'Malatya', 'Elazığ', 'Ağrı'],
            'Güneydoğu Anadolu': ['Gaziantep', 'Diyarbakır', 'Şanlıurfa', 'Mardin', 'Batman']
        }
        
        created_count = 0
        for i in range(count):
            # Rastgele il seç
            region = random.choice(list(regions.keys()))
            il_adi = random.choice(regions[region])
            
            # Cihaz sayıları oluştur
            kurulacak = random.randint(50, 500)
            kurulan = random.randint(0, kurulacak)
            arizali = random.randint(0, kurulan // 10)  # Kurulanlın %10'u kadar arızalı
            
            # AnaVeri oluştur
            ana_veri = AnaVeri.objects.create(
                il_adi=il_adi,
                kurulacak_cihaz_sayisi=kurulacak,
                kurulan_cihaz_sayisi=kurulan,
                arizali_cihaz_sayisi=arizali
            )
            
            created_count += 1
            completion = ana_veri.tamamlanma_yuzdesi
            self.stdout.write(
                f'  ✅ {il_adi}: {kurulan}/{kurulacak} cihaz (%{completion:.1f})'
            )
        
        self.stdout.write(f'✅ {created_count} ana veri kaydı oluşturuldu.')

    def create_veri_deger(self):
        """Dinamik sütun değerleri oluştur"""
        self.stdout.write('🔗 Dinamik sütun değerleri oluşturuluyor...')
        
        ana_veriler = AnaVeri.objects.all()
        dinamik_sutunlar = Sütun.objects.filter(tip='dinamik')
        
        # Değer şablonları
        sample_values = {
            'Nüfus': lambda: f"{random.randint(100000, 5000000):,}",
            'Bölge': lambda: random.choice(['Marmara', 'Ege', 'Akdeniz', 'İç Anadolu', 'Karadeniz', 'Doğu Anadolu', 'Güneydoğu Anadolu']),
            'Ekonomi Kodu': lambda: f"EKO-{random.randint(1000, 9999)}",
            'Proje Kodu': lambda: f"PRJ-{random.randint(2024, 2025)}-{random.randint(100, 999)}",
            'Sorumlu Ekip': lambda: f"Ekip {random.choice(['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon'])}",
            'Öncelik': lambda: random.choice(['Yüksek', 'Orta', 'Düşük', 'Kritik']),
            'Son Güncelleme': lambda: (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%d.%m.%Y'),
            'Cihaz Türü': lambda: random.choice(['Router', 'Switch', 'Access Point', 'Firewall', 'Load Balancer']),
            'Kategori': lambda: random.choice(['Ağ', 'Güvenlik', 'Erişim', 'Yönetim']),
            'Durum': lambda: random.choice(['Aktif', 'Bakımda', 'Arızalı', 'Test']),
            'Kurulum Sayısı': lambda: str(random.randint(1, 100)),
            'Hedef Sayı': lambda: str(random.randint(50, 200)),
            'Performans': lambda: f"%{random.randint(70, 99)}"
        }
        
        created_count = 0
        for ana_veri in ana_veriler:
            for sutun in dinamik_sutunlar:
                # Değer üret
                if sutun.ad in sample_values:
                    deger = sample_values[sutun.ad]()
                else:
                    deger = f"Değer-{random.randint(1, 1000)}"
                
                # VeriDeger oluştur
                veri_deger, created = VeriDeger.objects.get_or_create(
                    ana_veri=ana_veri,
                    sutun=sutun,
                    defaults={'deger': deger}
                )
                
                if created:
                    created_count += 1
        
        self.stdout.write(f'✅ {created_count} dinamik değer oluşturuldu.')

    def create_user_logs(self, count):
        """Kullanıcı işlem logları oluştur"""
        self.stdout.write(f'📝 {count} kullanıcı logu oluşturuluyor...')
        
        users = list(User.objects.all())
        if not users:
            self.stdout.write('⚠️  Kullanıcı bulunamadı, log oluşturulamadı.')
            return
        
        log_types = [
            'kullanici_olusturuldu', 'kullanici_guncellendi', 'giris_yapildi',
            'cikis_yapildi', 'veri_eklendi', 'veri_guncellendi', 'sutun_eklendi'
        ]
        
        created_count = 0
        for i in range(count):
            user = random.choice(users)
            islem_yapan = random.choice(users)
            islem_tipi = random.choice(log_types)
            
            # Log açıklaması oluştur
            descriptions = {
                'kullanici_olusturuldu': f'{user.first_name} {user.last_name} kullanıcısı oluşturuldu',
                'kullanici_guncellendi': f'{user.first_name} {user.last_name} kullanıcısı güncellendi',
                'giris_yapildi': f'{user.username} sisteme giriş yaptı',
                'cikis_yapildi': f'{user.username} sistemden çıkış yaptı',
                'veri_eklendi': f'Yeni veri kaydı eklendi',
                'veri_guncellendi': f'Veri kaydı güncellendi',
                'sutun_eklendi': f'Yeni sütun eklendi',
            }
            
            log = UserLog.objects.create(
                user=user,
                islem_yapan=islem_yapan,
                islem_tipi=islem_tipi,
                aciklama=descriptions.get(islem_tipi, 'Sistem işlemi gerçekleştirildi'),
                ip_adresi=f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
                user_agent=random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                ]),
                eski_deger={'field': 'old_value'} if random.choice([True, False]) else None,
                yeni_deger={'field': 'new_value'} if random.choice([True, False]) else None
            )
            
            # Tarihini geçmişe kaydır
            log.tarih = datetime.now() - timedelta(days=random.randint(1, 30))
            log.save()
            
            created_count += 1
        
        self.stdout.write(f'✅ {created_count} kullanıcı logu oluşturuldu.')
