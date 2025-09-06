import os
import json
import asyncio
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from .services.openai_service import OpenAIService
from .services.speech import SpeechService
from .models import AssistantConversation
import tempfile

@method_decorator(csrf_exempt, name='dispatch')
class AssistantAPIView(View):
    def post(self, request):
        try:
            # JSON verisini ayrıştır
            data = json.loads(request.body)
            question = data.get('question', '')
            use_elevenlabs = data.get('use_elevenlabs', True)  # Belirtilmemişse varsayılan olarak True
            stream_audio = data.get('stream_audio', False)  # Ses akışı
            user = request.user
            
            if not question:
                return JsonResponse({'error': 'Soru gerekli'}, status=400)
            
            # Servisleri başlat
            openai_service = OpenAIService()
            speech_service = SpeechService()
            
            # OpenAI kullanarak yanıt oluştur
            answer = openai_service.generate_response(user, question)
            
            # Konuşmayı kaydet
            conversation = AssistantConversation.objects.create(
                user=user,
                question=question,
                answer=answer
            )
            
            if stream_audio:
                # Akış için, konuşma ID'sini döndürecek ve istemcinin
                # ses akışını ayrı olarak istemesini sağlayacağız
                response_data = {
                    'answer': answer,
                    'conversation_id': conversation.id,
                    'audio_url': f'/assistant/audio-stream/{conversation.id}/'
                }
            else:
                # Ses dosyası oluştur
                audio_file_path = speech_service.text_to_speech(answer, use_elevenlabs=use_elevenlabs)
                
                # Yanıtı döndür
                response_data = {
                    'answer': answer,
                    'conversation_id': conversation.id,
                    'audio_url': f'/assistant/audio/{conversation.id}/' if audio_file_path else None
                }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class TranscribeAudioView(View):
    def post(self, request):
        try:
            # Ses dosyasının varlığını kontrol et
            if 'audio' not in request.FILES:
                return JsonResponse({'error': 'Ses dosyası bulunamadı'}, status=400)
            
            audio_file = request.FILES['audio']
            
            # Ses dosyasını geçici olarak kaydet
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_file:
                for chunk in audio_file.chunks():
                    tmp_file.write(chunk)
                temp_filename = tmp_file.name
            
            # Sesi metne dönüştür
            speech_service = SpeechService()
            transcribed_text = speech_service.speech_to_text(temp_filename)
            
            # Geçici dosyayı temizle
            os.unlink(temp_filename)
            
            if not transcribed_text:
                return JsonResponse({'error': 'Ses metne dönüştürülemedi'}, status=400)
            
            return JsonResponse({'text': transcribed_text})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_audio(request, conversation_id):
    """Bir konuşma için ses dosyasını sun"""
    try:
        conversation = AssistantConversation.objects.get(id=conversation_id, user=request.user)
        
        # Ses dosyası oluştur
        speech_service = SpeechService()
        audio_file_path = speech_service.text_to_speech(conversation.answer)
        
        if not audio_file_path or not os.path.exists(audio_file_path):
            return HttpResponse('Ses dosyası bulunamadı', status=404)
        
        # Dosyayı sun
        with open(audio_file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='audio/mpeg')
            response['Content-Disposition'] = f'inline; filename="response_{conversation_id}.mp3"'
            return response
            
    except AssistantConversation.DoesNotExist:
        return HttpResponse('Konuşma bulunamadı', status=404)
    except Exception as e:
        return HttpResponse(f'Hata: {str(e)}', status=500)

@login_required
def get_audio_stream(request, conversation_id):
    """Bir konuşma için ses akışı"""
    try:
        conversation = AssistantConversation.objects.get(id=conversation_id, user=request.user)
        
        # Ses akışı oluştur
        speech_service = SpeechService()
        
        # Bu örnekte, normal bir dosya yanıtı döndüreceğiz
        # Gerçek bir uygulamada, ses parçalarını akış yapardınız
        audio_file_path = speech_service.text_to_speech(conversation.answer)
        
        if not audio_file_path or not os.path.exists(audio_file_path):
            return HttpResponse('Ses dosyası bulunamadı', status=404)
        
        def generate():
            with open(audio_file_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    yield chunk
            # Akıştan sonra geçici dosyayı temizle
            try:
                os.unlink(audio_file_path)
            except:
                pass
        
        response = StreamingHttpResponse(generate(), content_type='audio/mpeg')
        response['Content-Disposition'] = f'inline; filename="response_{conversation_id}.mp3"'
        return response
            
    except AssistantConversation.DoesNotExist:
        return HttpResponse('Konuşma bulunamadı', status=404)
    except Exception as e:
        return HttpResponse(f'Hata: {str(e)}', status=500)

def assistant_page(request):
    """Asistan sayfasını oluştur"""
    return render(request, 'assistant/index.html')