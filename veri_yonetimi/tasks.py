from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
import json
import csv
import os
from .models import AnaVeri, Sütun, VeriDeger
from django.contrib.auth.models import User


@shared_task
def yedekle_veriler():
    """
    Verileri JSON formatında yedekle
    """
    try:
        # Yedekleme dizini oluştur
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Veri yapısını oluştur
        backup_data = {
            'timestamp': timezone.now().isoformat(),
            'sutunlar': [],
            'veriler': []
        }
        
        # Sütunları yedekle
        for sutun in Sütun.objects.all():
            backup_data['sutunlar'].append({
                'id': sutun.id,
                'ad': sutun.ad,
                'sıra': sutun.sıra,
                'aktif': sutun.aktif,
                'oluşturulma_tarihi': sutun.oluşturulma_tarihi.isoformat()
            })
        
        # Verileri yedekle
        for ana_veri in AnaVeri.objects.all():
            veri_data = {
                'id': ana_veri.id,
                'olusturulma_tarihi': ana_veri.olusturulma_tarihi.isoformat(),
                'guncellenme_tarihi': ana_veri.guncellenme_tarihi.isoformat(),
                'degerler': []
            }
            
            for deger in ana_veri.degerler.all():
                veri_data['degerler'].append({
                    'sutun_id': deger.sutun.id,
                    'sutun_adi': deger.sutun.ad,
                    'deger': deger.deger
                })
            
            backup_data['veriler'].append(veri_data)
        
        # JSON dosyasına kaydet
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_{timestamp}.json'
        filepath = os.path.join(backup_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        # Eski yedekleri temizle (7 günden eski)
        cleanup_old_backups()
        
        return f"Veri yedekleme başarılı: {filename}"
    
    except Exception as e:
        return f"Veri yedekleme hatası: {str(e)}"


@shared_task
def guncelle_istatistikler():
    """
    Sistem istatistiklerini güncelle ve cache'e kaydet
    """
    try:
        from django.core.cache import cache
        
        # Genel istatistikler
        stats = {
            'total_veri': AnaVeri.objects.count(),
            'total_sutun': Sütun.objects.filter(aktif=True).count(),
            'total_kullanici': User.objects.count(),
            'son_guncelleme': timezone.now().isoformat()
        }
        
        # İl bazında istatistikler
        il_stats = []
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
                il_stats.append(il_data)
        
        # Plaka sırasına göre sırala
        il_stats.sort(key=lambda x: int(x['plaka']))
        stats['il_istatistikleri'] = il_stats
        
        # Cache'e kaydet (1 saat geçerli)
        cache.set('system_stats', stats, 3600)
        
        return f"İstatistikler güncellendi: {len(il_stats)} il"
    
    except Exception as e:
        return f"İstatistik güncelleme hatası: {str(e)}"


@shared_task
def temizle_eski_loglar():
    """
    Eski log dosyalarını temizle
    """
    try:
        import glob
        
        # Log dizini
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            return "Log dizini bulunamadı"
        
        # 30 günden eski log dosyalarını bul
        cutoff_date = timezone.now() - timedelta(days=30)
        deleted_count = 0
        
        for log_file in glob.glob(os.path.join(log_dir, '*.log')):
            file_time = timezone.datetime.fromtimestamp(
                os.path.getmtime(log_file),
                tz=timezone.utc
            )
            
            if file_time < cutoff_date:
                os.remove(log_file)
                deleted_count += 1
        
        return f"{deleted_count} eski log dosyası silindi"
    
    except Exception as e:
        return f"Log temizleme hatası: {str(e)}"


@shared_task
def export_veriler_csv():
    """
    Verileri CSV formatında export et
    """
    try:
        # Export dizini oluştur
        export_dir = 'exports'
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        # CSV dosyası oluştur
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'veri_export_{timestamp}.csv'
        filepath = os.path.join(export_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
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
        
        # Eski export dosyalarını temizle (3 günden eski)
        cleanup_old_exports()
        
        return f"CSV export başarılı: {filename}"
    
    except Exception as e:
        return f"CSV export hatası: {str(e)}"


@shared_task
def email_raporu_gonder(recipient_email):
    """
    Günlük raporu email ile gönder
    """
    try:
        # İstatistikleri al
        stats = guncelle_istatistikler()
        
        # Email içeriği
        subject = f'Günlük Rapor - {timezone.now().strftime("%d.%m.%Y")}'
        
        message = f"""
        Günlük Sistem Raporu
        
        Tarih: {timezone.now().strftime("%d.%m.%Y %H:%M")}
        
        Genel İstatistikler:
        - Toplam Veri: {stats.get('total_veri', 0)}
        - Toplam Sütun: {stats.get('total_sutun', 0)}
        - Toplam Kullanıcı: {stats.get('total_kullanici', 0)}
        
        Bu rapor otomatik olarak oluşturulmuştur.
        """
        
        # Email gönder
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        
        return f"Email raporu gönderildi: {recipient_email}"
    
    except Exception as e:
        return f"Email gönderme hatası: {str(e)}"


def cleanup_old_backups():
    """
    Eski yedek dosyalarını temizle (7 günden eski)
    """
    try:
        import glob
        
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            return
        
        cutoff_date = timezone.now() - timedelta(days=7)
        deleted_count = 0
        
        for backup_file in glob.glob(os.path.join(backup_dir, 'backup_*.json')):
            file_time = timezone.datetime.fromtimestamp(
                os.path.getmtime(backup_file),
                tz=timezone.utc
            )
            
            if file_time < cutoff_date:
                os.remove(backup_file)
                deleted_count += 1
        
        return deleted_count
    
    except Exception:
        return 0


def cleanup_old_exports():
    """
    Eski export dosyalarını temizle (3 günden eski)
    """
    try:
        import glob
        
        export_dir = 'exports'
        if not os.path.exists(export_dir):
            return
        
        cutoff_date = timezone.now() - timedelta(days=3)
        deleted_count = 0
        
        for export_file in glob.glob(os.path.join(export_dir, '*.csv')):
            file_time = timezone.datetime.fromtimestamp(
                os.path.getmtime(export_file),
                tz=timezone.utc
            )
            
            if file_time < cutoff_date:
                os.remove(export_file)
                deleted_count += 1
        
        return deleted_count
    
    except Exception:
        return 0
