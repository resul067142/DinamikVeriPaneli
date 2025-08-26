from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Kullanıcı profil bilgileri - TC kimlik numarası vb.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Kullanıcı")
    tc_kimlik = models.CharField(max_length=11, unique=True, blank=True, null=True, verbose_name="TC Kimlik No")
    
    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"
    
    def __str__(self):
        return f"{self.user.username} - {self.tc_kimlik or 'TC Belirtilmemiş'}"
    
    @property
    def tc_kimlik_display(self):
        """TC kimlik numarasını güvenli şekilde göster"""
        if self.tc_kimlik:
            return f"{self.tc_kimlik[:3]}***{self.tc_kimlik[-2:]}"
        return "Belirtilmemiş"

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
    ]
    
    ad = models.CharField(max_length=100, verbose_name="Sütun Adı")
    tip = models.CharField(max_length=20, choices=SUTUN_TIPLERI, default='dinamik', verbose_name="Sütun Tipi")
    sıra = models.PositiveIntegerField(verbose_name="Sıra", default=0)
    aktif = models.BooleanField(default=True, verbose_name="Aktif")
    oluşturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    
    class Meta:
        verbose_name = "Sütun"
        verbose_name_plural = "Sütunlar"
        ordering = ['sıra', 'ad']
    
    def __str__(self):
        return f"{self.sıra}. {self.ad}"

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
