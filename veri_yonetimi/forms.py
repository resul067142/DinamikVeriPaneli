from django import forms
from .models import AnaVeri, Sütun, VeriDeger

class AnaVeriForm(forms.ModelForm):
    """
    AnaVeri modeli için dinamik form
    """
    class Meta:
        model = AnaVeri
        fields = []  # AnaVeri'de sadece tarih alanları var
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aktif sütunları al
        aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
        
        # Her aktif sütun için form alanı oluştur
        for sutun in aktif_sutunlar:
            field_name = f'sutun_{sutun.id}'
            
            # Mevcut değeri al (edit durumunda)
            initial_value = ''
            if self.instance and self.instance.pk:
                try:
                    veri_deger = self.instance.degerler.get(sutun=sutun)
                    initial_value = veri_deger.deger
                except VeriDeger.DoesNotExist:
                    pass
            elif hasattr(self, 'initial_data') and self.initial_data:
                # POST verisi varsa onu kullan
                field_name = f'sutun_{sutun.id}'
                initial_value = self.initial_data.get(field_name, '')
            
            # Plaka alanı için özel validasyon
            if sutun.ad == 'Plaka':
                self.fields[field_name] = forms.CharField(
                    max_length=10,
                    label=sutun.ad,
                    required=True,
                    initial=initial_value,
                    widget=forms.TextInput(attrs={
                        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                        'placeholder': f'{sutun.ad} değerini girin (örn: 01, 06, 34)',
                        'pattern': '[0-9]{1,2}',
                        'title': 'Lütfen 1-2 haneli plaka numarası girin'
                    })
                )
            else:
                self.fields[field_name] = forms.CharField(
                    max_length=500,
                    label=sutun.ad,
                    required=False,
                    initial=initial_value,
                    widget=forms.TextInput(attrs={
                        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                        'placeholder': f'{sutun.ad} değerini girin'
                    })
                )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Plaka alanı için özel validasyon
        aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
        for sutun in aktif_sutunlar:
            if sutun.ad == 'Plaka':
                field_name = f'sutun_{sutun.id}'
                plaka_value = cleaned_data.get(field_name, '').strip()
                
                if not plaka_value:
                    self.add_error(field_name, 'Plaka alanı zorunludur.')
                elif not plaka_value.isdigit():
                    self.add_error(field_name, 'Plaka sadece rakam içermelidir.')
                elif len(plaka_value) > 2:
                    self.add_error(field_name, 'Plaka en fazla 2 haneli olabilir.')
                elif int(plaka_value) < 1 or int(plaka_value) > 81:
                    self.add_error(field_name, 'Plaka 1-81 arasında olmalıdır.')
                
                # Aynı plaka ile başka kayıt var mı kontrol et
                if plaka_value and not self.instance.pk:  # Sadece yeni kayıt için
                    existing_plaka = VeriDeger.objects.filter(
                        sutun__ad='Plaka',
                        deger=plaka_value
                    ).exists()
                    if existing_plaka:
                        self.add_error(field_name, f'Bu plaka ({plaka_value}) zaten kullanılıyor.')
        
        return cleaned_data
    
    def save(self, commit=True):
        ana_veri = super().save(commit=False)
        
        # Cihaz sayısı alanlarını doğrudan AnaVeri'ye kaydet
        aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
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
                    # Bu alan otomatik hesaplanıyor
                    pass
                else:
                    # Dinamik sütunlar için VeriDeger tablosuna kaydet
                    if deger:  # Boş değerleri kaydetme
                        VeriDeger.objects.update_or_create(
                            ana_veri=ana_veri,
                            sutun=sutun,
                            defaults={'deger': deger}
                        )
                    else:
                        # Boş değer varsa mevcut kaydı sil
                        VeriDeger.objects.filter(
                            ana_veri=ana_veri,
                            sutun=sutun
                        ).delete()
        
        if commit:
            ana_veri.save()
        
        return ana_veri

class SütunForm(forms.ModelForm):
    """
    Sütun ekleme/düzenleme formu
    """
    class Meta:
        model = Sütun
        fields = ['ad', 'sıra', 'aktif']
        widgets = {
            'ad': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Sütun adını girin'
            }),
            'sıra': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '0'
            }),
            'aktif': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
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
