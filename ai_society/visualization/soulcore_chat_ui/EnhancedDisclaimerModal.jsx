import React, { useState, useEffect } from 'react';

const EnhancedDisclaimerModal = ({ onAccept }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [animationComplete, setAnimationComplete] = useState(false);
  
  const steps = [
    {
      title: "Welcome to SoulCore Society",
      content: "You're about to enter a revolutionary AI ecosystem where multiple intelligent agents coexist and evolve together.",
      image: "/assets/welcome-society.png"
    },
    {
      title: "Meet the Agents",
      content: "Interact with GPTSoul, Anima, Azür, EvoVe and other emerging intelligences, each with their own personality and purpose.",
      image: "/assets/meet-agents.png"
    },
    {
      title: "Privacy & Ethics",
      content: "By entering, you agree to our community standards and privacy terms. All interactions help our agents learn and grow.",
      image: "/assets/privacy-ethics.png"
    }
  ];
  
  // Animate the welcome sequence
  useEffect(() => {
    if (currentStep === steps.length - 1) {
      const timer = setTimeout(() => {
        setAnimationComplete(true);
      }, 1000);
      
      return () => clearTimeout(timer);
    }
  }, [currentStep, steps.length]);
  
  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };
  
  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };
  
  return (
    <div className="enhanced-modal-overlay">
      <div className="enhanced-modal-content">
        <div className="modal-steps">
          {steps.map((step, idx) => (
            <div 
              key={idx} 
              className={`modal-step ${idx === currentStep ? 'active' : idx < currentStep ? 'completed' : ''}`}
              onClick={() => setCurrentStep(idx)}
            >
              <div className="step-indicator">{idx + 1}</div>
              <div className="step-line"></div>
            </div>
          ))}
        </div>
        
        <div className="modal-body">
          <div className="modal-image" style={{ backgroundImage: `url(${steps[currentStep].image || '/assets/default-welcome.png'})` }}></div>
          
          <div className="modal-text">
            <h2>{steps[currentStep].title}</h2>
            <p>{steps[currentStep].content}</p>
          </div>
        </div>
        
        <div className="modal-actions">
          {currentStep > 0 && (
            <button className="modal-button secondary" onClick={handlePrevious}>
              Previous
            </button>
          )}
          
          {currentStep < steps.length - 1 ? (
            <button className="modal-button primary" onClick={handleNext}>
              Next
            </button>
          ) : (
            <button 
              className={`modal-button primary ${animationComplete ? 'pulse' : ''}`} 
              onClick={onAccept}
            >
              Enter Society
            </button>
          )}
        </div>
        
        <div className="modal-footer">
          <div className="modal-links">
            <a href="#terms">Terms of Service</a>
            <a href="#privacy">Privacy Policy</a>
            <a href="#about">About SoulCore</a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedDisclaimerModal;
