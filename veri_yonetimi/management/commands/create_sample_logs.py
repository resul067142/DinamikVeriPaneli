from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from veri_yonetimi.models import UserLog
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Örnek kullanıcı işlem logları oluşturur'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Oluşturulacak log sayısı (varsayılan: 50)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Mevcut kullanıcıları al
        users = list(User.objects.all())
        if not users:
            self.stdout.write(
                self.style.ERROR('Hiç kullanıcı bulunamadı. Önce kullanıcı oluşturun.')
            )
            return
        
        # Örnek işlem tipleri ve açıklamaları
        islem_ornekleri = [
            ('kullanici_olusturuldu', '{} kullanıcısı oluşturuldu'),
            ('kullanici_guncellendi', '{} kullanıcısının bilgileri güncellendi'),
            ('durum_degistirildi', '{} kullanıcısı {} yapıldı'),
            ('yetki_degistirildi', '{} kullanıcısının yetkisi {} olarak değiştirildi'),
            ('giris_yapildi', '{} kullanıcısı sisteme giriş yaptı'),
            ('cikis_yapildi', '{} kullanıcısı sistemden çıkış yaptı'),
            ('profil_guncellendi', '{} kullanıcısının profil bilgileri güncellendi'),
            ('veri_eklendi', '{} kullanıcısı yeni veri ekledi'),
            ('veri_guncellendi', '{} kullanıcısı veri güncelledi'),
            ('veri_silindi', '{} kullanıcısı veri sildi'),
            ('sutun_eklendi', '{} kullanıcısı yeni sütun ekledi'),
            ('sutun_guncellendi', '{} kullanıcısı sütun güncelledi'),
            ('sutun_silindi', '{} kullanıcısı sütun sildi'),
        ]
        
        # Örnek IP adresleri
        ip_adresleri = [
            '192.168.1.100',
            '192.168.1.101',
            '10.0.0.5',
            '172.16.1.50',
            '203.0.113.15',
            '198.51.100.25'
        ]
        
        # Örnek User Agent strings
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        
        created_count = 0
        
        for i in range(count):
            # Rastgele kullanıcı seç
            user = random.choice(users)
            islem_yapan = random.choice(users)
            
            # Rastgele işlem tipi ve açıklama seç
            islem_tipi, aciklama_template = random.choice(islem_ornekleri)
            
            # Açıklamayı oluştur
            if '{}' in aciklama_template:
                if 'yapıldı' in aciklama_template and 'degistirildi' not in aciklama_template:
                    durum = random.choice(['aktif', 'pasif'])
                    aciklama = aciklama_template.format(user.username, durum)
                elif 'yetki' in aciklama_template:
                    yetki = random.choice(['Admin', 'İl Sorumlusu', 'Normal Kullanıcı'])
                    aciklama = aciklama_template.format(user.username, yetki)
                else:
                    aciklama = aciklama_template.format(user.username)
            else:
                aciklama = aciklama_template
            
            # Rastgele tarih (son 30 gün içinde)
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            
            tarih = timezone.now() - timedelta(
                days=days_ago,
                hours=hours_ago,
                minutes=minutes_ago
            )
            
            # Rastgele IP ve User Agent
            ip_adresi = random.choice(ip_adresleri)
            user_agent = random.choice(user_agents)
            
            # Örnek eski ve yeni değerler
            eski_deger = None
            yeni_deger = None
            
            if islem_tipi == 'durum_degistirildi':
                eski_deger = {'is_active': random.choice([True, False])}
                yeni_deger = {'is_active': not eski_deger['is_active']}
            elif islem_tipi == 'yetki_degistirildi':
                eski_roller = [
                    {'is_superuser': True, 'is_staff': True},
                    {'is_superuser': False, 'is_staff': True},
                    {'is_superuser': False, 'is_staff': False}
                ]
                eski_deger = random.choice(eski_roller)
                yeni_deger = random.choice(eski_roller)
            elif islem_tipi == 'kullanici_olusturuldu':
                yeni_deger = {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_superuser': user.is_superuser,
                    'is_staff': user.is_staff
                }
            
            # Log kaydını oluştur
            try:
                UserLog.objects.create(
                    user=user,
                    islem_yapan=islem_yapan,
                    islem_tipi=islem_tipi,
                    aciklama=aciklama,
                    ip_adresi=ip_adresi,
                    user_agent=user_agent,
                    eski_deger=eski_deger,
                    yeni_deger=yeni_deger,
                    tarih=tarih
                )
                created_count += 1
                
                if created_count % 10 == 0:
                    self.stdout.write(f'✅ {created_count} log kaydı oluşturuldu...')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Log oluşturulurken hata: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Toplam {created_count} adet örnek kullanıcı işlem logu başarıyla oluşturuldu!'
            )
        )
        
        # İstatistikleri göster
        total_logs = UserLog.objects.count()
        today_logs = UserLog.objects.filter(tarih__date=timezone.now().date()).count()
        
        self.stdout.write(f'📊 Toplam log sayısı: {total_logs}')
        self.stdout.write(f'📈 Bugünkü log sayısı: {today_logs}')
