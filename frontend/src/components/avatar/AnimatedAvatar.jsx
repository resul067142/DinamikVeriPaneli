import React, { useState, useEffect, useRef } from 'react';
import Lottie from 'react-lottie';
import * as faceAnimationData from './face-animation.json'; // We'll create this file

const AnimatedAvatar = ({ isSpeaking = false, emotion = 'neutral' }) => {
  const [animationSpeed, setAnimationSpeed] = useState(1);
  const [currentAnimation, setCurrentAnimation] = useState('neutral');
  const audioAnalyserRef = useRef(null);
  const animationRef = useRef(null);

  // Animation configurations
  const animationConfig = {
    neutral: { speed: 0.5, loop: true },
    speaking: { speed: 1.5, loop: true },
    smiling: { speed: 1, loop: false },
    nodding: { speed: 0.8, loop: false },
    thinking: { speed: 0.3, loop: true }
  };

  // Update animation based on state
  useEffect(() => {
    if (isSpeaking) {
      setCurrentAnimation('speaking');
      setAnimationSpeed(animationConfig.speaking.speed);
    } else {
      setCurrentAnimation('neutral');
      setAnimationSpeed(animationConfig.neutral.speed);
    }
  }, [isSpeaking, emotion]);

  // Simulate lip sync based on audio (in a real implementation, this would connect to actual audio)
  useEffect(() => {
    if (isSpeaking) {
      const interval = setInterval(() => {
        // Randomize animation speed to simulate lip sync
        const randomSpeed = 0.8 + Math.random() * 1.2;
        setAnimationSpeed(randomSpeed);
      }, 200);

      return () => clearInterval(interval);
    }
  }, [isSpeaking]);

  // Lottie options
  const defaultOptions = {
    loop: animationConfig[currentAnimation]?.loop || true,
    autoplay: true,
    animationData: faceAnimationData,
    rendererSettings: {
      preserveAspectRatio: 'xMidYMid slice'
    }
  };

  return (
    <div className="relative w-48 h-48">
      <Lottie
        options={defaultOptions}
        height={192}
        width={192}
        speed={animationSpeed}
        isStopped={!isSpeaking && currentAnimation === 'neutral'}
      />
      
      {/* Emotion indicators */}
      {emotion === 'smiling' && (
        <div className="absolute top-4 right-4 w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center">
          <span className="text-xs">😊</span>
        </div>
      )}
      
      {emotion === 'thinking' && (
        <div className="absolute top-4 right-4 w-6 h-6 bg-blue-400 rounded-full flex items-center justify-center">
          <span className="text-xs">🤔</span>
        </div>
      )}
    </div>
  );
};

export default AnimatedAvatar;