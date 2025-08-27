from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Q
from .models import AnaVeri, SutunAyarlari, Sütun, VeriDeger
from .forms import AnaVeriForm, SütunForm
from django.db.models import Case, When, Value, IntegerField, CharField
from django.contrib.auth.models import User, Group

@login_required
def ana_sayfa(request):
    """
    Ana sayfa - Dashboard
    """
    # Aktif sütunları al
    aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
    
    # Sütunları sıra numarasına göre sırala
    dinamik_sutunlar = aktif_sutunlar.filter(tip='dinamik').order_by('sıra')
    cihaz_sutunlar = aktif_sutunlar.filter(tip__in=['kurulacak', 'kurulan', 'arizali', 'tamamlanma']).order_by('sıra')

    # Verileri al (sadece önizleme için)
    veriler = AnaVeri.objects.all()

    # İl sorumlusu ise sadece kendi ilini göster
    if not request.user.is_superuser:
        # Kullanıcının hangi ilin sorumlusu olduğunu bul
        user_il = None
        if request.user.last_name:  # last_name'de plaka var
            user_plaka = request.user.last_name
            # Bu plakaya sahip veriyi bul
            for ana_veri in veriler:
                for deger in ana_veri.degerler.all():
                    if deger.sutun.ad == 'Plaka' and deger.deger == user_plaka:
                        user_il = ana_veri
                        break
                if user_il:
                    break

            if user_il:
                veriler = AnaVeri.objects.filter(id=user_il.id)

    # Türkiye geneli istatistikler
    turkiye_toplam_kurulacak = sum(veri.kurulacak_cihaz_sayisi for veri in AnaVeri.objects.all())
    turkiye_toplam_kurulan = sum(veri.kurulan_cihaz_sayisi for veri in AnaVeri.objects.all())
    turkiye_toplam_arizali = sum(veri.arizali_cihaz_sayisi for veri in AnaVeri.objects.all())
    turkiye_tamamlanma_yuzdesi = round((turkiye_toplam_kurulan / turkiye_toplam_kurulacak * 100), 1) if turkiye_toplam_kurulacak > 0 else 0
    
    # İl özelinde istatistikler
    il_istatistikleri = []
    for veri in veriler:
        il_istatistikleri.append({
            'veri': veri,
            'tamamlanma_yuzdesi': veri.tamamlanma_yuzdesi,
            'kalan_cihaz': veri.kalan_cihaz_sayisi,
            'durum_renk': veri.durum_renk
        })
    
    # En iyi ve en kötü performans gösteren iller
    tum_veriler = AnaVeri.objects.all()
    en_iyi_iller = sorted(tum_veriler, key=lambda x: x.tamamlanma_yuzdesi, reverse=True)[:5]
    en_kotu_iller = sorted(tum_veriler, key=lambda x: x.tamamlanma_yuzdesi)[:5]

    # İller özelinde detaylı istatistik veriler
    il_tamamlanma_verileri = []
    for veri in tum_veriler:
        if veri.kurulacak_cihaz_sayisi > 0:
            yuzde = round((veri.kurulan_cihaz_sayisi / veri.kurulacak_cihaz_sayisi * 100), 1)
            il_tamamlanma_verileri.append({
                'il': veri.il_adi,
                'yuzde': yuzde,
                'veri': veri
            })
    
    if il_tamamlanma_verileri:
        # En yüksek ve en düşük tamamlanma
        en_yuksek_tamamlanma = max(il_tamamlanma_verileri, key=lambda x: x['yuzde'])
        en_dusuk_tamamlanma = min(il_tamamlanma_verileri, key=lambda x: x['yuzde'])
        
        # Ortalama tamamlanma
        ortalama_tamamlanma = round(sum(x['yuzde'] for x in il_tamamlanma_verileri) / len(il_tamamlanma_verileri), 1)
        
        # Toplam il sayısı
        toplam_il_sayisi = len(il_tamamlanma_verileri)
        
        # Performans kategorileri
        mukemmel_il_sayisi = len([x for x in il_tamamlanma_verileri if x['yuzde'] >= 80])
        iyi_il_sayisi = len([x for x in il_tamamlanma_verileri if 60 <= x['yuzde'] < 80])
        orta_il_sayisi = len([x for x in il_tamamlanma_verileri if 40 <= x['yuzde'] < 60])
        kritik_il_sayisi = len([x for x in il_tamamlanma_verileri if x['yuzde'] < 40])
        
        # Bölgesel ortalamalar
        marmara_illeri = ['İstanbul', 'Bursa', 'Kocaeli', 'Sakarya', 'Balıkesir', 'Çanakkale', 'Edirne', 'Tekirdağ', 'Yalova', 'Kırklareli']
        ege_illeri = ['İzmir', 'Manisa', 'Aydın', 'Muğla', 'Denizli', 'Afyonkarahisar', 'Kütahya', 'Uşak']
        akdeniz_illeri = ['Antalya', 'Adana', 'Mersin', 'Hatay', 'Kahramanmaraş', 'Osmaniye', 'Isparta', 'Burdur']
        ic_anadolu_illeri = ['Ankara', 'Konya', 'Kayseri', 'Sivas', 'Yozgat', 'Kırıkkale', 'Aksaray', 'Niğde', 'Nevşehir', 'Kırşehir', 'Çankırı', 'Karaman']
        
        marmara_ortalamasi = round(sum(x['yuzde'] for x in il_tamamlanma_verileri if x['il'] in marmara_illeri) / max(len([x for x in il_tamamlanma_verileri if x['il'] in marmara_illeri]), 1), 1)
        ege_ortalamasi = round(sum(x['yuzde'] for x in il_tamamlanma_verileri if x['il'] in ege_illeri) / max(len([x for x in il_tamamlanma_verileri if x['il'] in ege_illeri]), 1), 1)
        akdeniz_ortalamasi = round(sum(x['yuzde'] for x in il_tamamlanma_verileri if x['il'] in akdeniz_illeri) / max(len([x for x in il_tamamlanma_verileri if x['il'] in akdeniz_illeri]), 1), 1)
        ic_anadolu_ortalamasi = round(sum(x['yuzde'] for x in il_tamamlanma_verileri if x['il'] in ic_anadolu_illeri) / max(len([x for x in il_tamamlanma_verileri if x['il'] in ic_anadolu_illeri]), 1), 1)
    else:
        en_yuksek_tamamlanma = {'yuzde': 0, 'il': '-'}
        en_dusuk_tamamlanma = {'yuzde': 0, 'il': '-'}
        ortalama_tamamlanma = 0
        toplam_il_sayisi = 0
        mukemmel_il_sayisi = 0
        iyi_il_sayisi = 0
        orta_il_sayisi = 0
        kritik_il_sayisi = 0
        marmara_ortalamasi = 0
        ege_ortalamasi = 0
        akdeniz_ortalamasi = 0
        ic_anadolu_ortalamasi = 0

    # Sağ sidebar için ek veriler
    son_veriler = AnaVeri.objects.order_by('-olusturulma_tarihi')[:5]
    user_count = User.objects.count()

    context = {
        'veriler': veriler,
        'aktif_sutunlar': aktif_sutunlar,
        'dinamik_sutunlar': dinamik_sutunlar,
        'cihaz_sutunlar': cihaz_sutunlar,
        'son_veriler': son_veriler,
        'user_count': user_count,
        'turkiye_toplam_kurulacak': turkiye_toplam_kurulacak,
        'turkiye_toplam_kurulan': turkiye_toplam_kurulan,
        'turkiye_toplam_arizali': turkiye_toplam_arizali,
        'turkiye_tamamlanma_yuzdesi': turkiye_tamamlanma_yuzdesi,
        'il_istatistikleri': il_istatistikleri,
        'en_iyi_iller': en_iyi_iller,
        'en_kotu_iller': en_kotu_iller,
        'en_yuksek_tamamlanma': en_yuksek_tamamlanma,
        'en_dusuk_tamamlanma': en_dusuk_tamamlanma,
        'ortalama_tamamlanma': ortalama_tamamlanma,
        'toplam_il_sayisi': toplam_il_sayisi,
        'mukemmel_il_sayisi': mukemmel_il_sayisi,
        'iyi_il_sayisi': iyi_il_sayisi,
        'orta_il_sayisi': orta_il_sayisi,
        'kritik_il_sayisi': kritik_il_sayisi,
        'marmara_ortalamasi': marmara_ortalamasi,
        'ege_ortalamasi': ege_ortalamasi,
        'akdeniz_ortalamasi': akdeniz_ortalamasi,
        'ic_anadolu_ortalamasi': ic_anadolu_ortalamasi,
    }
    return render(request, 'veri_yonetimi/ana_sayfa.html', context)

@login_required
def veri_listesi(request):
    """
    Ana veri tablosunu listele
    """
    # Filtreleme parametreleri
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'olusturulma_tarihi')
    sort_order = request.GET.get('order', 'desc')
    
    # Sütun bazında filtreleme
    sutun_filtreleri = {}
    aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
    
    # Sütunları sıra numarasına göre sırala
    dinamik_sutunlar = aktif_sutunlar.filter(tip='dinamik').order_by('sıra')
    cihaz_sutunlar = aktif_sutunlar.filter(tip__in=['kurulacak', 'kurulan', 'arizali', 'tamamlanma']).order_by('sıra')
    
    for sutun in dinamik_sutunlar:
        filter_value = request.GET.get(f'filter_{sutun.id}', '')
        if filter_value:
            sutun_filtreleri[sutun.id] = filter_value
    
    # Verileri al
    veriler = AnaVeri.objects.all()
    
    # İl sorumlusu ise sadece kendi ilini göster
    if not request.user.is_superuser:
        # Kullanıcının hangi ilin sorumlusu olduğunu bul
        user_il = None
        if request.user.last_name:  # last_name'de plaka var
            user_plaka = request.user.last_name
            # Bu plakaya sahip veriyi bul
            for ana_veri in veriler:
                for deger in ana_veri.degerler.all():
                    if deger.sutun.ad == 'Plaka' and deger.deger == user_plaka:
                        user_il = ana_veri
                        break
                if user_il:
                    break
            
            if user_il:
                veriler = AnaVeri.objects.filter(id=user_il.id)
                # İl sorumlusuna bilgi mesajı göster
                from django.contrib import messages
                messages.info(request, f'Sadece {request.user.first_name} için veriler gösteriliyor.')
    
    # Genel arama filtresi
    if search_query:
        veriler = veriler.filter(
            Q(degerler__deger__icontains=search_query) |
            Q(id__icontains=search_query)
        ).distinct()
    
    # Sütun bazında filtreleme
    for sutun_id, filter_value in sutun_filtreleri.items():
        veriler = veriler.filter(
            degerler__sutun_id=sutun_id,
            degerler__deger__icontains=filter_value
        ).distinct()
    
    # Sıralama
    if sort_by == 'olusturulma_tarihi':
        if sort_order == 'desc':
            veriler = veriler.order_by('-olusturulma_tarihi')
        else:
            veriler = veriler.order_by('olusturulma_tarihi')
    elif sort_by == 'id':
        if sort_order == 'desc':
            veriler = veriler.order_by('-id')
        else:
            veriler = veriler.order_by('id')
    elif sort_by.startswith('sutun_'):
        # Sütun bazında sıralama
        sutun_id = sort_by.replace('sutun_', '')
        
        # Sütun değerlerini al ve sırala
        if sort_order == 'desc':
            # Azalan sıralama için önce boş değerler, sonra dolu değerler
            veriler = veriler.annotate(
                sutun_deger=Case(
                    When(degerler__sutun_id=sutun_id, then='degerler__deger'),
                    default=Value(''),
                    output_field=CharField(),
                )
            ).order_by('sutun_deger', '-olusturulma_tarihi')
        else:
            # Artan sıralama için önce dolu değerler, sonra boş değerler
            veriler = veriler.annotate(
                sutun_deger=Case(
                    When(degerler__sutun_id=sutun_id, then='degerler__deger'),
                    default=Value(''),
                    output_field=CharField(),
                )
            ).order_by('sutun_deger', 'olusturulma_tarihi')
    else:
        # Varsayılan sıralama: Plaka sırasına göre
        veriler = veriler.annotate(
            plaka_deger=Case(
                When(degerler__sutun__ad='Plaka', then='degerler__deger'),
                default=Value(''),
                output_field=CharField(),
            )
        ).order_by('plaka_deger')
    
    # Eğer hiç sütun yoksa varsayılan sütunları oluştur
    if not aktif_sutunlar.exists():
        varsayilan_sutunlar = [
            {'ad': 'Plaka', 'sıra': 1},
            {'ad': 'İl Adı', 'sıra': 2},
            {'ad': 'Kurulacak Cihaz Sayısı', 'sıra': 3},
            {'ad': 'Kurulan Cihaz Sayısı', 'sıra': 4},
            {'ad': 'Arızalı Cihaz Sayısı', 'sıra': 5},
        ]
        for sutun_data in varsayilan_sutunlar:
            Sütun.objects.create(**sutun_data)
        aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
    
    # Türkiye geneli istatistikler
    turkiye_toplam_kurulacak = sum(veri.kurulacak_cihaz_sayisi for veri in AnaVeri.objects.all())
    turkiye_toplam_kurulan = sum(veri.kurulan_cihaz_sayisi for veri in AnaVeri.objects.all())
    turkiye_toplam_arizali = sum(veri.arizali_cihaz_sayisi for veri in AnaVeri.objects.all())
    turkiye_tamamlanma_yuzdesi = round((turkiye_toplam_kurulan / turkiye_toplam_kurulacak * 100), 1) if turkiye_toplam_kurulacak > 0 else 0
    
    # İller özelinde istatistik veriler
    from django.db.models import Avg, Count, Q
    
    # Tüm illerin tamamlanma yüzdeleri
    il_tamamlanma_verileri = []
    for veri in AnaVeri.objects.all():
        if veri.kurulacak_cihaz_sayisi > 0:
            yuzde = round((veri.kurulan_cihaz_sayisi / veri.kurulacak_cihaz_sayisi * 100), 1)
            il_tamamlanma_verileri.append({
                'il': veri.il_adi,
                'yuzde': yuzde,
                'veri': veri
            })
    
    if il_tamamlanma_verileri:
        # En yüksek ve en düşük tamamlanma
        en_yuksek_tamamlanma = max(il_tamamlanma_verileri, key=lambda x: x['yuzde'])
        en_dusuk_tamamlanma = min(il_tamamlanma_verileri, key=lambda x: x['yuzde'])
        
        # Ortalama tamamlanma
        ortalama_tamamlanma = round(sum(x['yuzde'] for x in il_tamamlanma_verileri) / len(il_tamamlanma_verileri), 1)
        
        # Toplam il sayısı
        toplam_il_sayisi = len(il_tamamlanma_verileri)
        
        # Performans kategorileri
        mukemmel_il_sayisi = len([x for x in il_tamamlanma_verileri if x['yuzde'] >= 80])
        iyi_il_sayisi = len([x for x in il_tamamlanma_verileri if 60 <= x['yuzde'] < 80])
        orta_il_sayisi = len([x for x in il_tamamlanma_verileri if 40 <= x['yuzde'] < 60])
        kritik_il_sayisi = len([x for x in il_tamamlanma_verileri if x['yuzde'] < 40])
        
        # Bölgesel ortalamalar (basit hesaplama)
        marmara_illeri = ['İstanbul', 'Bursa', 'Kocaeli', 'Sakarya', 'Balıkesir', 'Çanakkale', 'Edirne', 'Tekirdağ', 'Yalova', 'Kırklareli']
        ege_illeri = ['İzmir', 'Manisa', 'Aydın', 'Muğla', 'Denizli', 'Afyonkarahisar', 'Kütahya', 'Uşak']
        akdeniz_illeri = ['Antalya', 'Adana', 'Mersin', 'Hatay', 'Kahramanmaraş', 'Osmaniye', 'Isparta', 'Burdur']
        ic_anadolu_illeri = ['Ankara', 'Konya', 'Kayseri', 'Sivas', 'Yozgat', 'Kırıkkale', 'Aksaray', 'Niğde', 'Nevşehir', 'Kırşehir', 'Çankırı', 'Karaman']
        
        marmara_ortalamasi = round(sum(x['yuzde'] for x in il_tamamlanma_verileri if x['il'] in marmara_illeri) / max(len([x for x in il_tamamlanma_verileri if x['il'] in marmara_illeri]), 1), 1)
        ege_ortalamasi = round(sum(x['yuzde'] for x in il_tamamlanma_verileri if x['il'] in ege_illeri) / max(len([x for x in il_tamamlanma_verileri if x['il'] in ege_illeri]), 1), 1)
        akdeniz_ortalamasi = round(sum(x['yuzde'] for x in il_tamamlanma_verileri if x['il'] in akdeniz_illeri) / max(len([x for x in il_tamamlanma_verileri if x['il'] in akdeniz_illeri]), 1), 1)
        ic_anadolu_ortalamasi = round(sum(x['yuzde'] for x in il_tamamlanma_verileri if x['il'] in ic_anadolu_illeri) / max(len([x for x in il_tamamlanma_verileri if x['il'] in ic_anadolu_illeri]), 1), 1)
    else:
        en_yuksek_tamamlanma = {'yuzde': 0, 'il': '-'}
        en_dusuk_tamamlanma = {'yuzde': 0, 'il': '-'}
        ortalama_tamamlanma = 0
        toplam_il_sayisi = 0
        mukemmel_il_sayisi = 0
        iyi_il_sayisi = 0
        orta_il_sayisi = 0
        kritik_il_sayisi = 0
        marmara_ortalamasi = 0
        ege_ortalamasi = 0
        akdeniz_ortalamasi = 0
        ic_anadolu_ortalamasi = 0
    
    # Sağ sidebar için ek veriler
    son_veriler = AnaVeri.objects.order_by('-olusturulma_tarihi')[:5]
    user_count = User.objects.count()
    
    context = {
        'veriler': veriler,
        'aktif_sutunlar': aktif_sutunlar,
        'dinamik_sutunlar': dinamik_sutunlar,
        'cihaz_sutunlar': cihaz_sutunlar,
        'search_query': search_query,
        'sort_by': sort_by.replace('-', '') if sort_by.startswith('-') else sort_by,
        'sort_order': 'desc' if sort_by.startswith('-') else 'asc',
        'sutun_filtreleri': sutun_filtreleri,
        'is_il_sorumlusu': not request.user.is_superuser,
        'son_veriler': son_veriler,
        'user_count': user_count,
        'turkiye_toplam_kurulacak': turkiye_toplam_kurulacak,
        'turkiye_toplam_kurulan': turkiye_toplam_kurulan,
        'turkiye_toplam_arizali': turkiye_toplam_arizali,
        'turkiye_tamamlanma_yuzdesi': turkiye_tamamlanma_yuzdesi,
        'en_yuksek_tamamlanma': en_yuksek_tamamlanma,
        'en_dusuk_tamamlanma': en_dusuk_tamamlanma,
        'ortalama_tamamlanma': ortalama_tamamlanma,
        'toplam_il_sayisi': toplam_il_sayisi,
        'mukemmel_il_sayisi': mukemmel_il_sayisi,
        'iyi_il_sayisi': iyi_il_sayisi,
        'orta_il_sayisi': orta_il_sayisi,
        'kritik_il_sayisi': kritik_il_sayisi,
        'marmara_ortalamasi': marmara_ortalamasi,
        'ege_ortalamasi': ege_ortalamasi,
        'akdeniz_ortalamasi': akdeniz_ortalamasi,
        'ic_anadolu_ortalamasi': ic_anadolu_ortalamasi,
    }
    return render(request, 'veri_yonetimi/veri_listesi.html', context)

@login_required
def veri_ekle(request):
    """
    Yeni veri ekle
    """
    # Sadece süper kullanıcılar veri ekleyebilir
    if not request.user.is_superuser:
        from django.contrib import messages
        messages.error(request, 'Sadece admin kullanıcılar yeni veri ekleyebilir.')
        return redirect('veri_yonetimi:veri_listesi')
    
    if request.method == 'POST':
        form = AnaVeriForm(request.POST)
        if form.is_valid():
            ana_veri = form.save()
            messages.success(request, 'Veri başarıyla eklendi!')
            return redirect('veri_yonetimi:veri_listesi')
    else:
        form = AnaVeriForm()
    
    # Aktif sütunları al
    aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
    
    # Sağ sidebar için ek veriler
    son_veriler = AnaVeri.objects.order_by('-olusturulma_tarihi')[:5]
    user_count = User.objects.count()
    
    context = {
        'form': form,
        'veri': None,  # Yeni veri için None
        'aktif_sutunlar': aktif_sutunlar,
        'is_edit': False,
        'son_veriler': son_veriler,
        'user_count': user_count,
    }
    return render(request, 'veri_yonetimi/veri_formu.html', context)

@login_required
def veri_guncelle(request, pk):
    """
    Veri güncelle
    """
    # Sadece süper kullanıcılar veri güncelleyebilir
    if not request.user.is_superuser:
        messages.error(request, 'Sadece admin kullanıcılar veri güncelleyebilir.')
        return redirect('veri_yonetimi:veri_listesi')
    
    ana_veri = get_object_or_404(AnaVeri, pk=pk)
    
    if request.method == 'POST':
        form = AnaVeriForm(request.POST, instance=ana_veri)
        if form.is_valid():
            ana_veri = form.save()
            messages.success(request, 'Veri başarıyla güncellendi!')
            return redirect('veri_yonetimi:veri_listesi')
    else:
        form = AnaVeriForm(instance=ana_veri)
    
    # Aktif sütunları al
    aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
    
    # Sağ sidebar için ek veriler
    son_veriler = AnaVeri.objects.order_by('-olusturulma_tarihi')[:5]
    user_count = User.objects.count()
    
    context = {
        'form': form,
        'veri': ana_veri,  # Template'de 'veri' olarak kullanılıyor
        'ana_veri': ana_veri,
        'aktif_sutunlar': aktif_sutunlar,
        'is_edit': True,
        'son_veriler': son_veriler,
        'user_count': user_count,
    }
    return render(request, 'veri_yonetimi/veri_formu.html', context)

@login_required
def veri_sil(request, pk):
    """
    Veri silme onay sayfası
    """
    # Sadece süper kullanıcılar veri silebilir
    if not request.user.is_superuser:
        messages.error(request, 'Sadece admin kullanıcılar veri silebilir.')
        return redirect('veri_yonetimi:veri_listesi')
    
    ana_veri = get_object_or_404(AnaVeri, pk=pk)
    
    # Aktif sütunları al
    aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
    
    context = {
        'ana_veri': ana_veri,
        'aktif_sutunlar': aktif_sutunlar,
    }
    return render(request, 'veri_yonetimi/veri_sil.html', context)

@login_required
def veri_sil_onay(request, pk):
    """
    AJAX ile veri silme onayı
    """
    if request.method == 'POST':
        veri = get_object_or_404(AnaVeri, pk=pk)
        veri.delete()
        return JsonResponse({'success': True, 'message': 'Veri başarıyla silindi!'})
    
    return JsonResponse({'success': False, 'message': 'Geçersiz istek!'})

# Sütun yönetimi view'ları
@login_required
def sutun_listesi(request):
    """
    Sütun listesi
    """
    sutunlar = Sütun.objects.all().order_by('sıra')
    
    # Site başlığını session'dan al
    site_title = request.session.get('site_title', 'Dinamik Veri Paneli')
    app_name = request.session.get('app_name', 'Dinamik Veri Paneli')
    app_description = request.session.get('app_description', 'Bu uygulama, veri yönetimi ve raporlama için tasarlanmıştır.')
    
    # Sağ sidebar için ek veriler
    son_veriler = AnaVeri.objects.order_by('-olusturulma_tarihi')[:5]
    user_count = User.objects.count()
    aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
    
    context = {
        'sutunlar': sutunlar,
        'site_title': site_title,
        'app_name': app_name,
        'app_description': app_description,
        'son_veriler': son_veriler,
        'user_count': user_count,
        'aktif_sutunlar': aktif_sutunlar,
    }
    return render(request, 'veri_yonetimi/sutun_listesi.html', context)

@login_required
def sutun_ekle(request):
    """
    Yeni sütun ekle
    """
    if request.method == 'POST':
        form = SütunForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sütun başarıyla eklendi!')
            return redirect('veri_yonetimi:sutun_listesi')
        else:
            messages.error(request, 'Form hataları var. Lütfen kontrol edin.')
    else:
        form = SütunForm()
    
    # Sağ sidebar için ek veriler
    son_veriler = AnaVeri.objects.order_by('-olusturulma_tarihi')[:5]
    user_count = User.objects.count()
    aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
    
    context = {
        'form': form,
        'is_edit': False,
        'son_veriler': son_veriler,
        'user_count': user_count,
        'aktif_sutunlar': aktif_sutunlar,
    }
    return render(request, 'veri_yonetimi/sutun_formu.html', context)

@login_required
def sutun_guncelle(request, pk):
    """
    Sütun güncelle
    """
    sutun = get_object_or_404(Sütun, pk=pk)
    
    if request.method == 'POST':
        form = SütunForm(request.POST, instance=sutun)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sütun başarıyla güncellendi!')
            return redirect('veri_yonetimi:sutun_listesi')
        else:
            messages.error(request, 'Form hataları var. Lütfen kontrol edin.')
    else:
        form = SütunForm(instance=sutun)
    
    # Sağ sidebar için ek veriler
    son_veriler = AnaVeri.objects.order_by('-olusturulma_tarihi')[:5]
    user_count = User.objects.count()
    aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
    
    context = {
        'form': form,
        'sutun': sutun,
        'is_edit': True,
        'son_veriler': son_veriler,
        'user_count': user_count,
        'aktif_sutunlar': aktif_sutunlar,
    }
    return render(request, 'veri_yonetimi/sutun_formu.html', context)

@login_required
def sutun_sil(request, pk):
    """
    Sütun sil
    """
    sutun = get_object_or_404(Sütun, pk=pk)
    
    if request.method == 'POST':
        # Sütun silinmeden önce veri sayısını kontrol et
        veri_sayisi = sutun.verideger_set.count()
        if veri_sayisi > 0:
            messages.error(request, f'Bu sütunda {veri_sayisi} veri bulunuyor. Önce verileri silmelisiniz.')
            return redirect('veri_yonetimi:sutun_listesi')
        
        sutun.delete()
        messages.success(request, 'Sütun başarıyla silindi!')
        return redirect('veri_yonetimi:sutun_listesi')
    
    # Sağ sidebar için ek veriler
    son_veriler = AnaVeri.objects.order_by('-olusturulma_tarihi')[:5]
    user_count = User.objects.count()
    aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
    
    context = {
        'sutun': sutun,
        'son_veriler': son_veriler,
        'user_count': user_count,
        'aktif_sutunlar': aktif_sutunlar,
    }
    return render(request, 'veri_yonetimi/sutun_sil.html', context)

@login_required
def update_site_title(request):
    """
    Site başlığını güncelle
    """
    if request.method == 'POST':
        site_title = request.POST.get('site_title', '').strip()
        
        if site_title:
            # Site başlığını session'a kaydet (gerçek uygulamada veritabanına kaydedilir)
            request.session['site_title'] = site_title
            messages.success(request, f'Site başlığı başarıyla güncellendi: {site_title}')
        else:
            messages.error(request, 'Site başlığı boş olamaz!')
    
    return redirect('veri_yonetimi:sutun_listesi')

@login_required
def update_app_settings(request):
    """
    Uygulama ayarlarını güncelle
    """
    if request.method == 'POST':
        app_name = request.POST.get('app_name', '').strip()
        app_description = request.POST.get('app_description', '').strip()
        
        if app_name:
            # Uygulama ayarlarını session'a kaydet
            request.session['app_name'] = app_name
            request.session['app_description'] = app_description
            messages.success(request, f'Uygulama ayarları başarıyla güncellendi: {app_name}')
        else:
            messages.error(request, 'Uygulama adı boş olamaz!')
    
    return redirect('veri_yonetimi:sutun_listesi')

@login_required
def kullanici_listesi(request):
    """
    Kullanıcı listesini göster (sadece admin)
    """
    # Sadece süper kullanıcılar kullanıcı listesini görebilir
    if not request.user.is_superuser:
        from django.contrib import messages
        messages.error(request, 'Sadece admin kullanıcılar kullanıcı listesini görebilir.')
        return redirect('veri_yonetimi:veri_listesi')
    
    # Tüm kullanıcıları al
    kullanicilar = User.objects.all().order_by('username')
    
    # İl sorumlusu grubunu al
    try:
        il_sorumlusu_group = Group.objects.get(name='İl Sorumlusu')
    except Group.DoesNotExist:
        il_sorumlusu_group = None
    
    # Sağ sidebar için ek veriler
    son_veriler = AnaVeri.objects.order_by('-olusturulma_tarihi')[:5]
    user_count = User.objects.count()
    aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
    
    # İstatistikler
    admin_count = User.objects.filter(is_superuser=True).count()
    active_count = User.objects.filter(is_active=True).count()
    il_sorumlusu_count = User.objects.filter(is_staff=True, is_superuser=False).count()
    
    context = {
        'kullanicilar': kullanicilar,
        'il_sorumlusu_group': il_sorumlusu_group,
        'son_veriler': son_veriler,
        'user_count': user_count,
        'aktif_sutunlar': aktif_sutunlar,
        'admin_count': admin_count,
        'active_count': active_count,
        'il_sorumlusu_count': il_sorumlusu_count,
    }
    return render(request, 'veri_yonetimi/kullanici_listesi.html', context)

@login_required
def kullanici_ekle(request):
    """
    Yeni kullanıcı ekle
    """
    # Sadece süper kullanıcılar kullanıcı ekleyebilir
    if not request.user.is_superuser:
        messages.error(request, 'Sadece admin kullanıcılar yeni kullanıcı ekleyebilir.')
        return redirect('veri_yonetimi:kullanici_listesi')
    
    if request.method == 'POST':
        # Form verilerini al
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        tc_kimlik = request.POST.get('tc_kimlik')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        is_superuser = request.POST.get('is_superuser') == 'on'
        is_staff = request.POST.get('is_staff') == 'on'
        
        # Validasyon
        if not username or not password1 or not password2:
            messages.error(request, 'Kullanıcı adı ve şifre zorunludur.')
            return redirect('veri_yonetimi:kullanici_ekle')
        
        if password1 != password2:
            messages.error(request, 'Şifreler eşleşmiyor.')
            return redirect('veri_yonetimi:kullanici_ekle')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Bu kullanıcı adı zaten kullanılıyor.')
            return redirect('veri_yonetimi:kullanici_ekle')
        
        if tc_kimlik and UserProfile.objects.filter(tc_kimlik=tc_kimlik).exists():
            messages.error(request, 'Bu TC kimlik numarası zaten kullanılıyor.')
            return redirect('veri_yonetimi:kullanici_ekle')
        
        try:
            # Kullanıcıyı oluştur
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                is_superuser=is_superuser,
                is_staff=is_staff
            )
            
            # TC kimlik numarasını ekle (UserProfile ile)
            if tc_kimlik:
                UserProfile.objects.create(user=user, tc_kimlik=tc_kimlik)
            
            messages.success(request, f'"{username}" kullanıcısı başarıyla oluşturuldu!')
            return redirect('veri_yonetimi:kullanici_listesi')
            
        except Exception as e:
            messages.error(request, f'Kullanıcı oluşturulurken hata oluştu: {str(e)}')
            return redirect('veri_yonetimi:kullanici_ekle')
    
    # Sağ sidebar için ek veriler
    son_veriler = AnaVeri.objects.order_by('-olusturulma_tarihi')[:5]
    user_count = User.objects.count()
    aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
    
    context = {
        'son_veriler': son_veriler,
        'user_count': user_count,
        'aktif_sutunlar': aktif_sutunlar,
    }
    return render(request, 'veri_yonetimi/kullanici_formu.html', context)

@login_required
def kullanici_guncelle(request, pk):
    """
    Kullanıcı güncelle
    """
    # Sadece süper kullanıcılar kullanıcı güncelleyebilir
    if not request.user.is_superuser:
        messages.error(request, 'Sadece admin kullanıcılar kullanıcı güncelleyebilir.')
        return redirect('veri_yonetimi:kullanici_listesi')
    
    kullanici = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        # Form verilerini al
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        tc_kimlik = request.POST.get('tc_kimlik')
        is_superuser = request.POST.get('is_superuser') == 'on'
        is_staff = request.POST.get('is_staff') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        # TC kimlik benzersizlik kontrolü
        current_tc = getattr(kullanici.profile, 'tc_kimlik', None) if hasattr(kullanici, 'profile') else None
        if tc_kimlik and tc_kimlik != current_tc:
            if UserProfile.objects.filter(tc_kimlik=tc_kimlik).exclude(user=kullanici).exists():
                messages.error(request, 'Bu TC kimlik numarası başka bir kullanıcı tarafından kullanılıyor.')
                return redirect('veri_yonetimi:kullanici_guncelle', pk=pk)
        
        try:
            # Kullanıcıyı güncelle
            kullanici.email = email
            kullanici.first_name = first_name
            kullanici.last_name = last_name
            kullanici.is_superuser = is_superuser
            kullanici.is_staff = is_staff
            kullanici.is_active = is_active
            kullanici.save()
            
            # TC kimlik numarasını güncelle (UserProfile ile)
            if hasattr(kullanici, 'profile'):
                kullanici.profile.tc_kimlik = tc_kimlik
                kullanici.profile.save()
            elif tc_kimlik:
                UserProfile.objects.create(user=kullanici, tc_kimlik=tc_kimlik)
            
            messages.success(request, f'"{kullanici.username}" kullanıcısı başarıyla güncellendi!')
            return redirect('veri_yonetimi:kullanici_listesi')
            
        except Exception as e:
            messages.error(request, f'Kullanıcı güncellenirken hata oluştu: {str(e)}')
            return redirect('veri_yonetimi:kullanici_guncelle', pk=pk)
    
    # Sağ sidebar için ek veriler
    son_veriler = AnaVeri.objects.order_by('-olusturulma_tarihi')[:5]
    user_count = User.objects.count()
    aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
    
    context = {
        'kullanici': kullanici,
        'son_veriler': son_veriler,
        'user_count': user_count,
        'aktif_sutunlar': aktif_sutunlar,
    }
    return render(request, 'veri_yonetimi/kullanici_formu.html', context)

@login_required
def generate_fake_tc(request):
    """
    Tüm kullanıcılar için fake TC kimlik numaraları üret
    """
    # Sadece süper kullanıcılar fake TC üretebilir
    if not request.user.is_superuser:
        messages.error(request, 'Sadece admin kullanıcılar fake TC kimlik numaraları üretebilir.')
        return redirect('veri_yonetimi:kullanici_listesi')
    
    if request.method == 'POST':
        try:
            from .models import UserProfile
            import random
            
            # Mevcut kullanıcıları al
            users = User.objects.all()
            created_count = 0
            updated_count = 0
            
            for user in users:
                # Fake TC kimlik numarası oluştur
                fake_tc = generate_valid_tc()
                
                # UserProfile oluştur veya güncelle
                if hasattr(user, 'profile'):
                    user.profile.tc_kimlik = fake_tc
                    user.profile.save()
                    updated_count += 1
                else:
                    UserProfile.objects.create(user=user, tc_kimlik=fake_tc)
                    created_count += 1
            
            messages.success(request, f'🎲 {created_count} yeni, {updated_count} güncellenmiş fake TC kimlik numarası oluşturuldu!')
            
        except Exception as e:
            messages.error(request, f'Fake TC kimlik numaraları oluşturulurken hata oluştu: {str(e)}')
    
    return redirect('veri_yonetimi:kullanici_listesi')

def generate_valid_tc():
    """
    Geçerli fake TC kimlik numarası oluştur
    """
    from .models import UserProfile
    import random
    
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

@login_required
def cihaz_turleri(request):
    """
    Cihaz türleri sayfasını göster
    """
    # Cihaz türleri verileri
    cihaz_turleri_data = [
        {
            'id': 1,
            'ad': 'Sürücü Analiz Kamerası',
            'aciklama': 'Sürücü davranışlarını analiz eden kamera sistemi',
            'kategori': 'Güvenlik',
            'durum': 'Aktif',
            'kurulum_sayisi': 1250,
            'hedef_sayisi': 2000,
            'tamamlanma_yuzdesi': 62.5,
            'icon': '📹',
            'renk': 'blue'
        },
        {
            'id': 2,
            'ad': 'ATS Araç Takip Sistemi',
            'aciklama': 'Araç konum ve durum takip sistemi',
            'kategori': 'Takip',
            'durum': 'Aktif',
            'kurulum_sayisi': 980,
            'hedef_sayisi': 1500,
            'tamamlanma_yuzdesi': 65.3,
            'icon': '🚗',
            'renk': 'green'
        },
        {
            'id': 3,
            'ad': 'GPS Konum Takip',
            'aciklama': 'Hassas konum belirleme ve rota takibi',
            'kategori': 'Navigasyon',
            'durum': 'Aktif',
            'kurulum_sayisi': 2100,
            'hedef_sayisi': 2500,
            'tamamlanma_yuzdesi': 84.0,
            'icon': '📍',
            'renk': 'purple'
        },
        {
            'id': 4,
            'ad': 'Yakıt Takip Sistemi',
            'aciklama': 'Yakıt tüketimi ve maliyet takibi',
            'kategori': 'Maliyet',
            'durum': 'Aktif',
            'kurulum_sayisi': 750,
            'hedef_sayisi': 1200,
            'tamamlanma_yuzdesi': 62.5,
            'icon': '⛽',
            'renk': 'orange'
        },
        {
            'id': 5,
            'ad': 'Motor Performans Monitörü',
            'aciklama': 'Motor sağlığı ve performans takibi',
            'kategori': 'Teknik',
            'durum': 'Aktif',
            'kurulum_sayisi': 680,
            'hedef_sayisi': 1000,
            'tamamlanma_yuzdesi': 68.0,
            'icon': '⚙️',
            'renk': 'red'
        },
        {
            'id': 6,
            'ad': 'Hız ve Mesafe Sensörü',
            'aciklama': 'Hız limiti ve güvenlik uyarıları',
            'kategori': 'Güvenlik',
            'durum': 'Aktif',
            'kurulum_sayisi': 890,
            'hedef_sayisi': 1300,
            'tamamlanma_yuzdesi': 68.5,
            'icon': '🏃',
            'renk': 'indigo'
        }
    ]
    
    # İstatistikler
    toplam_cihaz = sum(cihaz['kurulum_sayisi'] for cihaz in cihaz_turleri_data)
    toplam_hedef = sum(cihaz['hedef_sayisi'] for cihaz in cihaz_turleri_data)
    genel_tamamlanma = round((toplam_cihaz / toplam_hedef * 100), 1) if toplam_hedef > 0 else 0
    
    # En popüler cihaz
    en_populer = max(cihaz_turleri_data, key=lambda x: x['tamamlanma_yuzdesi'])
    
    context = {
        'cihaz_turleri': cihaz_turleri_data,
        'toplam_cihaz': toplam_cihaz,
        'toplam_hedef': toplam_hedef,
        'genel_tamamlanma': genel_tamamlanma,
        'en_populer': en_populer,
    }
    
    return render(request, 'veri_yonetimi/cihaz_turleri.html', context)


@login_required
def illere_gore_cihaz_turleri(request):
    """
    İllere göre cihaz türleri detay sayfasını göster
    """
    # Tüm illeri al
    tum_iller = AnaVeri.objects.all().order_by('il_adi')
    
    # Cihaz türleri tanımları
    cihaz_turleri = [
        {
            'id': 'surucu_kamera',
            'ad': 'Sürücü Analiz Kamerası',
            'icon': '📹',
            'renk': 'blue',
            'kategori': 'Güvenlik'
        },
        {
            'id': 'ats_takip',
            'ad': 'ATS Araç Takip Sistemi',
            'icon': '🚗',
            'renk': 'green',
            'kategori': 'Takip'
        },
        {
            'id': 'gps_konum',
            'ad': 'GPS Konum Takip',
            'icon': '📍',
            'renk': 'purple',
            'kategori': 'Navigasyon'
        },
        {
            'id': 'yakit_takip',
            'ad': 'Yakıt Takip Sistemi',
            'icon': '⛽',
            'renk': 'orange',
            'kategori': 'Maliyet'
        },
        {
            'id': 'motor_monitor',
            'ad': 'Motor Performans Monitörü',
            'icon': '⚙️',
            'renk': 'red',
            'kategori': 'Teknik'
        },
        {
            'id': 'hiz_sensor',
            'ad': 'Hız ve Mesafe Sensörü',
            'icon': '🏃',
            'renk': 'indigo',
            'kategori': 'Güvenlik'
        }
    ]
    
    # İl bazında cihaz türleri verileri
    il_cihaz_verileri = []
    
    for il in tum_iller:
        # Her il için cihaz türleri verilerini oluştur
        il_cihaz_data = {
            'il': il,
            'plaka': il.plaka if hasattr(il, 'plaka') else 'N/A',
            'il_adi': il.il_adi,
            'cihaz_turleri': []
        }
        
        for cihaz_tur in cihaz_turleri:
            # Her cihaz türü için rastgele veri oluştur (gerçek projede veritabanından gelecek)
            import random
            kurulacak = random.randint(50, 200)
            kurulan = random.randint(20, kurulacak)
            arizali = random.randint(0, 20)
            tamamlanma = round((kurulan / kurulacak * 100), 1) if kurulacak > 0 else 0
            
            il_cihaz_data['cihaz_turleri'].append({
                'tur': cihaz_tur,
                'kurulacak': kurulacak,
                'kurulan': kurulan,
                'arizali': arizali,
                'tamamlanma': tamamlanma,
                'durum_renk': 'green' if tamamlanma >= 80 else 'yellow' if tamamlanma >= 60 else 'red'
            })
        
        il_cihaz_verileri.append(il_cihaz_data)
    
    # Genel istatistikler
    toplam_il = len(il_cihaz_verileri)
    toplam_cihaz_turu = len(cihaz_turleri)
    
    # En iyi performans gösteren il
    en_iyi_il = max(il_cihaz_verileri, key=lambda x: sum(ct['tamamlanma'] for ct in x['cihaz_turleri']))
    
    # En kötü performans gösteren il
    en_kotu_il = min(il_cihaz_verileri, key=lambda x: sum(ct['tamamlanma'] for ct in x['cihaz_turleri']))
    
    context = {
        'il_cihaz_verileri': il_cihaz_verileri,
        'cihaz_turleri': cihaz_turleri,
        'toplam_il': toplam_il,
        'toplam_cihaz_turu': toplam_cihaz_turu,
        'en_iyi_il': en_iyi_il,
        'en_kotu_il': en_kotu_il,
    }
    
    return render(request, 'veri_yonetimi/illere_gore_cihaz_turleri.html', context)
