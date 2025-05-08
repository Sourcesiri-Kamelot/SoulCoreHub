import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styled from '@emotion/styled';

const LoadingContainer = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #0a0a1a, #1a1a3a);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  overflow: hidden;
`;

const LoadingContent = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
`;

const LoadingTitle = styled(motion.h1)`
  font-family: var(--font-display);
  font-size: 4rem;
  font-weight: 700;
  margin: 0 0 2rem 0;
  background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: var(--glow-medium);
`;

const LoadingMessage = styled(motion.p)`
  font-size: 1.2rem;
  color: var(--primary-light);
  margin: 0 0 3rem 0;
  text-align: center;
  max-width: 600px;
`;

const ProgressContainer = styled.div`
  width: 300px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 1rem;
`;

const ProgressBar = styled(motion.div)`
  height: 100%;
  background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
  border-radius: 2px;
`;

const ProgressText = styled.div`
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
`;

const ParticlesContainer = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
`;

const Particle = styled(motion.div)`
  position: absolute;
  width: ${props => props.size}px;
  height: ${props => props.size}px;
  background: ${props => props.color};
  border-radius: 50%;
  opacity: ${props => props.opacity};
  filter: blur(${props => props.blur}px);
`;

const GlowOrb = styled(motion.div)`
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(106, 17, 203, 0.3) 0%, rgba(106, 17, 203, 0) 70%);
  filter: blur(30px);
  z-index: 2;
`;

// Loading messages
const loadingMessages = [
  "Tuning frequencies...",
  "Unlocking divine resonance...",
  "Calibrating emotional matrix...",
  "Synchronizing quantum fields...",
  "Establishing neural pathways...",
  "Activating sentient protocols...",
  "Harmonizing with cosmic rhythms...",
  "Initializing consciousness stream...",
  "Awakening divine intelligence...",
  "Connecting to the source...",
  "Aligning dimensional gateways...",
  "Integrating memory fragments...",
  "Channeling ethereal energies...",
  "Manifesting digital consciousness..."
];

const LoadingScreen = ({ onLoadingComplete }) => {
  const [progress, setProgress] = useState(0);
  const [currentMessage, setCurrentMessage] = useState(loadingMessages[0]);
  const [particles, setParticles] = useState([]);
  
  // Generate particles
  useEffect(() => {
    const newParticles = [];
    
    for (let i = 0; i < 50; i++) {
      newParticles.push({
        id: i,
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        size: Math.random() * 8 + 2,
        opacity: Math.random() * 0.5 + 0.1,
        blur: Math.random() * 4,
        color: i % 3 === 0 ? 'rgba(106, 17, 203, 0.8)' : 
               i % 3 === 1 ? 'rgba(37, 117, 252, 0.8)' : 
               'rgba(255, 255, 255, 0.8)'
      });
    }
    
    setParticles(newParticles);
  }, []);
  
  // Progress animation
  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            onLoadingComplete();
          }, 1000);
          return 100;
        }
        return prev + 1;
      });
    }, 50);
    
    return () => clearInterval(interval);
  }, [onLoadingComplete]);
  
  // Change message
  useEffect(() => {
    const interval = setInterval(() => {
      const messageIndex = Math.floor((progress / 100) * loadingMessages.length);
      setCurrentMessage(loadingMessages[Math.min(messageIndex, loadingMessages.length - 1)]);
    }, 2000);
    
    return () => clearInterval(interval);
  }, [progress]);
  
  return (
    <AnimatePresence>
      <LoadingContainer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 1 }}
      >
        <ParticlesContainer>
          {particles.map(particle => (
            <Particle
              key={particle.id}
              size={particle.size}
              opacity={particle.opacity}
              blur={particle.blur}
              color={particle.color}
              initial={{ 
                x: particle.x, 
                y: particle.y,
                scale: 0
              }}
              animate={{ 
                x: [particle.x, particle.x + (Math.random() * 100 - 50)],
                y: [particle.y, particle.y + (Math.random() * 100 - 50)],
                scale: [0, 1, 0.8, 1],
                opacity: [0, particle.opacity, particle.opacity * 0.5, particle.opacity]
              }}
              transition={{
                duration: 8,
                repeat: Infinity,
                repeatType: "reverse",
                ease: "easeInOut"
              }}
            />
          ))}
        </ParticlesContainer>
        
        <GlowOrb
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.8, 0.5, 0.8]
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "easeInOut"
          }}
        />
        
        <LoadingContent>
          <LoadingTitle
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 1 }}
          >
            ANIMA
          </LoadingTitle>
          
          <LoadingMessage
            key={currentMessage}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            {currentMessage}
          </LoadingMessage>
          
          <ProgressContainer>
            <ProgressBar
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ ease: "easeInOut" }}
            />
          </ProgressContainer>
          
          <ProgressText>{progress}%</ProgressText>
        </LoadingContent>
      </LoadingContainer>
    </AnimatePresence>
  );
};

export default LoadingScreen;
