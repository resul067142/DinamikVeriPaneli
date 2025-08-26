from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg
from django.http import HttpResponse
import csv
import json
from datetime import datetime

from .models import AnaVeri, Sütun, VeriDeger
from .serializers import (
    AnaVeriSerializer, 
    SütunSerializer, 
    VeriDegerSerializer,
    KullaniciSerializer
)
from django.contrib.auth.models import User


class VeriListCreateAPIView(generics.ListCreateAPIView):
    """
    Veri listesi ve oluşturma API endpoint'i
    """
    queryset = AnaVeri.objects.all()
    serializer_class = AnaVeriSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['olusturulma_tarihi', 'guncellenme_tarihi']
    search_fields = ['degerler__deger']
    ordering_fields = ['olusturulma_tarihi', 'id']
    ordering = ['-olusturulma_tarihi']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # İl sorumlusu ise sadece kendi ilini göster
        if not self.request.user.is_superuser:
            user_plaka = self.request.user.last_name
            if user_plaka:
                queryset = queryset.filter(
                    degerler__sutun__ad='Plaka',
                    degerler__deger=user_plaka
                ).distinct()
        
        return queryset


class VeriRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Veri detay, güncelleme ve silme API endpoint'i
    """
    queryset = AnaVeri.objects.all()
    serializer_class = AnaVeriSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # İl sorumlusu ise sadece kendi ilini göster
        if not self.request.user.is_superuser:
            user_plaka = self.request.user.last_name
            if user_plaka:
                queryset = queryset.filter(
                    degerler__sutun__ad='Plaka',
                    degerler__deger=user_plaka
                ).distinct()
        
        return queryset


class VeriSearchAPIView(APIView):
    """
    Gelişmiş veri arama API endpoint'i
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        search_query = request.data.get('search', '')
        filters = request.data.get('filters', {})
        sort_by = request.data.get('sort_by', 'olusturulma_tarihi')
        sort_order = request.data.get('sort_order', 'desc')
        
        queryset = AnaVeri.objects.all()
        
        # İl sorumlusu kontrolü
        if not request.user.is_superuser:
            user_plaka = request.user.last_name
            if user_plaka:
                queryset = queryset.filter(
                    degerler__sutun__ad='Plaka',
                    degerler__deger=user_plaka
                ).distinct()
        
        # Arama
        if search_query:
            queryset = queryset.filter(
                Q(degerler__deger__icontains=search_query) |
                Q(id__icontains=search_query)
            ).distinct()
        
        # Filtreler
        for field, value in filters.items():
            if value:
                queryset = queryset.filter(
                    degerler__sutun__ad=field,
                    degerler__deger__icontains=value
                ).distinct()
        
        # Sıralama
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'
        queryset = queryset.order_by(sort_by)
        
        serializer = AnaVeriSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })


class SutunListCreateAPIView(generics.ListCreateAPIView):
    """
    Sütun listesi ve oluşturma API endpoint'i
    """
    queryset = Sütun.objects.all()
    serializer_class = SütunSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['aktif']
    ordering_fields = ['sıra', 'ad']
    ordering = ['sıra', 'ad']


class SutunRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Sütun detay, güncelleme ve silme API endpoint'i
    """
    queryset = Sütun.objects.all()
    serializer_class = SütunSerializer
    permission_classes = [IsAuthenticated]


class KullaniciListAPIView(generics.ListAPIView):
    """
    Kullanıcı listesi API endpoint'i (sadece admin)
    """
    queryset = User.objects.all()
    serializer_class = KullaniciSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'date_joined']
    ordering = ['username']


class KullaniciDetailAPIView(generics.RetrieveAPIView):
    """
    Kullanıcı detay API endpoint'i (sadece admin)
    """
    queryset = User.objects.all()
    serializer_class = KullaniciSerializer
    permission_classes = [IsAdminUser]


class IstatistikAPIView(APIView):
    """
    Genel istatistikler API endpoint'i
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Toplam veri sayısı
        total_veri = AnaVeri.objects.count()
        
        # Toplam sütun sayısı
        total_sutun = Sütun.objects.filter(aktif=True).count()
        
        # Toplam kullanıcı sayısı
        total_kullanici = User.objects.count()
        
        # Son eklenen veri tarihi
        son_veri_tarihi = AnaVeri.objects.aggregate(
            son_tarih=Max('olusturulma_tarihi')
        )['son_tarih']
        
        return Response({
            'total_veri': total_veri,
            'total_sutun': total_sutun,
            'total_kullanici': total_kullanici,
            'son_veri_tarihi': son_veri_tarihi,
            'son_guncelleme': datetime.now().isoformat()
        })


class IlIstatistikleriAPIView(APIView):
    """
    İl bazında istatistikler API endpoint'i
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # İl bazında cihaz istatistikleri
        il_istatistikleri = []
        
        for ana_veri in AnaVeri.objects.all():
            il_data = {}
            
            for deger in ana_veri.degerler.all():
                if deger.sutun.ad == 'Plaka':
                    il_data['plaka'] = deger.deger
                elif deger.sutun.ad == 'İl Adı':
                    il_data['il_adi'] = deger.deger
                elif deger.sutun.ad == 'Kurulacak Cihaz Sayısı':
                    il_data['kurulacak_cihaz'] = int(deger.deger) if deger.deger.isdigit() else 0
                elif deger.sutun.ad == 'Kurulan Cihaz Sayısı':
                    il_data['kurulan_cihaz'] = int(deger.deger) if deger.deger.isdigit() else 0
                elif deger.sutun.ad == 'Arızalı Cihaz Sayısı':
                    il_data['arizali_cihaz'] = int(deger.deger) if deger.deger.isdigit() else 0
            
            if 'plaka' in il_data and 'il_adi' in il_data:
                il_data['tamamlama_orani'] = (
                    (il_data['kurulan_cihaz'] / il_data['kurulacak_cihaz'] * 100)
                    if il_data['kurulacak_cihaz'] > 0 else 0
                )
                il_data['arizali_orani'] = (
                    (il_data['arizali_cihaz'] / il_data['kurulan_cihaz'] * 100)
                    if il_data['kurulan_cihaz'] > 0 else 0
                )
                il_istatistikleri.append(il_data)
        
        # Plaka sırasına göre sırala
        il_istatistikleri.sort(key=lambda x: int(x['plaka']))
        
        return Response({
            'il_istatistikleri': il_istatistikleri,
            'toplam_il': len(il_istatistikleri),
            'son_guncelleme': datetime.now().isoformat()
        })


class ExcelExportAPIView(APIView):
    """
    Excel export API endpoint'i
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Excel export işlemi burada yapılacak
        return Response({
            'message': 'Excel export özelliği yakında eklenecek',
            'status': 'coming_soon'
        })


class CSVExportAPIView(APIView):
    """
    CSV export API endpoint'i
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # CSV export işlemi
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="veri_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        
        # Başlık satırı
        aktif_sutunlar = Sütun.objects.filter(aktif=True).order_by('sıra')
        headers = [sutun.ad for sutun in aktif_sutunlar]
        headers.extend(['Oluşturulma Tarihi', 'Güncellenme Tarihi'])
        writer.writerow(headers)
        
        # Veri satırları
        for ana_veri in AnaVeri.objects.all():
            row = []
            for sutun in aktif_sutunlar:
                try:
                    deger = ana_veri.degerler.get(sutun=sutun).deger
                    row.append(deger)
                except VeriDeger.DoesNotExist:
                    row.append('')
            
            row.extend([
                ana_veri.olusturulma_tarihi.strftime('%d.%m.%Y %H:%M'),
                ana_veri.guncellenme_tarihi.strftime('%d.%m.%Y %H:%M')
            ])
            writer.writerow(row)
        
        return response


class PDFExportAPIView(APIView):
    """
    PDF export API endpoint'i
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # PDF export işlemi burada yapılacak
        return Response({
            'message': 'PDF export özelliği yakında eklenecek',
            'status': 'coming_soon'
        })


# Missing import for Max
from django.db.models import Max
