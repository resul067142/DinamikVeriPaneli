# AI Assistant for Django Web Application

This document describes the implementation of an AI assistant for your Django web application with the following features:

## Features Implemented

1. **Web Interface with Human Avatar**
   - Animated avatar with lip sync during speech
   - Facial expressions (smiling, thinking, etc.)
   - Implemented using CSS animations and JavaScript

2. **Voice and Text Q&A Capabilities**
   - Speech-to-text using Google Speech Recognition
   - Text-to-speech using both gTTS and ElevenLabs API
   - Support for both voice and text input

3. **Django Backend Integration**
   - Integrated with existing Django data models
   - Custom API endpoint at `/assistant/ask/`
   - Conversation history storage

4. **React/Next.js Frontend**
   - React component for the assistant interface
   - Avatar animations with lip sync
   - Real-time chat interface

5. **Advanced Features**
   - Support for ElevenLabs API for more natural text-to-speech
   - Audio streaming capabilities
   - TTS engine selection (ElevenLabs vs gTTS)
   - Streaming vs. non-streaming audio playback

## File Structure

```
django_app/
  assistant/
    models.py          # Conversation and settings models
    views.py           # API endpoints
    urls.py            # URL routing
    services/
      openai_service.py # OpenAI integration
      speech.py         # Speech-to-text and text-to-speech

frontend/
  src/
    components/
      Assistant.jsx     # Main React component
      avatar/
        AnimatedAvatar.jsx     # Avatar component with animations
        face-animation.json    # Lottie animation data

templates/
  assistant/
    index.html         # Django template version
```

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements_assistant.txt
   cd frontend && npm install
   ```

2. **Environment Variables**
   - Set `OPENAI_API_KEY` for OpenAI integration
   - Set `ELEVENLABS_API_KEY` for ElevenLabs TTS (optional)

3. **Run Django Server**
   ```bash
   python manage.py runserver
   ```

4. **Access the Assistant**
   - Visit `http://127.0.0.1:8000/assistant/` for the Django template version
   - Integrate the React component in your frontend application

## API Endpoints

- `POST /assistant/ask/` - Ask a question to the AI assistant
- `POST /assistant/transcribe/` - Transcribe audio to text
- `GET /assistant/audio/<conversation_id>/` - Get audio for a conversation
- `GET /assistant/audio-stream/<conversation_id>/` - Stream audio for a conversation

## Usage

1. Users can interact with the assistant via text input or voice recording
2. The assistant uses OpenAI to generate responses based on your Django data
3. Responses are converted to speech using either gTTS or ElevenLabs
4. The avatar animates during speech with lip sync and facial expressions
5. Conversation history is stored in the database

## Customization

- Modify the avatar animations in `frontend/src/components/avatar/face-animation.json`
- Adjust the OpenAI prompt in `assistant/services/openai_service.py`
- Change the ElevenLabs voice settings in `assistant/services/speech.py`
- Customize the UI in either the React component or Django template

## Requirements

- Django 4.2+
- Python 3.8+
- OpenAI API key
- ElevenLabs API key (optional, for premium TTS)
- Node.js and npm for React frontend