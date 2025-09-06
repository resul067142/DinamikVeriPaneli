import openai
import os
import random
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Count, Sum
from veri_yonetimi.models import AnaVeri  # Adjust import based on your actual models

class OpenAIService:
    def __init__(self):
        # Initialize OpenAI API key
        self.api_key = getattr(settings, 'OPENAI_API_KEY', '') or os.environ.get('OPENAI_API_KEY', '')
        if self.api_key and self.api_key != 'your-openai-api-key-here':
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None
        
    def get_context_data(self, user):
        """Kullanıcı için ilgili bağlam verilerini al"""
        context = {
            "user_info": {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
            }
        }
        
        # Kullanıcının il atamaları varsa il verilerini ekle
        if hasattr(user, 'profile'):
            profile = user.profile
            context["user_profile"] = {
                "tc_kimlik": profile.tc_kimlik,
                "sorumlu_iller": profile.get_sorumlu_iller_list(),
            }
            
            # Kullanıcının il atamaları varsa ilgili verileri al
            if profile.sorumlu_iller:
                provinces = profile.get_sorumlu_iller_list()
                province_data = AnaVeri.objects.filter(il_adi__in=provinces)
                context["province_data"] = [
                    {
                        "il_adi": data.il_adi,
                        "kurulacak_cihaz_sayisi": data.kurulacak_cihaz_sayisi,
                        "kurulan_cihaz_sayisi": data.kurulan_cihaz_sayisi,
                        "arizali_cihaz_sayisi": data.arizali_cihaz_sayisi,
                        "tamamlanma_yuzdesi": data.tamamlanma_yuzdesi,
                    }
                    for data in province_data
                ]
            else:
                # İl ataması yoksa tüm verileri al
                all_data = AnaVeri.objects.all()
                context["province_data"] = [
                    {
                        "il_adi": data.il_adi,
                        "kurulacak_cihaz_sayisi": data.kurulacak_cihaz_sayisi,
                        "kurulan_cihaz_sayisi": data.kurulan_cihaz_sayisi,
                        "arizali_cihaz_sayisi": data.arizali_cihaz_sayisi,
                        "tamamlanma_yuzdesi": data.tamamlanma_yuzdesi,
                    }
                    for data in all_data
                ]
        
        return context
    
    def generate_fallback_response(self, user, question):
        """API anahtarı olmadan çalışan geliştirilmiş yanıt oluşturucu"""
        context = self.get_context_data(user)
        
        # Basit kurallar tabanlı yanıt sistemi
        question_lower = question.lower().strip()
        
        # Selamlama
        if any(greeting in question_lower for greeting in ["merhaba", "selam", "günaydın", "iyi akşamlar", "hey"]):
            name = user.first_name or user.username
            responses = [
                f"Merhaba {name}! 😊 Size bugün nasıl yardımcı olabilirim?",
                f"Selam {name}! Sistemle ilgili ne öğrenmek istiyorsunuz? 🤔",
                f"Merhaba {name}! Veri yönetimi sistemi hakkında sorularınızı yanıtlayabilirim. Ne bilmek istersiniz?"
            ]
            return random.choice(responses)
        
        # Yardım isteği
        elif any(help_word in question_lower for help_word in ["yardım", "yardim", "ne yapabilirsin", "neler yapabilirsin", "yardımcı ol", "yardimci ol"]):
            return ("Size aşağıdaki konularda yardımcı olabilirim:\n\n"
                   "📊 Sistem İstatistikleri:\n"
                   "  • Toplam veri ve kullanıcı sayıları\n"
                   "  • İl bazında tamamlanma oranları\n"
                   "  • Cihaz dağılım istatistikleri\n\n"
                   "📈 Detaylı Bilgiler:\n"
                   "  • Belirli iller hakkında bilgiler\n"
                   "  • En iyi ve en düşük performanslı iller\n"
                   "  • Ortalama tamamlanma oranları\n\n"
                   "Sorularınızı doğal dilde, Türkçe olarak sorabilirsiniz. Örneğin 'İstanbul hakkında ne biliyorsun?' gibi. 🙌")
        
        # Teşekkür
        elif any(thanks in question_lower for thanks in ["teşekkür", "tesekkur", "sağol", "saol", "thanks"]):
            responses = [
                "Rica ederim! Başka bir şey öğrenmek ister misiniz? 😊",
                "Memnuniyetle! Yardımcı olmamı istediğiniz başka bir konu var mı? 🤗",
                "Ne demek! Sistem hakkında daha fazla bilgi almak isterseniz sormaktan çekinmeyin! 🙌"
            ]
            return random.choice(responses)
        
        # Toplam veri sayısı
        elif any(word in question_lower for word in ["toplam", "veri", "kayıt", "sayı"]) and \
             any(word in question_lower for word in ["veri", "kayıt", "adet", "sayı", "kaç"]):
            total_data = AnaVeri.objects.count()
            responses = [
                f"Sistemde şu anda toplam {total_data} adet il verisi kayıtlı. 📊 Bu veriler tüm Türkiye illerini kapsıyor.",
                f"Veritabanımızda {total_data} farklı il için detaylı veri bulunuyor. Her il için cihaz kurulum bilgileri mevcut. 🗂️",
                f"Toplam {total_data} il verisine sahibiz. Bu veriler sistemde düzenli olarak güncelleniyor. 🔄"
            ]
            return random.choice(responses)
        
        # İl sayısı
        elif any(word in question_lower for word in ["il", "şehir", "sehir"]) and \
             any(word in question_lower for word in ["sayı", "adet", "kaç"]):
            total_provinces = AnaVeri.objects.count()
            responses = [
                f"Sistemde toplam {total_provinces} il için veri bulunmaktadır. 🇹🇷 Türkiye'nin tüm illeri bu veritabanında mevcut.",
                f"Veritabanımızda {total_provinces} farklı il kaydı var. Her il için ayrıntılı istatistikler oluşturabiliyoruz. 📈",
                f"Toplam {total_provinces} il verisine erişebiliyorum. Bu veriler gerçek zamanlı olarak güncelleniyor. ⚡"
            ]
            return random.choice(responses)
        
        # Kullanıcı sayısı
        elif any(word in question_lower for word in ["kullanıcı", "user", "kisi", "kişi"]) and \
             any(word in question_lower for word in ["sayı", "adet", "kaç"]):
            total_users = User.objects.count()
            responses = [
                f"Sistemde şu anda toplam {total_users} kullanıcı kayıtlı. 👥 Bu kullanıcılar farklı yetkilerle sisteme erişiyor.",
                f"Toplam {total_users} kullanıcı hesabı oluşturulmuş. Kullanıcılar sisteme giriş yaparak verilere erişebiliyor. 🔐",
                f"Veritabanında {total_users} farklı kullanıcı kaydı bulunuyor. Her kullanıcının kendine özel erişim yetkileri var. 🛡️"
            ]
            return random.choice(responses)
        
        # Ortalama tamamlanma oranı
        elif any(word in question_lower for word in ["ortalama", "avg", "average"]) and \
             any(word in question_lower for word in ["tamamlanma", "oran", "yüzde", "yuzde"]):
            avg_completion = AnaVeri.objects.aggregate(Avg('tamamlanma_yuzdesi'))['tamamlanma_yuzdesi__avg']
            if avg_completion is not None:
                responses = [
                    f"Sistem genelinde ortalama tamamlanma oranı %{avg_completion:.2f}. 📊 Bu oran tüm iller için hesaplanan ortalama değeri gösteriyor.",
                    f"Tüm iller bazında ortalama tamamlanma oranımız %{avg_completion:.2f}. 🎯 Bu değer sistem performansını gösteren önemli bir metrik.",
                    f"Genel ortalama tamamlanma yüzdesi %{avg_completion:.2f}. 📈 Bu oran zamanla değişen dinamik bir değerdir."
                ]
                return random.choice(responses)
            else:
                return "Sistemde henüz tamamlanma oranı verisi bulunmamaktadır. 📉"
        
        # En yüksek tamamlanma oranı
        elif any(word in question_lower for word in ["yüksek", "en yüksek", "max", "fazla", "iyi", "başarılı", "başarili"]) and \
             any(word in question_lower for word in ["tamamlanma", "oran", "yüzde", "yuzde"]):
            top_provinces = AnaVeri.objects.order_by('-tamamlanma_yuzdesi')[:5]
            if top_provinces:
                response = "🏆 En yüksek tamamlanma oranına sahip illerimiz:\n\n"
                for i, province in enumerate(top_provinces, 1):
                    if i == 1:
                        response += f"🥇 {i}. {province.il_adi}: %{province.tamamlanma_yuzdesi:.2f} (En iyi performans! 🌟)\n"
                    elif i == 2:
                        response += f"🥈 {i}. {province.il_adi}: %{province.tamamlanma_yuzdesi:.2f}\n"
                    elif i == 3:
                        response += f"🥉 {i}. {province.il_adi}: %{province.tamamlanma_yuzdesi:.2f}\n"
                    else:
                        response += f"  {i}. {province.il_adi}: %{province.tamamlanma_yuzdesi:.2f}\n"
                return response
            else:
                return "Sistemde henüz tamamlanma oranı verisi bulunmamaktadır. 📉"
        
        # En düşük tamamlanma oranı
        elif any(word in question_lower for word in ["düşük", "en düşük", "min", "az", "kötü", "zayıf", "zayif"]) and \
             any(word in question_lower for word in ["tamamlanma", "oran", "yüzde", "yuzde"]):
            low_provinces = AnaVeri.objects.order_by('tamamlanma_yuzdesi')[:5]
            if low_provinces:
                response = "📊 Gelişime açık illerimiz (En düşük tamamlanma oranları):\n\n"
                for i, province in enumerate(low_provinces, 1):
                    response += f"  {i}. {province.il_adi}: %{province.tamamlanma_yuzdesi:.2f}\n"
                response += "\nBu illerde daha fazla çalışma yapılması gerekebilir. 💪"
                return response
            else:
                return "Sistemde henüz tamamlanma oranı verisi bulunmamaktadır. 📉"
        
        # Belirli bir il hakkında bilgi
        elif any(city in question_lower for city in ["istanbul", "ankara", "izmir", "antalya", "bursa", "adana", "konya", "izmit", "mersin", "samsun"]):
            # Örnek olarak birkaç büyük şehir
            city_mapping = {
                "istanbul": "İstanbul",
                "ankara": "Ankara",
                "izmir": "İzmir",
                "antalya": "Antalya",
                "bursa": "Bursa",
                "adana": "Adana",
                "konya": "Konya",
                "izmit": "Kocaeli",
                "mersin": "Mersin",
                "samsun": "Samsun"
            }
            
            for key, city_name in city_mapping.items():
                if key in question_lower:
                    province_data = AnaVeri.objects.filter(il_adi=city_name).first()
                    if province_data:
                        responses = [
                            f"📍 {city_name} ili için detaylı bilgiler:\n\n"
                            f"🔧 Kurulacak Cihaz: {province_data.kurulacak_cihaz_sayisi}\n"
                            f"✅ Kurulan Cihaz: {province_data.kurulan_cihaz_sayisi}\n"
                            f"⚠️ Arızalı Cihaz: {province_data.arizali_cihaz_sayisi}\n"
                            f"📈 Tamamlanma Oranı: %{province_data.tamamlanma_yuzdesi:.2f}",
                            
                            f"📊 {city_name} ile ilgili güncel veriler:\n\n"
                            f"• Toplam cihaz hedefi: {province_data.kurulacak_cihaz_sayisi}\n"
                            f"• Kurulan cihaz sayısı: {province_data.kurulan_cihaz_sayisi}\n"
                            f"• Arızalı cihazlar: {province_data.arizali_cihaz_sayisi}\n"
                            f"• İlerleme durumu: %{province_data.tamamlanma_yuzdesi:.2f} tamamlandı",
                            
                            f"📈 {city_name} ili performansı:\n\n"
                            f"Kurulum hedefi: {province_data.kurulacak_cihaz_sayisi} cihaz\n"
                            f"Tamamlanan: {province_data.kurulan_cihaz_sayisi} cihaz\n"
                            f"Arızalı: {province_data.arizali_cihaz_sayisi} cihaz\n"
                            f"Tamamlanma yüzdesi: %{province_data.tamamlanma_yuzdesi:.2f}"
                        ]
                        return random.choice(responses)
                    else:
                        return f"😔 {city_name} ili için sistemde veri bulunamadı."
        
        # Cihaz istatistikleri
        elif any(word in question_lower for word in ["cihaz", "device"]) and \
             any(word in question_lower for word in ["toplam", "sayı", "adet", "kaç"]):
            total_devices = AnaVeri.objects.aggregate(
                total_kurulacak=Sum('kurulacak_cihaz_sayisi'),
                total_kurulan=Sum('kurulan_cihaz_sayisi'),
                total_arizali=Sum('arizali_cihaz_sayisi')
            )
            if total_devices['total_kurulacak'] is not None:
                completion_rate = (total_devices['total_kurulan'] / total_devices['total_kurulacak'] * 100) if total_devices['total_kurulacak'] > 0 else 0
                responses = [
                    f"🔧 Sistem genelinde cihaz istatistikleri:\n\n"
                    f"🎯 Toplam kurulacak cihaz: {total_devices['total_kurulacak']}\n"
                    f"✅ Toplam kurulan cihaz: {total_devices['total_kurulan']}\n"
                    f"⚠️ Toplam arızalı cihaz: {total_devices['total_arizali']}\n"
                    f"📊 Kurulum oranı: %{completion_rate:.2f}",
                    
                    f"📈 Genel cihaz dağılımı:\n\n"
                    f"• Planlanan kurulum: {total_devices['total_kurulacak']} cihaz\n"
                    f"• Gerçekleştirilen kurulum: {total_devices['total_kurulan']} cihaz\n"
                    f"• Arızalı cihaz sayısı: {total_devices['total_arizali']} adet\n"
                    f"• Başarı oranı: %{completion_rate:.2f}"
                ]
                return random.choice(responses)
            else:
                return "😔 Sistemde henüz cihaz verisi bulunmamaktadır."
        
        # Rastgele genel sorular
        elif any(word in question_lower for word in ["sen", "siz", "asistan", "yardımcı"]) and \
             any(word in question_lower for word in ["kim", "ne", "nedir", "neden", "nasıl", "nasıl çalışıyorsun"]):
            responses = [
                "Ben AI Asistan'ım! 🤖 Sisteminizdeki veriler hakkında size yardımcı olabiliyorum. "
                "İl verileri, kullanıcı istatistikleri, cihaz dağılımları ve daha fazlası hakkında sorularınızı yanıtlayabilirim.\n\n"
                "Örneğin şunları sorabilirsiniz:\n"
                "• 'İstanbul hakkında ne biliyorsun?'\n"
                "• 'En iyi performans gösteren iller hangileri?'\n"
                "• 'Sistemde kaç kullanıcı var?'\n\n"
                "Size nasıl yardımcı olabilirim? 🤗",
                
                "Merhaba! Ben veri yönetimi sistemlerinde çalışan bir AI asistanıyım. 📊\n\n"
                "Size şu konularda yardımcı olabilirim:\n"
                "🔍 İstatistiksel Bilgiler: Toplam veri sayıları, kullanıcı istatistikleri\n"
                "🏙️ İl Bazlı Detaylar: Belirli iller hakkında bilgiler\n"
                "📈 Performans Metrikleri: Tamamlanma oranları, cihaz dağılımları\n\n"
                "Sorularınızı doğal şekilde, günlük konuşma dilinde sorabilirsiniz. Size nasıl yardımcı olabilirim? 😊"
            ]
            return random.choice(responses)
        
        # Varsayılan yanıt
        else:
            responses = [
                "🤔 Sisteminizdeki veriler hakkında sorular sorabilirsiniz. Size nasıl yardımcı olabilirim?\n\n"
                "Örnek sorular:\n"
                "• 'Toplam veri sayısı kaç?'\n"
                "• 'En yüksek tamamlanma oranına sahip iller hangileri?'\n"
                "• 'İstanbul ili hakkında bilgi ver'\n"
                "• 'Ortalama tamamlanma oranı nedir?'\n"
                "• 'Sistemde kaç kullanıcı var?'\n\n"
                "Sorularınızı doğal dilde, Türkçe olarak sorabilirsiniz. 🙌",
                
                "👋 Veri yönetimi sisteminiz hakkında size nasıl yardımcı olabilirim?\n\n"
                "Size yardımcı olabileceğim konular:\n"
                "🔍 İstatistiksel Bilgiler:\n"
                "  - Toplam veri ve kullanıcı sayıları\n"
                "  - İl bazında tamamlanma oranları\n"
                "  - Cihaz dağılım istatistikleri\n\n"
                "🏙️ İl Bazlı Detaylar:\n"
                "  - Belirli iller hakkında bilgiler\n"
                "  - En iyi ve gelişime açık iller\n"
                "  - Detaylı cihaz sayıları\n\n"
                "Sorularınızı doğal şekilde, günlük konuşma dilinde sorabilirsiniz. 😊",
                
                "✨ Size aşağıdaki örnek sorularla yardımcı olabilirim:\n\n"
                "📊 Genel İstatistikler:\n"
                "  • 'Sistemde kaç kullanıcı var?'\n"
                "  • 'Toplam veri sayısı kaç?'\n\n"
                "📍 İl Bazlı Bilgiler:\n"
                "  • 'Ankara ili hakkında bilgi'\n"
                "  • 'İstanbul ne durumda?'\n\n"
                "📈 Performans Metrikleri:\n"
                "  • 'En iyi iller hangileri?'\n"
                "  • 'Ortalama tamamlanma oranı nedir?'\n\n"
                "Sorularınızı rahatça Türkçe olarak sorabilirsiniz. 🤗"
            ]
            return random.choice(responses)
    
    def generate_response(self, user, question):
        """OpenAI kullanarak bir yanıt oluştur"""
        # API key kontrolü
        if not self.client:
            # API anahtarı yoksa fallback yanıt oluşturucuyu kullan
            return self.generate_fallback_response(user, question)
        
        # Bağlam verilerini al
        context = self.get_context_data(user)
        
        # Bağlam içeren sistem istemi oluştur
        system_prompt = f"""
        Veri yönetim sistemi için bir AI asistansınız.
        Aşağıdaki kullanıcı ve veri bilgilerine erişiminiz var:
        
        Kullanıcı Bilgisi: {context['user_info']}
        
        {f"Kullanıcı Profili: {context.get('user_profile', {})}" if 'user_profile' in context else ""}
        
        İl Verileri: {context['province_data'][:5]}  # İlk 5 veri ile sınırlı
        
        Lütfen bu bilgilere dayanarak yardımcı ve doğru yanıtlar verin.
        Belirli veriler sorulursa, sayısal bilgiler ve içgörüler sağlayın.
        Her zaman kibar ve profesyonel olun.
        Yanıtlarınızı Türkçe olarak verin.
        Kullanıcı dostu, doğal ve samimi bir dil kullanın.
        Yanıtlarınız robotik değil, insan gibi doğal olmalıdır.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # veya erişiminiz varsa gpt-4
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except openai.AuthenticationError:
            # Kimlik doğrulama hatası durumunda fallback kullan
            return self.generate_fallback_response(user, question)
        except Exception as e:
            # Diğer hatalar durumunda fallback kullan
            return self.generate_fallback_response(user, question)