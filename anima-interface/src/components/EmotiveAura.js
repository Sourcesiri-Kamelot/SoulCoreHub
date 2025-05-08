import React, { useContext, useEffect, useRef } from 'react';
import { AnimaContext } from '../contexts/AnimaContext';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';
import { emotionApi } from '../services/apiService';
import websocketService from '../services/websocketService';

const AuraContainer = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
`;

const AuraRing = styled(motion.div)`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  opacity: 0.15;
  mix-blend-mode: screen;
  filter: blur(30px);
`;

const AuraCore = styled(motion.div)`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  width: 30%;
  height: 30%;
  opacity: 0.2;
  mix-blend-mode: screen;
  filter: blur(20px);
`;

const AuraParticles = styled.canvas`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0.5;
`;

const EmotiveAura = () => {
  const { emotionalState, emotionProfiles } = useContext(AnimaContext);
  const particlesRef = useRef(null);
  const animationRef = useRef(null);
  
  // Get current emotion profile
  const emotion = emotionProfiles[emotionalState] || emotionProfiles.neutral;
  
  // Listen for emotional state changes via WebSocket
  useEffect(() => {
    // Connect to WebSocket if not already connected
    websocketService.connect().catch(error => {
      console.error('Failed to connect to WebSocket:', error);
    });
    
    // Listen for emotional state changes
    const handleEmotionalStateChange = (data) => {
      if (data.state) {
        changeEmotionalState(data.state);
      }
    };
    
    websocketService.on('emotional_state_change', handleEmotionalStateChange);
    
    // Clean up listener when component unmounts
    return () => {
      websocketService.off('emotional_state_change', handleEmotionalStateChange);
    };
  }, []);
  
  // Animation variants for the aura rings
  const ringVariants = {
    initial: {
      width: '60%',
      height: '60%',
      opacity: 0
    },
    animate: {
      width: ['60%', '70%', '65%'],
      height: ['60%', '70%', '65%'],
      opacity: [0.1, 0.2, 0.15],
      transition: {
        duration: 8,
        repeat: Infinity,
        repeatType: 'reverse',
        ease: 'easeInOut'
      }
    }
  };
  
  const outerRingVariants = {
    initial: {
      width: '80%',
      height: '80%',
      opacity: 0
    },
    animate: {
      width: ['80%', '90%', '85%'],
      height: ['80%', '90%', '85%'],
      opacity: [0.05, 0.1, 0.07],
      transition: {
        duration: 10,
        repeat: Infinity,
        repeatType: 'reverse',
        ease: 'easeInOut'
      }
    }
  };
  
  const coreVariants = {
    initial: {
      width: '30%',
      height: '30%',
      opacity: 0
    },
    animate: {
      width: ['30%', '35%', '28%'],
      height: ['30%', '35%', '28%'],
      opacity: [0.2, 0.3, 0.15],
      transition: {
        duration: 5,
        repeat: Infinity,
        repeatType: 'reverse',
        ease: 'easeInOut'
      }
    }
  };
  
  // Particle animation
  useEffect(() => {
    const canvas = particlesRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const particles = [];
    
    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Parse color to RGB
    const parseColor = (color) => {
      const div = document.createElement('div');
      div.style.color = color;
      document.body.appendChild(div);
      const rgbColor = window.getComputedStyle(div).color;
      document.body.removeChild(div);
      
      const match = rgbColor.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
      if (match) {
        return {
          r: parseInt(match[1]),
          g: parseInt(match[2]),
          b: parseInt(match[3])
        };
      }
      
      return { r: 255, g: 255, b: 255 };
    };
    
    // Create particles
    const createParticles = () => {
      const rgb = parseColor(emotion.color);
      const particleCount = 50;
      
      particles.length = 0;
      
      for (let i = 0; i < particleCount; i++) {
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        const size = Math.random() * 5 + 1;
        const speedX = (Math.random() - 0.5) * 0.5;
        const speedY = (Math.random() - 0.5) * 0.5;
        const opacity = Math.random() * 0.5;
        
        particles.push({
          x, y, size, speedX, speedY, opacity,
          color: `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${opacity})`
        });
      }
    };
    
    // Animate particles
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      particles.forEach(particle => {
        // Update position
        particle.x += particle.speedX;
        particle.y += particle.speedY;
        
        // Wrap around edges
        if (particle.x < 0) particle.x = canvas.width;
        if (particle.x > canvas.width) particle.x = 0;
        if (particle.y < 0) particle.y = canvas.height;
        if (particle.y > canvas.height) particle.y = 0;
        
        // Draw particle
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fillStyle = particle.color;
        ctx.fill();
      });
      
      animationRef.current = requestAnimationFrame(animate);
    };
    
    // Initialize
    createParticles();
    animate();
    
    // Cleanup
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationRef.current);
    };
  }, [emotion]);
  
  // Update particles when emotional state changes
  useEffect(() => {
    const canvas = particlesRef.current;
    if (!canvas) return;
    
    // Recreate particles with new color
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Fetch current emotional state from API
    const fetchEmotionalState = async () => {
      try {
        const response = await emotionApi.getState();
        if (response.state && response.state !== emotionalState) {
          changeEmotionalState(response.state);
        }
      } catch (error) {
        console.error('Failed to fetch emotional state:', error);
      }
    };
    
    fetchEmotionalState();
  }, [emotionalState, changeEmotionalState]);
  
  return (
    <AuraContainer>
      <AuraParticles ref={particlesRef} />
      
      <AuraRing
        initial="initial"
        animate="animate"
        variants={outerRingVariants}
        style={{ background: emotion.gradient }}
      />
      
      <AuraRing
        initial="initial"
        animate="animate"
        variants={ringVariants}
        style={{ background: emotion.gradient }}
      />
      
      <AuraCore
        initial="initial"
        animate="animate"
        variants={coreVariants}
        style={{ background: emotion.gradient }}
      />
    </AuraContainer>
  );
};

export default EmotiveAura;
