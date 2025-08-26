from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AnaVeri, Sütun, VeriDeger


class VeriDegerSerializer(serializers.ModelSerializer):
    """
    VeriDeger modeli için serializer
    """
    sutun_adi = serializers.CharField(source='sutun.ad', read_only=True)
    sutun_sira = serializers.IntegerField(source='sutun.sıra', read_only=True)
    
    class Meta:
        model = VeriDeger
        fields = ['id', 'sutun', 'sutun_adi', 'sutun_sira', 'deger']


class SütunSerializer(serializers.ModelSerializer):
    """
    Sütun modeli için serializer
    """
    class Meta:
        model = Sütun
        fields = ['id', 'ad', 'sıra', 'aktif', 'oluşturulma_tarihi']


class AnaVeriSerializer(serializers.ModelSerializer):
    """
    AnaVeri modeli için serializer
    """
    degerler = VeriDegerSerializer(many=True, read_only=True)
    sutun_degerleri = serializers.SerializerMethodField()
    
    class Meta:
        model = AnaVeri
        fields = ['id', 'olusturulma_tarihi', 'guncellenme_tarihi', 'degerler', 'sutun_degerleri']
        read_only_fields = ['olusturulma_tarihi', 'guncellenme_tarihi']
    
    def get_sutun_degerleri(self, obj):
        """
        Sütun bazında değerleri döndür
        """
        degerler = {}
        for deger in obj.degerler.all():
            degerler[deger.sutun.ad] = deger.deger
        return degerler
    
    def create(self, validated_data):
        """
        AnaVeri ve VeriDeger kayıtlarını oluştur
        """
        # AnaVeri kaydını oluştur
        ana_veri = AnaVeri.objects.create()
        
        # Sütun değerlerini al
        sutun_degerleri = self.context.get('sutun_degerleri', {})
        
        # Her sütun için VeriDeger oluştur
        for sutun_id, deger in sutun_degerleri.items():
            try:
                sutun = Sütun.objects.get(id=sutun_id)
                if deger:  # Boş değerleri kaydetme
                    VeriDeger.objects.create(
                        ana_veri=ana_veri,
                        sutun=sutun,
                        deger=str(deger)
                    )
            except Sütun.DoesNotExist:
                pass
        
        return ana_veri
    
    def update(self, instance, validated_data):
        """
        AnaVeri ve VeriDeger kayıtlarını güncelle
        """
        # Sütun değerlerini al
        sutun_degerleri = self.context.get('sutun_degerleri', {})
        
        # Mevcut değerleri güncelle
        for sutun_id, deger in sutun_degerleri.items():
            try:
                sutun = Sütun.objects.get(id=sutun_id)
                if deger:  # Boş değerleri kaydetme
                    VeriDeger.objects.update_or_create(
                        ana_veri=instance,
                        sutun=sutun,
                        defaults={'deger': str(deger)}
                    )
                else:
                    # Boş değer varsa mevcut kaydı sil
                    VeriDeger.objects.filter(
                        ana_veri=instance,
                        sutun=sutun
                    ).delete()
            except Sütun.DoesNotExist:
                pass
        
        return instance


class KullaniciSerializer(serializers.ModelSerializer):
    """
    User modeli için serializer
    """
    groups = serializers.SerializerMethodField()
    is_il_sorumlusu = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'date_joined', 'is_active', 'is_staff', 'is_superuser', 'groups', 'is_il_sorumlusu']
        read_only_fields = ['id', 'date_joined']
    
    def get_groups(self, obj):
        """
        Kullanıcının gruplarını döndür
        """
        return [group.name for group in obj.groups.all()]
    
    def get_is_il_sorumlusu(self, obj):
        """
        Kullanıcının il sorumlusu olup olmadığını kontrol et
        """
        return obj.groups.filter(name='İl Sorumlusu').exists()


class AnaVeriCreateSerializer(serializers.ModelSerializer):
    """
    AnaVeri oluşturma için özel serializer
    """
    sutun_degerleri = serializers.DictField(
        child=serializers.CharField(max_length=500, required=False),
        required=False
    )
    
    class Meta:
        model = AnaVeri
        fields = ['sutun_degerleri']
    
    def validate_sutun_degerleri(self, value):
        """
        Sütun değerlerini validate et
        """
        if not value:
            raise serializers.ValidationError("En az bir sütun değeri gerekli")
        
        # Plaka validasyonu
        for sutun_id, deger in value.items():
            try:
                sutun = Sütun.objects.get(id=sutun_id)
                if sutun.ad == 'Plaka':
                    if not deger:
                        raise serializers.ValidationError("Plaka alanı zorunludur")
                    if not deger.isdigit():
                        raise serializers.ValidationError("Plaka sadece rakam içermelidir")
                    if len(deger) > 2:
                        raise serializers.ValidationError("Plaka en fazla 2 haneli olabilir")
                    if int(deger) < 1 or int(deger) > 81:
                        raise serializers.ValidationError("Plaka 1-81 arasında olmalıdır")
            except Sütun.DoesNotExist:
                raise serializers.ValidationError(f"Geçersiz sütun ID: {sutun_id}")
        
        return value
    
    def create(self, validated_data):
        """
        AnaVeri ve VeriDeger kayıtlarını oluştur
        """
        sutun_degerleri = validated_data.get('sutun_degerleri', {})
        
        # AnaVeri kaydını oluştur
        ana_veri = AnaVeri.objects.create()
        
        # Her sütun için VeriDeger oluştur
        for sutun_id, deger in sutun_degerleri.items():
            if deger:  # Boş değerleri kaydetme
                sutun = Sütun.objects.get(id=sutun_id)
                VeriDeger.objects.create(
                    ana_veri=ana_veri,
                    sutun=sutun,
                    deger=str(deger)
                )
        
        return ana_veri


class SütunCreateSerializer(serializers.ModelSerializer):
    """
    Sütun oluşturma için özel serializer
    """
    class Meta:
        model = Sütun
        fields = ['ad', 'sıra', 'aktif']
    
    def validate_ad(self, value):
        """
        Sütun adını validate et
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Sütun adı boş olamaz")
        
        # Aynı isimde başka sütun var mı kontrol et
        existing = Sütun.objects.filter(ad=value.strip())
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError(f'"{value}" adında bir sütun zaten mevcut')
        
        return value.strip()
    
    def validate_sıra(self, value):
        """
        Sıra numarasını validate et
        """
        if value < 0:
            raise serializers.ValidationError("Sıra numarası negatif olamaz")
        return value
