from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from veri_yonetimi.models import UserProfile
import random

class Command(BaseCommand):
    help = 'Mevcut kullanıcılar için fake TC kimlik numaraları oluşturur'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Mevcut TC kimlik numaralarını da değiştir',
        )

    def handle(self, *args, **options):
        self.stdout.write('🆔 Fake TC kimlik numaraları oluşturuluyor...')
        
        # Mevcut kullanıcıları al
        users = User.objects.all()
        created_count = 0
        updated_count = 0
        
        for user in users:
            # TC kimlik numarası kontrolü
            if hasattr(user, 'profile') and user.profile.tc_kimlik and not options['force']:
                self.stdout.write(f'⚠️  {user.username} için zaten TC kimlik numarası mevcut: {user.profile.tc_kimlik}')
                continue
            
            # Fake TC kimlik numarası oluştur
            fake_tc = self.generate_fake_tc()
            
            # UserProfile oluştur veya güncelle
            if hasattr(user, 'profile'):
                user.profile.tc_kimlik = fake_tc
                user.profile.save()
                updated_count += 1
                self.stdout.write(f'✅ {user.username} TC kimlik numarası güncellendi: {fake_tc}')
            else:
                UserProfile.objects.create(user=user, tc_kimlik=fake_tc)
                created_count += 1
                self.stdout.write(f'➕ {user.username} için TC kimlik numarası oluşturuldu: {fake_tc}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 İşlem tamamlandı! '
                f'Yeni oluşturulan: {created_count}, '
                f'Güncellenen: {updated_count}'
            )
        )

    def generate_fake_tc(self):
        """Geçerli fake TC kimlik numarası oluştur"""
        while True:
            # İlk 9 haneyi rastgele oluştur
            first_nine = ''.join([str(random.randint(0, 9)) for _ in range(9)])
            
            # 10. hane (1. kontrol hanesi)
            sum_odd = sum(int(first_nine[i]) for i in range(0, 9, 2))
            sum_even = sum(int(first_nine[i]) for i in range(1, 8, 2))
            
            digit_10 = (sum_odd * 7 - sum_even) % 10
            
            # 11. hane (2. kontrol hanesi)
            first_ten = first_nine + str(digit_10)
            sum_all = sum(int(first_ten[i]) for i in range(10))
            
            digit_11 = sum_all % 10
            
            # Tam TC kimlik numarası
            tc = first_nine + str(digit_10) + str(digit_11)
            
            # Benzersizlik kontrolü
            if not UserProfile.objects.filter(tc_kimlik=tc).exists():
                return tc
