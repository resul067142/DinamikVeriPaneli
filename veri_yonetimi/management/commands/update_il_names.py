from django.core.management.base import BaseCommand
from veri_yonetimi.models import AnaVeri, VeriDeger, Sütun

class Command(BaseCommand):
    help = 'Mevcut verilere il adları ekler'

    def handle(self, *args, **options):
        # İl adları listesi
        il_adi_listesi = [
            "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya", "Ankara", "Antalya", "Artvin", "Aydın", "Balıkesir",
            "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli",
            "Diyarbakır", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari",
            "Hatay", "Isparta", "Mersin", "İstanbul", "İzmir", "Kars", "Kastamonu", "Kayseri", "Kırklareli", "Kırşehir",
            "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Kahramanmaraş", "Mardin", "Muğla", "Muş", "Nevşehir",
            "Niğde", "Ordu", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Tekirdağ", "Tokat",
            "Trabzon", "Tunceli", "Şanlıurfa", "Uşak", "Van", "Yozgat", "Zonguldak", "Aksaray", "Bayburt", "Karaman",
            "Kırıkkale", "Batman", "Şırnak", "Bartın", "Ardahan", "Iğdır", "Yalova", "Karabük", "Kilis", "Osmaniye", "Düzce"
        ]
        
        # Mevcut verileri güncelle
        veriler = AnaVeri.objects.all()
        updated_count = 0
        
        for i, veri in enumerate(veriler):
            if i < len(il_adi_listesi):
                veri.il_adi = il_adi_listesi[i]
                veri.save()
                updated_count += 1
                self.stdout.write(f"Veri #{veri.id} -> {il_adi_listesi[i]}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Toplam {updated_count} veri güncellendi!')
        )
