from django.urls import path
from . import api_views

app_name = 'api'

urlpatterns = [
    # Veri API endpoints
    path('veriler/', api_views.VeriListCreateAPIView.as_view(), name='veri-list-create'),
    path('veriler/<int:pk>/', api_views.VeriRetrieveUpdateDestroyAPIView.as_view(), name='veri-detail'),
    path('veriler/search/', api_views.VeriSearchAPIView.as_view(), name='veri-search'),
    
    # Sütun API endpoints
    path('sutunlar/', api_views.SutunListCreateAPIView.as_view(), name='sutun-list-create'),
    path('sutunlar/<int:pk>/', api_views.SutunRetrieveUpdateDestroyAPIView.as_view(), name='sutun-detail'),
    
    # Kullanıcı API endpoints
    path('kullanicilar/', api_views.KullaniciListAPIView.as_view(), name='kullanici-list'),
    path('kullanicilar/<int:pk>/', api_views.KullaniciDetailAPIView.as_view(), name='kullanici-detail'),
    
    # İstatistik API endpoints
    path('istatistikler/', api_views.IstatistikAPIView.as_view(), name='istatistikler'),
    path('istatistikler/iller/', api_views.IlIstatistikleriAPIView.as_view(), name='il-istatistikleri'),
    
    # Export API endpoints
    path('export/excel/', api_views.ExcelExportAPIView.as_view(), name='excel-export'),
    path('export/csv/', api_views.CSVExportAPIView.as_view(), name='csv-export'),
    path('export/pdf/', api_views.PDFExportAPIView.as_view(), name='pdf-export'),
]
