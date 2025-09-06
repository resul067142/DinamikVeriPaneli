from django.urls import path
from . import views

app_name = 'assistant'

urlpatterns = [
    path('ask/', views.AssistantAPIView.as_view(), name='ask'),
    path('transcribe/', views.TranscribeAudioView.as_view(), name='transcribe'),
    path('audio/<int:conversation_id>/', views.get_audio, name='get_audio'),
    path('audio-stream/<int:conversation_id>/', views.get_audio_stream, name='get_audio_stream'),
    path('', views.assistant_page, name='assistant_page'),
]