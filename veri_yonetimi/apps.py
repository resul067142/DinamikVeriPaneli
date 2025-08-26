from django.apps import AppConfig


class VeriYonetimiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'veri_yonetimi'
    
    def ready(self):
        import veri_yonetimi.templatetags.custom_filters
