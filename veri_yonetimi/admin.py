from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import AnaVeri, SutunAyarlari, Sütun, VeriDeger, UserProfile

@admin.register(Sütun)
class SütunAdmin(admin.ModelAdmin):
    list_display = ['ad', 'tip', 'sıra', 'aktif', 'oluşturulma_tarihi']
    list_filter = ['tip', 'aktif', 'oluşturulma_tarihi']
    search_fields = ['ad']
    ordering = ['sıra', 'ad']
    list_editable = ['tip', 'sıra', 'aktif']
    
    fieldsets = (
        ('Sütun Bilgileri', {
            'fields': ('ad', 'tip', 'sıra', 'aktif')
        }),
        ('Tarih Bilgileri', {
            'fields': ('oluşturulma_tarihi',),
            'classes': ('collapse',)
        }),
    )

@admin.register(AnaVeri)
class AnaVeriAdmin(admin.ModelAdmin):
    list_display = ['id', 'olusturulma_tarihi', 'guncellenme_tarihi', 'deger_sayisi', 'kurulacak_cihaz_sayisi', 'kurulan_cihaz_sayisi', 'arizali_cihaz_sayisi', 'tamamlanma_yuzdesi']
    list_filter = ['olusturulma_tarihi', 'guncellenme_tarihi']
    readonly_fields = ['olusturulma_tarihi', 'guncellenme_tarihi', 'tamamlanma_yuzdesi']
    ordering = ['-olusturulma_tarihi']
    
    fieldsets = (
        ('Cihaz Bilgileri', {
            'fields': ('kurulacak_cihaz_sayisi', 'kurulan_cihaz_sayisi', 'arizali_cihaz_sayisi')
        }),
        ('Tarih Bilgileri', {
            'fields': ('olusturulma_tarihi', 'guncellenme_tarihi'),
            'classes': ('collapse',)
        }),
    )
    
    def deger_sayisi(self, obj):
        return obj.degerler.count()
    deger_sayisi.short_description = 'Değer Sayısı'
    
    def tamamlanma_yuzdesi(self, obj):
        return f"%{obj.tamamlanma_yuzdesi}"
    tamamlanma_yuzdesi.short_description = 'Tamamlanma %'

@admin.register(VeriDeger)
class VeriDegerAdmin(admin.ModelAdmin):
    list_display = ['ana_veri', 'sutun', 'deger']
    list_filter = ['sutun', 'sutun__aktif']
    search_fields = ['deger', 'sutun__ad']
    ordering = ['sutun__sıra', 'ana_veri__id']

@admin.register(SutunAyarlari)
class SutunAyarlariAdmin(admin.ModelAdmin):
    list_display = ['sutun_1_baslik', 'sutun_2_baslik', 'sutun_3_baslik', 'sutun_4_baslik', 'guncellenme_tarihi']
    readonly_fields = ['guncellenme_tarihi']
    
    def has_add_permission(self, request):
        # Sadece bir tane kayıt olmasına izin ver
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        # Silmeye izin verme
        return False

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'tc_kimlik_display', 'tc_kimlik']
    list_filter = ['user__is_active', 'user__is_superuser']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'tc_kimlik']
    ordering = ['user__username']
    
    fieldsets = (
        ('Kullanıcı Bilgileri', {
            'fields': ('user', 'tc_kimlik')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# User model'ine TC kimlik alanı ekle
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil Bilgileri'

# User admin'ini özelleştir
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'tc_kimlik_display', 'is_staff', 'is_active')
    
    def tc_kimlik_display(self, obj):
        if hasattr(obj, 'profile') and obj.profile.tc_kimlik:
            return obj.profile.tc_kimlik_display
        return "Belirtilmemiş"
    tc_kimlik_display.short_description = 'TC Kimlik'

# User admin'ini yeniden kaydet
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
