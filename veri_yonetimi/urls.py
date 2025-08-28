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
    path('kullanici/<int:pk>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('kullanici/<int:pk>/change-role/', views.change_user_role, name='change_user_role'),
    path('kullanici/<int:pk>/cities/', views.get_user_cities, name='get_user_cities'),
    path('kullanici/<int:pk>/assign-cities/', views.assign_cities_to_user, name='assign_cities_to_user'),
    path('kullanici/fake-tc/', views.generate_fake_tc, name='generate_fake_tc'),
    path('kullanici/loglari/', views.kullanici_loglari, name='kullanici_loglari'),
    path('kullanici/loglari/excel/', views.kullanici_loglari_excel, name='kullanici_loglari_excel'),
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
