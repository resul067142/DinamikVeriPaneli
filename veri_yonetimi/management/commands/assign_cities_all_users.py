from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from veri_yonetimi.models import UserProfile
import random


class Command(BaseCommand):
    help = 'Tüm kullanıcılara rastgele il ataması yapar'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-cities',
            type=int,
            default=1,
            help='Minimum atanacak il sayısı (varsayılan: 1)'
        )
        parser.add_argument(
            '--max-cities',
            type=int,
            default=5,
            help='Maksimum atanacak il sayısı (varsayılan: 5)'
        )

    def handle(self, *args, **options):
        min_cities = options['min_cities']
        max_cities = options['max_cities']
        
        # Türkiye illeri listesi
        turkiye_illeri = [
            'Adana', 'Adıyaman', 'Afyonkarahisar', 'Ağrı', 'Amasya', 'Ankara', 'Antalya', 'Artvin', 
            'Aydın', 'Balıkesir', 'Bilecik', 'Bingöl', 'Bitlis', 'Bolu', 'Burdur', 'Bursa', 
            'Çanakkale', 'Çankırı', 'Çorum', 'Denizli', 'Diyarbakır', 'Edirne', 'Elazığ', 'Erzincan', 
            'Erzurum', 'Eskişehir', 'Gaziantep', 'Giresun', 'Gümüşhane', 'Hakkari', 'Hatay', 'Isparta', 
            'Mersin', 'İstanbul', 'İzmir', 'Kars', 'Kastamonu', 'Kayseri', 'Kırklareli', 'Kırşehir', 
            'Kocaeli', 'Konya', 'Kütahya', 'Malatya', 'Manisa', 'Kahramanmaraş', 'Mardin', 'Muğla', 
            'Muş', 'Nevşehir', 'Niğde', 'Ordu', 'Rize', 'Sakarya', 'Samsun', 'Siirt', 'Sinop', 
            'Sivas', 'Tekirdağ', 'Tokat', 'Trabzon', 'Tunceli', 'Şanlıurfa', 'Uşak', 'Van', 'Yozgat', 
            'Zonguldak', 'Aksaray', 'Bayburt', 'Karaman', 'Kırıkkale', 'Batman', 'Şırnak', 'Bartın', 
            'Ardahan', 'Iğdır', 'Yalova', 'Karabük', 'Kilis', 'Osmaniye', 'Düzce'
        ]
        
        # Tüm kullanıcıları al
        users = User.objects.all()
        updated_count = 0
        
        for user in users:
            # UserProfile oluştur veya getir
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Superuser'lara il ataması yapma (tüm illere erişebilirler)
            if user.is_superuser:
                if profile.sorumlu_iller:
                    profile.sorumlu_iller = ''
                    profile.save()
                    self.stdout.write(
                        self.style.WARNING(f'🔓 {user.username} (Admin) - Tüm illere erişim')
                    )
                continue
            
            # Rastgele il sayısı belirle
            num_cities = random.randint(min_cities, max_cities)
            
            # Rastgele iller seç
            selected_cities = random.sample(turkiye_illeri, num_cities)
            
            # İl atamasını yap
            profile.set_sorumlu_iller(selected_cities)
            profile.save()
            
            updated_count += 1
            cities_str = ', '.join(selected_cities)
            self.stdout.write(
                self.style.SUCCESS(f'✅ {user.username} - {num_cities} il: {cities_str}')
            )
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'🎉 Toplam {updated_count} kullanıcıya il ataması yapıldı!')
        )
        self.stdout.write(
            self.style.WARNING(f'📍 {min_cities}-{max_cities} il arasında rastgele atama yapıldı.')
        )
