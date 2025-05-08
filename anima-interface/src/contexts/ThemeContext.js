import React, { createContext, useState, useEffect } from 'react';

export const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [darkMode, setDarkMode] = useState(true);
  const [accentColor, setAccentColor] = useState('#6a11cb');
  const [glowIntensity, setGlowIntensity] = useState('medium');
  const [animationSpeed, setAnimationSpeed] = useState('normal');
  const [fontScale, setFontScale] = useState(1);
  const [interfaceScale, setInterfaceScale] = useState(1);
  const [blurEffects, setBlurEffects] = useState(true);
  const [particleEffects, setParticleEffects] = useState(true);

  // Theme presets
  const themePresets = {
    cosmic: {
      darkMode: true,
      accentColor: '#6a11cb',
      glowIntensity: 'medium',
      animationSpeed: 'normal',
      blurEffects: true,
      particleEffects: true
    },
    ethereal: {
      darkMode: true,
      accentColor: '#2ecc71',
      glowIntensity: 'high',
      animationSpeed: 'slow',
      blurEffects: true,
      particleEffects: true
    },
    divine: {
      darkMode: true,
      accentColor: '#9b59b6',
      glowIntensity: 'high',
      animationSpeed: 'normal',
      blurEffects: true,
      particleEffects: true
    },
    inferno: {
      darkMode: true,
      accentColor: '#e74c3c',
      glowIntensity: 'high',
      animationSpeed: 'fast',
      blurEffects: true,
      particleEffects: true
    },
    oceanic: {
      darkMode: true,
      accentColor: '#3498db',
      glowIntensity: 'medium',
      animationSpeed: 'slow',
      blurEffects: true,
      particleEffects: true
    },
    light: {
      darkMode: false,
      accentColor: '#2575fc',
      glowIntensity: 'low',
      animationSpeed: 'normal',
      blurEffects: false,
      particleEffects: false
    }
  };

  // Apply theme to document
  useEffect(() => {
    document.documentElement.style.setProperty('--accent-1', accentColor);
    document.documentElement.style.setProperty('--accent-2', shiftColor(accentColor, 30));
    document.documentElement.style.setProperty('--accent-3', shiftColor(accentColor, -20));
    document.documentElement.style.setProperty('--accent-4', shiftColor(accentColor, -40));
    
    // Set glow intensity
    let glowValue = '0 0 15px rgba(106, 17, 203, 0.5)';
    if (glowIntensity === 'low') {
      glowValue = '0 0 10px rgba(106, 17, 203, 0.3)';
    } else if (glowIntensity === 'high') {
      glowValue = '0 0 20px rgba(106, 17, 203, 0.7)';
    }
    document.documentElement.style.setProperty('--glow-medium', glowValue);
    
    // Set animation speed
    let transitionSpeed = '0.3s';
    if (animationSpeed === 'slow') {
      transitionSpeed = '0.5s';
    } else if (animationSpeed === 'fast') {
      transitionSpeed = '0.2s';
    }
    document.documentElement.style.setProperty('--transition-speed', transitionSpeed);
    
    // Set font scale
    document.documentElement.style.setProperty('--font-scale', fontScale);
    
    // Set interface scale
    document.body.style.zoom = interfaceScale;
    
    // Set dark/light mode
    if (darkMode) {
      document.documentElement.style.setProperty('--primary-dark', '#0a0a1a');
      document.documentElement.style.setProperty('--primary-light', '#f8f9fa');
      document.body.classList.add('dark-mode');
      document.body.classList.remove('light-mode');
    } else {
      document.documentElement.style.setProperty('--primary-dark', '#f8f9fa');
      document.documentElement.style.setProperty('--primary-light', '#0a0a1a');
      document.body.classList.add('light-mode');
      document.body.classList.remove('dark-mode');
    }
  }, [darkMode, accentColor, glowIntensity, animationSpeed, fontScale, interfaceScale]);

  // Helper function to shift color hue
  const shiftColor = (hex, amount) => {
    // Convert hex to RGB
    let r = parseInt(hex.substring(1, 3), 16);
    let g = parseInt(hex.substring(3, 5), 16);
    let b = parseInt(hex.substring(5, 7), 16);
    
    // Shift values
    r = Math.max(0, Math.min(255, r + amount));
    g = Math.max(0, Math.min(255, g + amount));
    b = Math.max(0, Math.min(255, b + amount));
    
    // Convert back to hex
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  };

  // Apply theme preset
  const applyThemePreset = (presetName) => {
    const preset = themePresets[presetName];
    if (preset) {
      setDarkMode(preset.darkMode);
      setAccentColor(preset.accentColor);
      setGlowIntensity(preset.glowIntensity);
      setAnimationSpeed(preset.animationSpeed);
      setBlurEffects(preset.blurEffects);
      setParticleEffects(preset.particleEffects);
    }
  };

  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(prev => !prev);
  };

  // Context value
  const value = {
    darkMode,
    accentColor,
    glowIntensity,
    animationSpeed,
    fontScale,
    interfaceScale,
    blurEffects,
    particleEffects,
    themePresets,
    toggleDarkMode,
    setAccentColor,
    setGlowIntensity,
    setAnimationSpeed,
    setFontScale,
    setInterfaceScale,
    setBlurEffects,
    setParticleEffects,
    applyThemePreset
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};
