from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

class UserProfile(models.Model):
    """
    Kullanıcı profil bilgileri - TC kimlik numarası ve sorumlu iller
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Kullanıcı")
    tc_kimlik = models.CharField(max_length=11, unique=True, blank=True, null=True, verbose_name="TC Kimlik No")
    sorumlu_iller = models.TextField(blank=True, null=True, verbose_name="Sorumlu İller", 
                                    help_text="Bu kullanıcının sorumlu olduğu iller (virgülle ayrılmış). Boşsa tüm illeri görebilir.")
    
    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_sorumlu_iller_display()}"
    
    def get_sorumlu_iller_list(self):
        """Sorumlu illeri liste olarak döndür"""
        if not self.sorumlu_iller:
            return []
        return [il.strip() for il in self.sorumlu_iller.split(',') if il.strip()]
    
    def get_sorumlu_iller_display(self):
        """Sorumlu illeri görüntüleme için"""
        iller = self.get_sorumlu_iller_list()
        if not iller:
            return 'Tüm İller'
        elif len(iller) == 1:
            return iller[0]
        elif len(iller) <= 3:
            return ', '.join(iller)
        else:
            return f"{', '.join(iller[:3])}... (+{len(iller)-3})"
    
    def set_sorumlu_iller(self, iller_list):
        """Sorumlu illeri liste olarak set et"""
        if iller_list:
            self.sorumlu_iller = ', '.join(iller_list)
        else:
            self.sorumlu_iller = ''
    
    def is_responsible_for_il(self, il_adi):
        """Kullanıcının belirtilen ilden sorumlu olup olmadığını kontrol et"""
        if not self.sorumlu_iller:
            return True  # Boşsa tüm illere erişimi var
        return il_adi in self.get_sorumlu_iller_list()
    
    @property
    def tc_kimlik_display(self):
        """TC kimlik numarasını güvenli şekilde göster"""
        if self.tc_kimlik:
            return f"{self.tc_kimlik[:3]}***{self.tc_kimlik[-2:]}"
        return "Belirtilmemiş"

class UserLog(models.Model):
    """
    Kullanıcı işlemlerini takip etmek için log modeli
    """
    ISLEM_TIPLERI = [
        ('kullanici_olusturuldu', 'Kullanıcı Oluşturuldu'),
        ('kullanici_guncellendi', 'Kullanıcı Güncellendi'),
        ('kullanici_silindi', 'Kullanıcı Silindi'),
        ('durum_degistirildi', 'Durum Değiştirildi'),
        ('yetki_degistirildi', 'Yetki Değiştirildi'),
        ('giris_yapildi', 'Giriş Yapıldı'),
        ('cikis_yapildi', 'Çıkış Yapıldı'),
        ('profil_guncellendi', 'Profil Güncellendi'),
        ('sifre_degistirildi', 'Şifre Değiştirildi'),
        ('veri_eklendi', 'Veri Eklendi'),
        ('veri_guncellendi', 'Veri Güncellendi'),
        ('veri_silindi', 'Veri Silindi'),
        ('sutun_eklendi', 'Sütun Eklendi'),
        ('sutun_guncellendi', 'Sütun Güncellendi'),
        ('sutun_silindi', 'Sütun Silindi'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_logs', verbose_name="Kullanıcı")
    islem_yapan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='yapilan_islemler', verbose_name="İşlemi Yapan")
    islem_tipi = models.CharField(max_length=50, choices=ISLEM_TIPLERI, verbose_name="İşlem Tipi")
    aciklama = models.TextField(verbose_name="Açıklama")
    ip_adresi = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Adresi")
    user_agent = models.CharField(max_length=500, null=True, blank=True, verbose_name="User Agent")
    eski_deger = models.JSONField(null=True, blank=True, verbose_name="Eski Değer")
    yeni_deger = models.JSONField(null=True, blank=True, verbose_name="Yeni Değer")
    tarih = models.DateTimeField(auto_now_add=True, verbose_name="Tarih")
    
    class Meta:
        verbose_name = "Kullanıcı İşlem Logu"
        verbose_name_plural = "Kullanıcı İşlem Logları"
        ordering = ['-tarih']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_islem_tipi_display()} - {self.tarih.strftime('%d.%m.%Y %H:%M')}"
    
    @property
    def islem_rengi(self):
        """İşlem tipine göre renk sınıfı"""
        renk_mapping = {
            'kullanici_olusturuldu': 'text-green-600 bg-green-100',
            'kullanici_guncellendi': 'text-blue-600 bg-blue-100',
            'kullanici_silindi': 'text-red-600 bg-red-100',
            'durum_degistirildi': 'text-orange-600 bg-orange-100',
            'yetki_degistirildi': 'text-purple-600 bg-purple-100',
            'giris_yapildi': 'text-green-600 bg-green-100',
            'cikis_yapildi': 'text-gray-600 bg-gray-100',
            'profil_guncellendi': 'text-blue-600 bg-blue-100',
            'sifre_degistirildi': 'text-yellow-600 bg-yellow-100',
        }
        return renk_mapping.get(self.islem_tipi, 'text-gray-600 bg-gray-100')
    
    @property
    def islem_ikonu(self):
        """İşlem tipine göre ikon"""
        ikon_mapping = {
            'kullanici_olusturuldu': '➕',
            'kullanici_guncellendi': '✏️',
            'kullanici_silindi': '🗑️',
            'durum_degistirildi': '🔄',
            'yetki_degistirildi': '👑',
            'giris_yapildi': '🔓',
            'cikis_yapildi': '🔒',
            'profil_guncellendi': '👤',
            'sifre_degistirildi': '🔑',
            'veri_eklendi': '📝',
            'veri_guncellendi': '📋',
            'veri_silindi': '🗑️',
            'sutun_eklendi': '🗂️',
            'sutun_guncellendi': '📑',
            'sutun_silindi': '🗂️',
        }
        return ikon_mapping.get(self.islem_tipi, '📋')

class Sütun(models.Model):
    """
    Dinamik sütun tanımları
    """
    SUTUN_TIPLERI = [
        ('dinamik', 'Dinamik Sütun'),
        ('kurulacak', 'Kurulacak Cihaz Sayısı'),
        ('kurulan', 'Kurulan Cihaz Sayısı'),
        ('arizali', 'Arızalı Cihaz Sayısı'),
        ('tamamlanma', 'Tamamlanma Durumu'),
        ('veri_listesi', 'Veri Listesi Sütunu'),
        ('cihaz_turleri', 'Cihaz Türleri Sütunu'),
    ]
    
    MENU_TIPLERI = [
        ('veri_listesi', 'Veri Listesi'),
        ('cihaz_turleri', 'Cihaz Türleri'),
        ('genel', 'Genel (Tüm Menüler)'),
    ]
    
    ad = models.CharField(max_length=100, verbose_name="Sütun Adı")
    tip = models.CharField(max_length=20, choices=SUTUN_TIPLERI, default='dinamik', verbose_name="Sütun Tipi")
    menu_tipi = models.CharField(max_length=30, choices=MENU_TIPLERI, default='genel', verbose_name="Menü Tipi")
    sıra = models.PositiveIntegerField(verbose_name="Sıra", default=0)
    aktif = models.BooleanField(default=True, verbose_name="Aktif")
    gorunur = models.BooleanField(default=True, verbose_name="Görünür")
    genislik = models.CharField(max_length=20, default='auto', verbose_name="Genişlik", help_text="CSS genişlik değeri (px, %, auto)")
    hizalama = models.CharField(max_length=20, choices=[('left', 'Sol'), ('center', 'Orta'), ('right', 'Sağ')], default='left', verbose_name="Hizalama")
    oluşturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    
    class Meta:
        verbose_name = "Sütun"
        verbose_name_plural = "Sütunlar"
        ordering = ['menu_tipi', 'sıra', 'ad']
    
    def __str__(self):
        return f"{self.menu_tipi} - {self.sıra}. {self.ad}"
    
    @classmethod
    def get_menu_columns(cls, menu_tipi):
        """Belirli menü için aktif sütunları getir"""
        return cls.objects.filter(
            Q(aktif=True) & 
            Q(gorunur=True) & 
            (Q(menu_tipi=menu_tipi) | Q(menu_tipi='genel'))
        ).order_by('sıra')

class AnaVeri(models.Model):
    """
    Ana veri tablosu - dinamik sütunlar ile
    """
    il_adi = models.CharField(max_length=100, verbose_name="İl Adı", default="İstanbul")
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncellenme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    # Cihaz sayısı alanları
    kurulacak_cihaz_sayisi = models.PositiveIntegerField(
        default=0, 
        verbose_name="Kurulacak Cihaz Sayısı",
        help_text="Bu il için kurulacak toplam cihaz sayısı"
    )
    kurulan_cihaz_sayisi = models.PositiveIntegerField(
        default=0, 
        verbose_name="Kurulan Cihaz Sayısı",
        help_text="Bu il için şu ana kadar kurulan cihaz sayısı"
    )
    arizali_cihaz_sayisi = models.PositiveIntegerField(
        default=0, 
        verbose_name="Arızalı Cihaz Sayısı",
        help_text="Bu il için arızalı olan cihaz sayısı"
    )
    
    class Meta:
        verbose_name = "Ana Veri"
        verbose_name_plural = "Ana Veriler"
        ordering = ['-olusturulma_tarihi']
    
    def __str__(self):
        return f"Veri #{self.id} - {self.olusturulma_tarihi.strftime('%d.%m.%Y %H:%M')}"
    
    @property
    def tamamlanma_yuzdesi(self):
        """Kurulum tamamlanma yüzdesini hesapla"""
        if self.kurulacak_cihaz_sayisi == 0:
            return 0
        return round((self.kurulan_cihaz_sayisi / self.kurulacak_cihaz_sayisi) * 100, 1)
    
    @property
    def kalan_cihaz_sayisi(self):
        """Kurulacak kalan cihaz sayısı"""
        return max(0, self.kurulacak_cihaz_sayisi - self.kurulan_cihaz_sayisi)
    
    @property
    def durum_renk(self):
        """Tamamlanma durumuna göre renk sınıfı"""
        yuzde = self.tamamlanma_yuzdesi
        if yuzde >= 80:
            return 'text-green-600 bg-green-100'
        elif yuzde >= 60:
            return 'text-yellow-600 bg-yellow-100'
        elif yuzde >= 40:
            return 'text-orange-600 bg-orange-100'
        else:
            return 'text-red-600 bg-red-100'

class VeriDeger(models.Model):
    """
    Her veri için sütun değerleri
    """
    ana_veri = models.ForeignKey(AnaVeri, on_delete=models.CASCADE, related_name='degerler', verbose_name="Ana Veri")
    sutun = models.ForeignKey(Sütun, on_delete=models.CASCADE, verbose_name="Sütun")
    deger = models.CharField(max_length=500, verbose_name="Değer")
    
    class Meta:
        verbose_name = "Veri Değeri"
        verbose_name_plural = "Veri Değerleri"
        unique_together = ['ana_veri', 'sutun']
    
    def __str__(self):
        return f"{self.sutun.ad}: {self.deger}"

# Eski modelleri geriye uyumluluk için tutuyoruz
class SutunAyarlari(models.Model):
    """
    Geriye uyumluluk için eski sütun ayarları
    """
    sutun_1_baslik = models.CharField(max_length=50, default="Sütun 1", verbose_name="1. Sütun Başlığı")
    sutun_2_baslik = models.CharField(max_length=50, default="Sütun 2", verbose_name="2. Sütun Başlığı")
    sutun_3_baslik = models.CharField(max_length=50, default="Sütun 3", verbose_name="3. Sütun Başlığı")
    sutun_4_baslik = models.CharField(max_length=50, default="Sütun 4", verbose_name="4. Sütun Başlığı")
    guncellenme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "Sütun Ayarları (Eski)"
        verbose_name_plural = "Sütun Ayarları (Eski)"
    
    def __str__(self):
        return "Eski Sütun Ayarları"
