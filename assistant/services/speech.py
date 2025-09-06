import os
import tempfile
import asyncio
from django.conf import settings
from gtts import gTTS
import speech_recognition as sr
from elevenlabs import ElevenLabs, play
from elevenlabs.client import ElevenLabs as ElevenLabsClient

class SpeechService:
    def __init__(self):
        # ElevenLabs API anahtarını başlat
        self.elevenlabs_api_key = os.environ.get('ELEVENLABS_API_KEY', '')
        if self.elevenlabs_api_key:
            self.elevenlabs_client = ElevenLabsClient(api_key=self.elevenlabs_api_key)
        else:
            self.elevenlabs_client = None
    
    def text_to_speech(self, text, language='tr', use_elevenlabs=True):
        """
        Metni sese dönüştür ve geçici dosyaya kaydet
        Ses dosyasının yolunu döndürür
        """
        try:
            # ElevenLabs kullanılabilirse ve use_elevenlabs True ise önce onu dene
            if self.elevenlabs_client and use_elevenlabs:
                try:
                    # ElevenLabs ile ses oluştur
                    audio = self.elevenlabs_client.generate(
                        text=text,
                        voice="Rachel",  # İstediğiniz sesle değiştirebilirsiniz
                        model="eleven_multilingual_v2"
                    )
                    
                    # Geçici dosyaya kaydet
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                    temp_filename = temp_file.name
                    temp_file.close()
                    
                    # Ses dosyasını kaydet
                    with open(temp_filename, 'wb') as f:
                        for chunk in audio:
                            f.write(chunk)
                    
                    return temp_filename
                except Exception as e:
                    print(f"ElevenLabs TTS hatası: {e}")
                    # gTTS'e geri dön
                    pass
            
            # gTTS'e geri dön
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_filename = temp_file.name
            temp_file.close()
            
            # gTTS ile ses oluştur
            tts = gTTS(text=text, lang=language, slow=False, lang_check=False)
            tts.save(temp_filename)
            
            return temp_filename
        except Exception as e:
            print(f"Metinden-sese dönüştürme hatası: {e}")
            return None
    
    async def text_to_speech_stream(self, text, use_elevenlabs=True):
        """
        Metni sese dönüştür ve akış yanıtı döndür
        """
        try:
            # ElevenLabs kullanılabilirse ve use_elevenlabs True ise önce onu dene
            if self.elevenlabs_client and use_elevenlabs:
                try:
                    # ElevenLabs ile ses oluştur (akış modu)
                    audio_stream = self.elevenlabs_client.generate(
                        text=text,
                        voice="Rachel",
                        model="eleven_multilingual_v2",
                        stream=True
                    )
                    return audio_stream
                except Exception as e:
                    print(f"ElevenLabs TTS akış hatası: {e}")
                    # gTTS'e geri dön
                    pass
            
            # Geri dönüş - gTTS için hala tam ses oluşturmak gerekiyor
            # Gerçek bir uygulamada farklı bir akış TTS hizmeti kullanmak isteyebilirsiniz
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_filename = temp_file.name
            temp_file.close()
            
            # gTTS ile ses oluştur
            tts = gTTS(text=text, lang='tr', slow=False, lang_check=False)
            tts.save(temp_filename)
            
            # Şimdilik dosya yolunu döndür
            return temp_filename
        except Exception as e:
            print(f"Metinden-sese dönüştürme akış hatası: {e}")
            return None
    
    def speech_to_text(self, audio_file_path, language='tr-TR'):
        """
        Sesi metne dönüştür
        """
        try:
            recognizer = sr.Recognizer()
            
            # Farklı ses formatlarını dene
            try:
                with sr.AudioFile(audio_file_path) as source:
                    # Ortam gürültüsüne göre ayarla
                    recognizer.adjust_for_ambient_noise(source)
                    audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data, language=language)
                    return text
            except sr.UnknownValueError:
                print("Google Konuşma Tanıma sesi anlayamadı")
                return None
            except sr.RequestError as e:
                print(f"Google Konuşma Tanıma hizmetinden sonuç alınamadı; {e}")
                return None
            except Exception as e:
                # Farklı parametrelerle tekrar dene
                try:
                    with sr.AudioFile(audio_file_path) as source:
                        audio_data = recognizer.record(source)
                        text = recognizer.recognize_google_cloud(audio_data, language=language)
                        return text
                except Exception as e2:
                    print(f"Sesten-metne dönüştürme hatası: {e}")
                    return None
        except Exception as e:
            print(f"Sesten-metne dönüştürme hatası: {e}")
            return None