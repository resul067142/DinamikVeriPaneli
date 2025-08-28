def app_settings(request):
    """
    Uygulama ayarlarını tüm template'lere ekle
    """
    from .models import AppSettings
    
    try:
        settings = AppSettings.get_settings()
        return settings
    except Exception:
        # Hata durumunda varsayılan değerleri döndür
        return {
            'app_name': 'DVP',
            'app_description': 'Dinamik Veri Paneli',
            'app_logo': None,
        }

def statistics_data(request):
    """
    Sağ sidebar istatistiklerini tüm template'lere ekle
    """
    # Login sayfasında istatistikleri gösterme
    if not request.user.is_authenticated:
        return {}
    
    from django.contrib.auth.models import User
    from django.utils import timezone
    from django.db.models import Sum
    from .models import AnaVeri, Sütun
    
    # Sistem İstatistikleri
    user_count = User.objects.count()
    sutun_count = Sütun.objects.filter(aktif=True).count()
    toplam_veri_count = AnaVeri.objects.count()
    bugun_eklenen = AnaVeri.objects.filter(olusturulma_tarihi__date=timezone.now().date()).count()
    
    # Türkiye geneli istatistikler
    try:
        turkiye_veriler = AnaVeri.objects.all()
        turkiye_toplam_kurulacak = turkiye_veriler.aggregate(toplam=Sum('kurulacak_cihaz_sayisi'))['toplam'] or 0
        turkiye_toplam_kurulan = turkiye_veriler.aggregate(toplam=Sum('kurulan_cihaz_sayisi'))['toplam'] or 0
        turkiye_toplam_arizali = turkiye_veriler.aggregate(toplam=Sum('arizali_cihaz_sayisi'))['toplam'] or 0
        
        if turkiye_toplam_kurulacak > 0:
            turkiye_tamamlanma_yuzdesi = round((turkiye_toplam_kurulan / turkiye_toplam_kurulacak) * 100, 1)
        else:
            turkiye_tamamlanma_yuzdesi = 0
    except Exception:
        turkiye_toplam_kurulacak = 0
        turkiye_toplam_kurulan = 0
        turkiye_toplam_arizali = 0
        turkiye_tamamlanma_yuzdesi = 0
    
    # İl bazında istatistikler (performans için limit koyuyoruz)
    try:
        il_bazinda_veriler = {}
        veriler = AnaVeri.objects.all()[:100]  # Performance sınırı
        
        for veri in veriler:
            il_adi = veri.il_adi or 'Belirtilmemiş'
            if il_adi not in il_bazinda_veriler:
                il_bazinda_veriler[il_adi] = {
                    'kurulacak': 0,
                    'kurulan': 0,
                    'arizali': 0
                }
            
            il_bazinda_veriler[il_adi]['kurulacak'] += veri.kurulacak_cihaz_sayisi or 0
            il_bazinda_veriler[il_adi]['kurulan'] += veri.kurulan_cihaz_sayisi or 0
            il_bazinda_veriler[il_adi]['arizali'] += veri.arizali_cihaz_sayisi or 0
        
        # İl dağılımı hesaplama
        toplam_il_sayisi = len(il_bazinda_veriler)
        mukemmel_il_sayisi = 0
        iyi_il_sayisi = 0
        orta_il_sayisi = 0
        kritik_il_sayisi = 0
        
        for il_data in il_bazinda_veriler.values():
            if il_data['kurulacak'] > 0:
                tamamlanma = (il_data['kurulan'] / il_data['kurulacak']) * 100
                if tamamlanma >= 90:
                    mukemmel_il_sayisi += 1
                elif tamamlanma >= 70:
                    iyi_il_sayisi += 1
                elif tamamlanma >= 50:
                    orta_il_sayisi += 1
                else:
                    kritik_il_sayisi += 1
            else:
                kritik_il_sayisi += 1
                
    except Exception:
        toplam_il_sayisi = 0
        mukemmel_il_sayisi = 0
        iyi_il_sayisi = 0
        orta_il_sayisi = 0
        kritik_il_sayisi = 0
    
    return {
        'user_count': user_count,
        'sutun_count': sutun_count,
        'toplam_veri_count': toplam_veri_count,
        'bugun_eklenen': bugun_eklenen,
        'turkiye_toplam_kurulacak': turkiye_toplam_kurulacak,
        'turkiye_toplam_kurulan': turkiye_toplam_kurulan,
        'turkiye_toplam_arizali': turkiye_toplam_arizali,
        'turkiye_tamamlanma_yuzdesi': turkiye_tamamlanma_yuzdesi,
        'toplam_il_sayisi': toplam_il_sayisi,
        'mukemmel_il_sayisi': mukemmel_il_sayisi,
        'iyi_il_sayisi': iyi_il_sayisi,
        'orta_il_sayisi': orta_il_sayisi,
        'kritik_il_sayisi': kritik_il_sayisi,
    }
