import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from veri_yonetimi.models import AnaVeri, Sütun, VeriDeger

class Command(BaseCommand):
    help = 'Tüm verileri sil ve 81 il için yeni mantıkta veriler oluştur'

    def handle(self, *args, **options):
        self.stdout.write('🗑️ Tüm mevcut veriler siliniyor...')
        
        # Tüm verileri sil
        AnaVeri.objects.all().delete()
        VeriDeger.objects.all().delete()
        Sütun.objects.all().delete()
        
        self.stdout.write('✅ Tüm veriler silindi.')
        
        # Yeni sütunları oluştur
        self.stdout.write('📊 Yeni sütunlar oluşturuluyor...')
        
        sutunlar = [
            {'ad': 'Plaka', 'sıra': 1, 'aktif': True},
            {'ad': 'İl Adı', 'sıra': 2, 'aktif': True},
            {'ad': 'Kurulacak Cihaz Sayısı', 'sıra': 3, 'aktif': True},
            {'ad': 'Kurulan Cihaz Sayısı', 'sıra': 4, 'aktif': True},
            {'ad': 'Arızalı Cihaz Sayısı', 'sıra': 5, 'aktif': True},
        ]
        
        for sutun_data in sutunlar:
            sutun = Sütun.objects.create(**sutun_data)
            self.stdout.write(f'  ✅ {sutun.ad} sütunu oluşturuldu')
        
        self.stdout.write('✅ Tüm sütunlar oluşturuldu.')
        
        # 81 il için veriler oluştur
        self.stdout.write('🏙️ 81 il için veriler oluşturuluyor...')
        
        # Türkiye'nin 81 ili
        iller = [
            {'plaka': '01', 'il_adi': 'Adana'},
            {'plaka': '02', 'il_adi': 'Adıyaman'},
            {'plaka': '03', 'il_adi': 'Afyonkarahisar'},
            {'plaka': '04', 'il_adi': 'Ağrı'},
            {'plaka': '05', 'il_adi': 'Amasya'},
            {'plaka': '06', 'il_adi': 'Ankara'},
            {'plaka': '07', 'il_adi': 'Antalya'},
            {'plaka': '08', 'il_adi': 'Artvin'},
            {'plaka': '09', 'il_adi': 'Aydın'},
            {'plaka': '10', 'il_adi': 'Balıkesir'},
            {'plaka': '11', 'il_adi': 'Bilecik'},
            {'plaka': '12', 'il_adi': 'Bingöl'},
            {'plaka': '13', 'il_adi': 'Bitlis'},
            {'plaka': '14', 'il_adi': 'Bolu'},
            {'plaka': '15', 'il_adi': 'Burdur'},
            {'plaka': '16', 'il_adi': 'Bursa'},
            {'plaka': '17', 'il_adi': 'Çanakkale'},
            {'plaka': '18', 'il_adi': 'Çankırı'},
            {'plaka': '19', 'il_adi': 'Çorum'},
            {'plaka': '20', 'il_adi': 'Denizli'},
            {'plaka': '21', 'il_adi': 'Diyarbakır'},
            {'plaka': '22', 'il_adi': 'Edirne'},
            {'plaka': '23', 'il_adi': 'Elazığ'},
            {'plaka': '24', 'il_adi': 'Erzincan'},
            {'plaka': '25', 'il_adi': 'Erzurum'},
            {'plaka': '26', 'il_adi': 'Eskişehir'},
            {'plaka': '27', 'il_adi': 'Gaziantep'},
            {'plaka': '28', 'il_adi': 'Giresun'},
            {'plaka': '29', 'il_adi': 'Gümüşhane'},
            {'plaka': '30', 'il_adi': 'Hakkari'},
            {'plaka': '31', 'il_adi': 'Hatay'},
            {'plaka': '32', 'il_adi': 'Isparta'},
            {'plaka': '33', 'il_adi': 'Mersin'},
            {'plaka': '34', 'il_adi': 'İstanbul'},
            {'plaka': '35', 'il_adi': 'İzmir'},
            {'plaka': '36', 'il_adi': 'Kars'},
            {'plaka': '37', 'il_adi': 'Kastamonu'},
            {'plaka': '38', 'il_adi': 'Kayseri'},
            {'plaka': '39', 'il_adi': 'Kırklareli'},
            {'plaka': '40', 'il_adi': 'Kırşehir'},
            {'plaka': '41', 'il_adi': 'Kocaeli'},
            {'plaka': '42', 'il_adi': 'Konya'},
            {'plaka': '43', 'il_adi': 'Kütahya'},
            {'plaka': '44', 'il_adi': 'Malatya'},
            {'plaka': '45', 'il_adi': 'Manisa'},
            {'plaka': '46', 'il_adi': 'Kahramanmaraş'},
            {'plaka': '47', 'il_adi': 'Mardin'},
            {'plaka': '48', 'il_adi': 'Muğla'},
            {'plaka': '49', 'il_adi': 'Muş'},
            {'plaka': '50', 'il_adi': 'Nevşehir'},
            {'plaka': '51', 'il_adi': 'Niğde'},
            {'plaka': '52', 'il_adi': 'Ordu'},
            {'plaka': '53', 'il_adi': 'Rize'},
            {'plaka': '54', 'il_adi': 'Sakarya'},
            {'plaka': '55', 'il_adi': 'Samsun'},
            {'plaka': '56', 'il_adi': 'Siirt'},
            {'plaka': '57', 'il_adi': 'Sinop'},
            {'plaka': '58', 'il_adi': 'Sivas'},
            {'plaka': '59', 'il_adi': 'Tekirdağ'},
            {'plaka': '60', 'il_adi': 'Tokat'},
            {'plaka': '61', 'il_adi': 'Trabzon'},
            {'plaka': '62', 'il_adi': 'Tunceli'},
            {'plaka': '63', 'il_adi': 'Şanlıurfa'},
            {'plaka': '64', 'il_adi': 'Uşak'},
            {'plaka': '65', 'il_adi': 'Van'},
            {'plaka': '66', 'il_adi': 'Yozgat'},
            {'plaka': '67', 'il_adi': 'Zonguldak'},
            {'plaka': '68', 'il_adi': 'Aksaray'},
            {'plaka': '69', 'il_adi': 'Bayburt'},
            {'plaka': '70', 'il_adi': 'Karaman'},
            {'plaka': '71', 'il_adi': 'Kırıkkale'},
            {'plaka': '72', 'il_adi': 'Batman'},
            {'plaka': '73', 'il_adi': 'Şırnak'},
            {'plaka': '74', 'il_adi': 'Bartın'},
            {'plaka': '75', 'il_adi': 'Ardahan'},
            {'plaka': '76', 'il_adi': 'Iğdır'},
            {'plaka': '77', 'il_adi': 'Yalova'},
            {'plaka': '78', 'il_adi': 'Karabük'},
            {'plaka': '79', 'il_adi': 'Kilis'},
            {'plaka': '80', 'il_adi': 'Osmaniye'},
            {'plaka': '81', 'il_adi': 'Düzce'}
        ]
        
        # Verileri oluştur
        for i, il_data in enumerate(iller):
            # Ana veri kaydı oluştur
            ana_veri = AnaVeri.objects.create()
            
            # Sütun değerlerini oluştur
            sutun_listesi = list(Sütun.objects.all().order_by('sıra'))
            
            # Gerçekçi cihaz sayıları oluştur (plaka sırasına göre)
            plaka_no = int(il_data['plaka'])
            
            # Kurulacak cihaz sayısı (plaka sırasına göre değişken)
            kurulacak_cihaz = 100 + (plaka_no * 5) + (i * 3)
            
            # Kurulan cihaz sayısı (kurulacak'tan biraz az)
            kurulan_cihaz = kurulacak_cihaz - (plaka_no % 10) - 5
            
            # Arızalı cihaz sayısı (kurulan'ın %5-15'i arası)
            arizali_oran = (plaka_no % 10 + 5) / 100
            arizali_cihaz = int(kurulan_cihaz * arizali_oran)
            
            degerler = [
                il_data['plaka'],
                il_data['il_adi'],
                str(kurulacak_cihaz),
                str(kurulan_cihaz),
                str(arizali_cihaz)
            ]
            
            for sutun, deger in zip(sutun_listesi, degerler):
                VeriDeger.objects.create(
                    ana_veri=ana_veri,
                    sutun=sutun,
                    deger=str(deger)
                )
            
            self.stdout.write(f'  ✅ {il_data["il_adi"]} ({il_data["plaka"]}) verisi oluşturuldu')
        
        self.stdout.write('✅ Tüm veriler başarıyla oluşturuldu!')
        self.stdout.write(f'📊 Toplam {len(iller)} il verisi eklendi.')
        self.stdout.write(f'🔢 Toplam {len(sutunlar)} sütun tanımlandı.')
        self.stdout.write('')
        self.stdout.write('📋 Yeni Sütun Yapısı:')
        self.stdout.write('   1. Plaka')
        self.stdout.write('   2. İl Adı')
        self.stdout.write('   3. Kurulacak Cihaz Sayısı')
        self.stdout.write('   4. Kurulan Cihaz Sayısı')
        self.stdout.write('   5. Arızalı Cihaz Sayısı')
        self.stdout.write('')
        self.stdout.write('🎯 Sıralama Özellikleri:')
        self.stdout.write('   - Plaka sırasına göre otomatik sıralama')
        self.stdout.write('   - Her sütunda bağımsız sıralama')
        self.stdout.write('   - Gerçekçi cihaz sayıları')
