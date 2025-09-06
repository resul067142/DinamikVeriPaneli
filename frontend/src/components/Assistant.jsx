import React, { useState, useRef, useEffect } from 'react';
import AnimatedAvatar from './avatar/AnimatedAvatar';

const Assistant = () => {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [emotion, setEmotion] = useState('neutral');
  const [userInput, setUserInput] = useState('');
  const [conversation, setConversation] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [useElevenLabs, setUseElevenLabs] = useState(true); // Default to ElevenLabs
  const [streamAudio, setStreamAudio] = useState(false); // Whether to stream audio
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const chatContainerRef = useRef(null);
  const audioRef = useRef(null);

  // Scroll to bottom of chat when new messages are added
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [conversation]);

  // Welcome message
  useEffect(() => {
    const welcomeMessage = {
      id: Date.now(),
      sender: 'assistant',
      text: 'Merhaba! Size nasıl yardımcı olabilirim?',
      timestamp: new Date()
    };
    setConversation([welcomeMessage]);
  }, []);

  const toggleTTS = () => {
    setUseElevenLabs(!useElevenLabs);
  };

  const toggleStreaming = () => {
    setStreamAudio(!streamAudio);
  };

  const toggleMicrophone = async () => {
    if (!isListening) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorderRef.current = new MediaRecorder(stream);
        audioChunksRef.current = [];

        mediaRecorderRef.current.ondataavailable = (event) => {
          audioChunksRef.current.push(event.data);
        };

        mediaRecorderRef.current.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          await sendAudioToBackend(audioBlob);
          stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorderRef.current.start();
        setIsListening(true);
        setEmotion('speaking');
      } catch (error) {
        console.error('Microphone access error:', error);
        alert('Microphone access error: ' + error.message);
      }
    } else {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
      setIsListening(false);
      setEmotion('neutral');
    }
  };

  const sendAudioToBackend = async (audioBlob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    
    try {
      const response = await fetch('/assistant/transcribe/', {
        method: 'POST',
        body: formData,
        credentials: 'include',
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        }
      });
      
      const data = await response.json();
      
      if (data.text) {
        setUserInput(data.text);
        await sendQuestion(data.text);
      } else {
        addAssistantMessage('Could not understand your voice. Please try again.');
      }
    } catch (error) {
      console.error('Error sending audio:', error);
      addAssistantMessage('Error processing audio: ' + error.message);
    }
  };

  // Helper function to get CSRF token
  const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  };

  const addUserMessage = (text) => {
    const newMessage = {
      id: Date.now(),
      sender: 'user',
      text: text,
      timestamp: new Date()
    };
    setConversation(prev => [...prev, newMessage]);
  };

  const addAssistantMessage = (text) => {
    const newMessage = {
      id: Date.now(),
      sender: 'assistant',
      text: text,
      timestamp: new Date()
    };
    setConversation(prev => [...prev, newMessage]);
  };

  const sendQuestion = async (questionText = null) => {
    const textToSend = questionText || userInput.trim();
    
    if (!textToSend) return;

    // Add user message to conversation
    addUserMessage(textToSend);
    setUserInput('');
    setIsLoading(true);
    setIsListening(false);
    setEmotion('thinking');

    try {
      const response = await fetch('/assistant/ask/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        credentials: 'include',
        body: JSON.stringify({ 
          question: textToSend,
          use_elevenlabs: useElevenLabs,
          stream_audio: streamAudio
        })
      });

      const data = await response.json();
      
      if (data.error) {
        addAssistantMessage('Error: ' + data.error);
        setEmotion('neutral');
        return;
      }
      
      // Add assistant response
      addAssistantMessage(data.answer);
      
      // Play audio if available
      if (data.audio_url) {
        if (streamAudio) {
          // Stream audio
          setIsSpeaking(true);
          setEmotion('speaking');
          
          // Create audio element for streaming
          if (audioRef.current) {
            audioRef.current.pause();
          }
          
          audioRef.current = new Audio(data.audio_url);
          audioRef.current.onended = () => {
            setIsSpeaking(false);
            setEmotion('smiling');
            setTimeout(() => setEmotion('neutral'), 2000);
          };
          
          try {
            await audioRef.current.play();
          } catch (e) {
            console.error('Audio play error:', e);
            setIsSpeaking(false);
            setEmotion('neutral');
          }
        } else {
          // Regular audio playback
          setIsSpeaking(true);
          setEmotion('speaking');
          
          const audio = new Audio(data.audio_url);
          audio.onended = () => {
            setIsSpeaking(false);
            setEmotion('smiling');
            setTimeout(() => setEmotion('neutral'), 2000);
          };
          audio.play().catch(e => {
            console.error('Audio play error:', e);
            setIsSpeaking(false);
            setEmotion('neutral');
          });
        }
      } else {
        setEmotion('smiling');
        setTimeout(() => setEmotion('neutral'), 2000);
      }
      
    } catch (error) {
      console.error('Error sending question:', error);
      addAssistantMessage('Üzgünüm, şu anda yardımcı olamıyorum. Lütfen daha sonra tekrar deneyin.');
      setEmotion('neutral');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendQuestion();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="card bg-white shadow-xl rounded-2xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-500 to-indigo-600 p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold">AI Assistant</h1>
                <p className="opacity-90">How can I help you today?</p>
              </div>
              <div className="avatar">
                <div className="w-16 rounded-full bg-white/20 flex items-center justify-center">
                  <span className="text-2xl">🤖</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Avatar Section */}
          <div className="p-6 bg-gradient-to-r from-indigo-50 to-purple-50 flex flex-col items-center">
            <div className="relative">
              {/* Animated Avatar */}
              <AnimatedAvatar isSpeaking={isSpeaking} emotion={emotion} />
              
              {/* Microphone Indicator */}
              {isListening && (
                <div className="absolute -bottom-2 -right-2 w-12 h-12 bg-red-500 rounded-full flex items-center justify-center text-white shadow-lg animate-pulse">
                  <span className="text-xl">🎤</span>
                </div>
              )}
            </div>
            
            <div className="mt-4 text-center">
              <h2 className="text-xl font-semibold text-gray-800">AI Assistant</h2>
              <p className="text-gray-600">Ask me anything about your data</p>
            </div>
          </div>
          
          {/* Chat Container */}
          <div className="p-6">
            <div 
              ref={chatContainerRef}
              className="space-y-4 h-96 overflow-y-auto mb-6 bg-gray-50 rounded-xl p-4"
            >
              {conversation.map((message) => (
                <div 
                  key={message.id} 
                  className={`chat ${message.sender === 'user' ? 'chat-end' : 'chat-start'}`}
                >
                  <div className="chat-image avatar">
                    <div className={`w-10 rounded-full flex items-center justify-center text-white ${
                      message.sender === 'user' ? 'bg-blue-500' : 'bg-purple-500'
                    }`}>
                      {message.sender === 'user' ? '👤' : '🤖'}
                    </div>
                  </div>
                  <div className="chat-header mb-1">
                    {message.sender === 'user' ? 'You' : 'Assistant'}
                    <time className="text-xs opacity-50 ml-2">
                      {message.timestamp.toLocaleTimeString()}
                    </time>
                  </div>
                  <div className={`chat-bubble ${
                    message.sender === 'user' 
                      ? 'bg-blue-100 text-blue-800' 
                      : 'bg-purple-100 text-purple-800'
                  }`}>
                    {message.text}
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="chat chat-start">
                  <div className="chat-image avatar">
                    <div className="w-10 rounded-full bg-purple-500 flex items-center justify-center text-white">
                      🤖
                    </div>
                  </div>
                  <div className="chat-bubble bg-purple-100 text-purple-800">
                    <span className="loading loading-dots loading-sm"></span>
                  </div>
                </div>
              )}
            </div>
            
            {/* Input Area */}
            <div className="flex gap-2 flex-wrap">
              <div className="flex-1 relative min-w-[200px]">
                <input 
                  type="text" 
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your question here or use voice input..."
                  className="input input-bordered w-full pr-12"
                  disabled={isLoading}
                />
                <button 
                  onClick={toggleMicrophone}
                  className={`btn btn-circle absolute right-2 top-1/2 transform -translate-y-1/2 border-none ${
                    isListening 
                      ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                      : 'bg-blue-500 hover:bg-blue-600'
                  }`}
                >
                  <span className="text-lg">{isListening ? 'stop' : 'mic'}</span>
                </button>
              </div>
              <button 
                onClick={toggleTTS}
                className="btn btn-secondary"
              >
                <span className="mr-2">{useElevenLabs ? '🎤' : '🔊'}</span> 
                {useElevenLabs ? 'ElevenLabs' : 'gTTS'}
              </button>
              <button 
                onClick={toggleStreaming}
                className={`btn ${streamAudio ? 'btn-success' : 'btn-info'}`}
              >
                <span className="mr-2">📡</span> 
                {streamAudio ? 'Streaming ON' : 'Streaming OFF'}
              </button>
              <button 
                onClick={() => sendQuestion()}
                className="btn btn-primary"
                disabled={isLoading || !userInput.trim()}
              >
                {isLoading ? (
                  <span className="loading loading-spinner"></span>
                ) : (
                  <>
                    <span className="mr-2">📤</span> Send
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Assistant;