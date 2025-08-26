def app_settings(request):
    """
    Uygulama ayarlarını tüm template'lere ekle
    """
    return {
        'app_name': request.session.get('app_name', 'DVP'),
        'app_description': request.session.get('app_description', 'Dinamik Veri Paneli'),
    }
