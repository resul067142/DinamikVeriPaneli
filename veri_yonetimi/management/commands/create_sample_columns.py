from django.core.management.base import BaseCommand
from veri_yonetimi.models import Sütun

class Command(BaseCommand):
    help = 'Sütun yönetimi için örnek sütunlar oluşturur'

    def handle(self, *args, **options):
        # Mevcut sütunları temizle
        Sütun.objects.all().delete()
        
        # Veri Listesi için sütunlar
        veri_listesi_sutunlar = [
            {'ad': 'İl Adı', 'tip': 'dinamik', 'menu_tipi': 'veri_listesi', 'sıra': 1, 'aktif': True, 'gorunur': True, 'genislik': '150px', 'hizalama': 'left'},
            {'ad': 'Kurulacak Cihaz', 'tip': 'kurulacak', 'menu_tipi': 'veri_listesi', 'sıra': 2, 'aktif': True, 'gorunur': True, 'genislik': '120px', 'hizalama': 'center'},
            {'ad': 'Kurulan Cihaz', 'tip': 'kurulan', 'menu_tipi': 'veri_listesi', 'sıra': 3, 'aktif': True, 'gorunur': True, 'genislik': '120px', 'hizalama': 'center'},
            {'ad': 'Arızalı Cihaz', 'tip': 'arizali', 'menu_tipi': 'veri_listesi', 'sıra': 4, 'aktif': True, 'gorunur': True, 'genislik': '120px', 'hizalama': 'center'},
            {'ad': 'Tamamlanma %', 'tip': 'tamamlanma', 'menu_tipi': 'veri_listesi', 'sıra': 5, 'aktif': True, 'gorunur': True, 'genislik': '140px', 'hizalama': 'center'},
        ]
        
        # Cihaz Türleri için sütunlar
        cihaz_turleri_sutunlar = [
            {'ad': 'Cihaz', 'tip': 'cihaz_turleri', 'menu_tipi': 'cihaz_turleri', 'sıra': 1, 'aktif': True, 'gorunur': True, 'genislik': '200px', 'hizalama': 'left'},
            {'ad': 'Kategori', 'tip': 'cihaz_turleri', 'menu_tipi': 'cihaz_turleri', 'sıra': 2, 'aktif': True, 'gorunur': True, 'genislik': '120px', 'hizalama': 'center'},
            {'ad': 'Durum', 'tip': 'cihaz_turleri', 'menu_tipi': 'cihaz_turleri', 'sıra': 3, 'aktif': True, 'gorunur': True, 'genislik': '100px', 'hizalama': 'center'},
            {'ad': 'Kurulum', 'tip': 'cihaz_turleri', 'menu_tipi': 'cihaz_turleri', 'sıra': 4, 'aktif': True, 'gorunur': True, 'genislik': '100px', 'hizalama': 'center'},
            {'ad': 'Hedef', 'tip': 'cihaz_turleri', 'menu_tipi': 'cihaz_turleri', 'sıra': 5, 'aktif': True, 'gorunur': True, 'genislik': '100px', 'hizalama': 'center'},
            {'ad': 'Tamamlanma', 'tip': 'cihaz_turleri', 'menu_tipi': 'cihaz_turleri', 'sıra': 6, 'aktif': True, 'gorunur': True, 'genislik': '140px', 'hizalama': 'center'},
        ]
        
        # Tüm sütunları birleştir
        tum_sutunlar = veri_listesi_sutunlar + cihaz_turleri_sutunlar
        
        # Sütunları oluştur
        for sutun_data in tum_sutunlar:
            Sütun.objects.create(**sutun_data)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Başarıyla {len(tum_sutunlar)} örnek sütun oluşturuldu!'
            )
        )
        
        # Özet bilgi
        self.stdout.write('\nOluşturulan sütunlar:')
        for sutun in Sütun.objects.all().order_by('menu_tipi', 'sıra'):
            self.stdout.write(f'  - {sutun.menu_tipi}: {sutun.ad} (Sıra: {sutun.sıra})')
