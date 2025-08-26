import os
from celery import Celery

# Django ayarlarını Celery için set et
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dinamik_veri_paneli.settings')

# Celery app oluştur
app = Celery('veri_yonetimi')

# Django ayarlarından Celery konfigürasyonunu al
app.config_from_object('django.conf:settings', namespace='CELERY')

# Otomatik olarak tüm Django app'lerdeki tasks.py dosyalarını bul
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """
    Debug task - test amaçlı
    """
    print(f'Request: {self.request!r}')


# Periyodik görevler
app.conf.beat_schedule = {
    'veri-yedekleme': {
        'task': 'veri_yonetimi.tasks.yedekle_veriler',
        'schedule': 3600.0,  # Her saat
    },
    'istatistik-guncelle': {
        'task': 'veri_yonetimi.tasks.guncelle_istatistikler',
        'schedule': 1800.0,  # Her 30 dakika
    },
    'eski-loglari-temizle': {
        'task': 'veri_yonetimi.tasks.temizle_eski_loglar',
        'schedule': 86400.0,  # Her gün
    },
}
