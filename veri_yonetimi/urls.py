from django.urls import path
from . import views, auth_views

app_name = 'veri_yonetimi'

urlpatterns = [
    # Ana sayfa
    path('', views.ana_sayfa, name='ana_sayfa'),
    path('dashboard/', views.ana_sayfa, name='dashboard'),
    
    # Veri listesi
    path('veri/', views.veri_listesi, name='veri_listesi'),
    
    # Kullanıcı yönetimi
    path('kullanicilar/', views.kullanici_listesi, name='kullanici_listesi'),
    path('kullanici/ekle/', views.kullanici_ekle, name='kullanici_ekle'),
    path('kullanici/guncelle/<int:pk>/', views.kullanici_guncelle, name='kullanici_guncelle'),
    path('kullanici/fake-tc/', views.generate_fake_tc, name='generate_fake_tc'),
    path('login/', auth_views.user_login, name='user_login'),
    path('register/', auth_views.user_register, name='user_register'),
    path('logout/', auth_views.user_logout, name='user_logout'),
    
    # CRUD işlemleri
    path('veri/ekle/', views.veri_ekle, name='veri_ekle'),
    path('veri/guncelle/<int:pk>/', views.veri_guncelle, name='veri_guncelle'),
    path('veri/sil/<int:pk>/', views.veri_sil, name='veri_sil'),
    path('veri/sil-onay/<int:pk>/', views.veri_sil_onay, name='veri_sil_onay'),
    
    # Sütun yönetimi
    path('sutunlar/', views.sutun_listesi, name='sutun_listesi'),
    path('sutun/ekle/', views.sutun_ekle, name='sutun_ekle'),
    path('sutun/guncelle/<int:pk>/', views.sutun_guncelle, name='sutun_guncelle'),
    path('sutun/sil/<int:pk>/', views.sutun_sil, name='sutun_sil'),
    
    # Site ayarları
    path('update-app-settings/', views.update_app_settings, name='update_app_settings'),
]
