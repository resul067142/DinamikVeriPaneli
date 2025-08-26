from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Sütun, AnaVeri, VeriDeger

class BasicTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_superuser=True
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Test sütunu oluştur
        self.sutun = Sütun.objects.create(
            ad='Test Sütun',
            aktif=True,
            sıra=1
        )
        
        # Test ana veri oluştur
        self.ana_veri = AnaVeri.objects.create()
        
        # Test veri değeri oluştur
        self.veri_deger = VeriDeger.objects.create(
            ana_veri=self.ana_veri,
            sutun=self.sutun,
            deger='Test Değer'
        )
    
    def test_models(self):
        """Temel model testleri"""
        self.assertEqual(str(self.sutun), '1. Test Sütun')
        self.assertEqual(str(self.ana_veri), f'Veri #{self.ana_veri.id} - {self.ana_veri.olusturulma_tarihi.strftime("%d.%m.%Y %H:%M")}')
        self.assertEqual(str(self.veri_deger), 'Test Sütun: Test Değer')
    
    def test_veri_listesi_view(self):
        """Veri listesi view testi"""
        response = self.client.get(reverse('veri_yonetimi:veri_listesi'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Değer')
    
    def test_sutun_listesi_view(self):
        """Sütun listesi view testi"""
        response = self.client.get(reverse('veri_yonetimi:sutun_listesi'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Sütun')
    
    def test_admin_access(self):
        """Admin erişim testi"""
        response = self.client.get(reverse('veri_yonetimi:veri_ekle'))
        self.assertEqual(response.status_code, 200)
    
    def test_non_admin_access(self):
        """Non-admin erişim testi"""
        # Normal kullanıcı oluştur
        normal_user = User.objects.create_user(
            username='normaluser',
            password='testpass123'
        )
        self.client.login(username='normaluser', password='testpass123')
        
        response = self.client.get(reverse('veri_yonetimi:veri_ekle'))
        self.assertEqual(response.status_code, 302)  # Redirect to list
