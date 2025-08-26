from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from veri_yonetimi.models import Sütun, AnaVeri, VeriDeger


class Command(BaseCommand):
    help = 'Her il için il sorumlusu kullanıcıları oluştur'

    def handle(self, *args, **options):
        self.stdout.write('👥 İl sorumlusu kullanıcıları oluşturuluyor...')
        
        # İl verilerini al
        il_verileri = []
        for ana_veri in AnaVeri.objects.all():
            plaka = None
            il_adi = None
            
            for deger in ana_veri.degerler.all():
                if deger.sutun.ad == 'Plaka':
                    plaka = deger.deger
                elif deger.sutun.ad == 'İl Adı':
                    il_adi = deger.deger
            
            if plaka and il_adi:
                il_verileri.append({
                    'plaka': plaka,
                    'il_adi': il_adi
                })
        
        # İl sorumlusu grubunu oluştur
        il_sorumlusu_group, created = Group.objects.get_or_create(name='İl Sorumlusu')
        if created:
            self.stdout.write('  ✅ İl Sorumlusu grubu oluşturuldu')
        
        # Her il için kullanıcı oluştur
        created_users = []
        for il_data in il_verileri:
            username = f"{il_data['il_adi'].lower()}{il_data['plaka']}"
            password = f"{il_data['il_adi'].lower()}{il_data['plaka']}"
            
            # Kullanıcı zaten var mı kontrol et
            if User.objects.filter(username=username).exists():
                self.stdout.write(f'  ⚠️ {username} kullanıcısı zaten mevcut')
                continue
            
            # Kullanıcı oluştur
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=f"{il_data['il_adi']} İl Sorumlusu",
                last_name=il_data['plaka'],
                email=f"{username}@example.com",
                is_staff=True,  # Admin paneline erişim
                is_superuser=False  # Süper kullanıcı değil
            )
            
            # İl sorumlusu grubuna ekle
            user.groups.add(il_sorumlusu_group)
            
            created_users.append(user)
            self.stdout.write(f'  ✅ {username} kullanıcısı oluşturuldu (Şifre: {password})')
        
        self.stdout.write('')
        self.stdout.write('✅ İl sorumlusu kullanıcıları oluşturuldu!')
        self.stdout.write(f'📊 Toplam {len(created_users)} yeni kullanıcı eklendi.')
        self.stdout.write('')
        self.stdout.write('🔑 Kullanıcı Bilgileri:')
        self.stdout.write('   - Kullanıcı adı: iladiplaka (örn: adana01)')
        self.stdout.write('   - Şifre: iladiplaka (örn: adana01)')
        self.stdout.write('   - Yetki: İl Sorumlusu (sadece kendi ilini görebilir)')
        self.stdout.write('')
        self.stdout.write('👑 Admin Kullanıcı:')
        self.stdout.write('   - Kullanıcı adı: admin')
        self.stdout.write('   - Şifre: admin')
        self.stdout.write('   - Yetki: Süper Kullanıcı (her şeyi görebilir)')
