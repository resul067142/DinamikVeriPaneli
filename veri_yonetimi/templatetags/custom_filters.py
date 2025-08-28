from django import template
from django.utils import timezone
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Dictionary'den key ile değer alma
    """
    return dictionary.get(key, '')

@register.filter
def add_string(value, arg):
    """
    String concatenation
    """
    return str(value) + str(arg)

@register.filter
def get_field(form, field_name):
    """
    Form'dan field_name ile field alma
    """
    return form[field_name]

@register.filter
def get_today_logs_count(user):
    """
    Kullanıcının bugünkü işlem sayısı
    """
    try:
        from ..models import UserLog
        today = timezone.now().date()
        return UserLog.objects.filter(
            islem_yapan=user,
            tarih__date=today
        ).count()
    except:
        return 0

@register.filter
def get_week_logs_count(user):
    """
    Kullanıcının son 7 gündeki işlem sayısı
    """
    try:
        from ..models import UserLog
        week_ago = timezone.now() - timedelta(days=7)
        return UserLog.objects.filter(
            islem_yapan=user,
            tarih__gte=week_ago
        ).count()
    except:
        return 0

@register.filter
def get_total_logs_count(user):
    """
    Kullanıcının toplam işlem sayısı
    """
    try:
        from ..models import UserLog
        return UserLog.objects.filter(islem_yapan=user).count()
    except:
        return 0
