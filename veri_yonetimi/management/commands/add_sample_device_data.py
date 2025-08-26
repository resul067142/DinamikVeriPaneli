from django.core.management.base import BaseCommand
from veri_yonetimi.models import AnaVeri
import random

class Command(BaseCommand):
    help = 'Mevcut verilere örnek cihaz sayıları ekler'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Mevcut cihaz sayılarını da değiştir',
        )

    def handle(self, *args, **options):
        self.stdout.write('📱 Örnek cihaz sayıları ekleniyor...')
        
        # Mevcut verileri al
        veriler = AnaVeri.objects.all()
        updated_count = 0
        
        for veri in veriler:
            # Eğer zaten cihaz sayısı varsa ve force kullanılmıyorsa atla
            if veri.kurulacak_cihaz_sayisi > 0 and not options['force']:
                self.stdout.write(f'⚠️  Veri #{veri.id} için zaten cihaz sayısı mevcut: {veri.kurulacak_cihaz_sayisi}')
                continue
            
            # Rastgele cihaz sayıları oluştur
            kurulacak = random.randint(50, 200)  # 50-200 arası
            kurulan = random.randint(0, kurulacak)  # 0 ile kurulacak arası
            
            # Cihaz sayılarını güncelle
            veri.kurulacak_cihaz_sayisi = kurulacak
            veri.kurulan_cihaz_sayisi = kurulan
            veri.save()
            
            updated_count += 1
            self.stdout.write(f'✅ Veri #{veri.id} güncellendi: Kurulacak: {kurulacak}, Kurulan: {kurulan}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 İşlem tamamlandı! Güncellenen veri sayısı: {updated_count}'
            )
        )
