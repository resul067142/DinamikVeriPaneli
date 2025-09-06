from django import forms
from .models import AnaVeri, Sütun, VeriDeger

class AnaVeriForm(forms.Form):
    """
    AnaVeri modeli için dinamik form
    """
    # ModelForm yerine Form kullan - hiç zorunlu field olmasın
    
    def __init__(self, *args, **kwargs):
        # Kullanıcı bilgisini al
        self.user = kwargs.pop('user', None)
        # Instance bilgisini al (güncelleme için)
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        # Aktif sütunları al
        aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
        
        # Her aktif sütun için form alanı oluştur
        for sutun in aktif_sutunlar:
            field_name = f'sutun_{sutun.id}'
            
            # Plaka sütunu için özel işlem
            if sutun.ad == 'Plaka':
                # Plaka için simple text input (choice olmasın)
                self.fields[field_name] = forms.CharField(
                    max_length=10,
                    label=sutun.ad,
                    required=False,
                    widget=forms.TextInput(attrs={
                        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                        'placeholder': 'Plaka kodu girin (01-81)',
                        'pattern': '[0-9]{1,2}',
                        'title': '1-81 arası plaka kodu'
                    })
                )
            # İl Adı sütunu için özel işlem
            elif sutun.ad == 'İl Adı':
                # İl Adı için de simple text input (choice olmasın)
                self.fields[field_name] = forms.CharField(
                    max_length=50,
                    label=sutun.ad,
                    required=False,
                    widget=forms.TextInput(attrs={
                        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                        'placeholder': 'İl adını girin',
                        'list': f'il_listesi_{sutun.id}'
                    })
                )

            else:
                # Diğer sütunlar için normal text input
                self.fields[field_name] = forms.CharField(
                    max_length=500,
                    label=sutun.ad,
                    required=False,  # Hepsini False yap
                    widget=forms.TextInput(attrs={
                        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                                            'placeholder': f'{sutun.ad} değerini girin'
                })
            )
    
    def set_initial_from_instance(self):
        """Instance'dan initial değerleri set et"""
        if not self.instance:
            return
            
        initial_data = {}
        aktif_sutunlar = Sütun.objects.filter(aktif=True)
        
        for sutun in aktif_sutunlar:
            field_name = f'sutun_{sutun.id}'
            
            if sutun.tip == 'kurulacak':
                initial_data[field_name] = self.instance.kurulacak_cihaz_sayisi
            elif sutun.tip == 'kurulan':
                initial_data[field_name] = self.instance.kurulan_cihaz_sayisi
            elif sutun.tip == 'arizali':
                initial_data[field_name] = self.instance.arizali_cihaz_sayisi
            elif sutun.tip == 'tamamlanma':
                if self.instance.kurulacak_cihaz_sayisi and self.instance.kurulacak_cihaz_sayisi > 0:
                    tamamlanma = int((self.instance.kurulan_cihaz_sayisi / self.instance.kurulacak_cihaz_sayisi) * 100)
                    initial_data[field_name] = tamamlanma
                else:
                    initial_data[field_name] = 0
            elif sutun.ad == 'İl Adı':
                initial_data[field_name] = self.instance.il_adi
            else:
                # Dinamik sütunlar için VeriDeger'dan değeri al
                try:
                    from .models import VeriDeger
                    veri_deger = VeriDeger.objects.get(ana_veri=self.instance, sutun=sutun)
                    initial_data[field_name] = veri_deger.deger
                except VeriDeger.DoesNotExist:
                    initial_data[field_name] = ''
        
        # Form field'larına initial değerleri set et
        for field_name, value in initial_data.items():
            if field_name in self.fields:
                self.fields[field_name].initial = value
                self.initial[field_name] = value
        
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Plaka validasyonu - sadece Plaka sütunları için kontrol et
        plaka_sutunlar = Sütun.objects.filter(ad='Plaka', aktif=True)
        
        for sutun in plaka_sutunlar:
            field_name = f'sutun_{sutun.id}'
            if field_name in cleaned_data:
                value = cleaned_data[field_name]
                
                # Plaka alanı için özel validasyon (opsiyonel)
                if value:  # Sadece değer varsa validate et
                    if not value.isdigit():
                        self.add_error(field_name, 'Plaka alanına sadece rakam girebilirsiniz. Örnek: 01, 06, 34, 35')
                    elif int(value) < 1 or int(value) > 81:
                        self.add_error(field_name, 'Plaka 01-81 arasında olmalıdır. Girdiğiniz değer: ' + value)
        
        return cleaned_data
    
    def save(self, commit=True):
        
        # Mevcut instance'ı kullan veya yeni oluştur
        ana_veri = self.instance if self.instance else AnaVeri()
        
        # Cihaz sayısı alanlarını doğrudan AnaVeri'ye kaydet
        aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
        
        # İl adını set et
        il_adi = None
        for sutun in aktif_sutunlar:
            if sutun.ad == 'İl Adı':
                field_name = f'sutun_{sutun.id}'
                if field_name in self.cleaned_data:
                    il_adi = self.cleaned_data[field_name]
                    break
        
        if il_adi:
            ana_veri.il_adi = il_adi
        
        if commit:
            ana_veri.save()
            
            # VeriDeger'ları kaydet
            for sutun in aktif_sutunlar:
                field_name = f'sutun_{sutun.id}'
                
                if field_name in self.cleaned_data:
                    deger = self.cleaned_data[field_name]
                    
                    # Cihaz sayısı alanları için özel işlem
                    if sutun.tip == 'kurulacak':
                        ana_veri.kurulacak_cihaz_sayisi = int(deger) if deger else 0
                    elif sutun.tip == 'kurulan':
                        ana_veri.kurulan_cihaz_sayisi = int(deger) if deger else 0
                    elif sutun.tip == 'arizali':
                        ana_veri.arizali_cihaz_sayisi = int(deger) if deger else 0
                    elif sutun.tip == 'tamamlanma':
                        # tamamlanma_yuzdesi property olduğu için set edilemez
                        pass
                    else:
                        # Dinamik sütunlar için VeriDeger tablosuna kaydet
                        try:
                            # Mevcut değeri bul veya yeni oluştur
                            veri_deger, created = VeriDeger.objects.get_or_create(
                                ana_veri=ana_veri,
                                sutun=sutun,
                                defaults={'deger': deger if deger else ''}
                            )
                            if not created:
                                # Mevcut değeri güncelle
                                veri_deger.deger = deger if deger else ''
                                veri_deger.save()
                        except Exception as e:
                            pass
                else:
                    pass
            
            # Cihaz sayılarını tekrar kaydet (VeriDeger'lardan sonra)
            ana_veri.save()
        
        return ana_veri

class SütunForm(forms.ModelForm):
    """
    Sütun ekleme/düzenleme formu
    """
    class Meta:
        model = Sütun
        fields = ['ad', 'tip', 'menu_tipi', 'sıra', 'aktif', 'gorunur', 'genislik', 'hizalama']
        widgets = {
            'ad': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Sütun adını girin'
            }),
            'tip': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'menu_tipi': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'sıra': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '0'
            }),
            'aktif': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
            }),
            'gorunur': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
            }),
            'genislik': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'auto, 100px, 20% vb.'
            }),
            'hizalama': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            })
        }
    
    def clean_ad(self):
        ad = self.cleaned_data['ad'].strip()
        if not ad:
            raise forms.ValidationError('Sütun adı boş olamaz.')
        
        # Aynı isimde başka sütun var mı kontrol et
        existing = Sütun.objects.filter(ad=ad)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise forms.ValidationError(f'"{ad}" adında bir sütun zaten mevcut.')
        
        return ad
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Menü tipi seçeneklerini güncelle
        self.fields['menu_tipi'].choices = [
            ('veri_listesi', '📊 Veri Listesi'),
            ('cihaz_turleri', '📱 Cihaz Türleri'),
            ('genel', '🌐 Genel (Tüm Menüler)'),
        ]
        
        # Sütun tipi seçeneklerini güncelle
        self.fields['tip'].choices = [
            ('dinamik', '🔄 Dinamik Sütun'),
            ('kurulacak', '📦 Kurulacak Cihaz Sayısı'),
            ('kurulan', '✅ Kurulan Cihaz Sayısı'),
            ('arizali', '⚠️ Arızalı Cihaz Sayısı'),
            ('tamamlanma', '📈 Tamamlanma Durumu'),
            ('cihaz_turleri', '📱 Cihaz Türleri Sütunu'),
        ]
