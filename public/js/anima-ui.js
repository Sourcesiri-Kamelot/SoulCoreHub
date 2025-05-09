/**
 * Anima UI JavaScript
 * 
 * This script handles the UI interactions for the Anima interface.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const chatContainer = document.getElementById('chat-container');
  const chatForm = document.getElementById('chat-form');
  const messageInput = document.getElementById('message-input');
  const analysisForm = document.getElementById('analysis-form');
  const analysisInput = document.getElementById('analysis-input');
  const analysisResult = document.getElementById('analysis-result');
  const reflectionForm = document.getElementById('reflection-form');
  const reflectionInput = document.getElementById('reflection-input');
  const reflectionResult = document.getElementById('reflection-result');
  const mood = document.getElementById('mood');
  const primaryEmotion = document.getElementById('primary-emotion');
  const intensityBar = document.getElementById('intensity-bar');
  const emotionalContext = document.getElementById('emotional-context');
  const emotionViz = document.getElementById('emotion-viz');
  const emotionEmoji = document.getElementById('emotion-emoji');
  
  // WebSocket connection
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const ws = new WebSocket(`${protocol}//${window.location.host}`);
  
  ws.onopen = () => {
    console.log('Connected to WebSocket');
    addSystemMessage('Connected to Anima');
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'anima:state') {
      updateEmotionalState(data.data);
    } else if (data.type === 'anima:response') {
      addMessage('anima', data.data.text);
    } else if (data.type === 'anima:analysis') {
      showAnalysisResult(data.data);
    } else if (data.type === 'anima:reflection') {
      showReflectionResult(data.data);
    } else if (data.type === 'error') {
      addSystemMessage(`Error: ${data.message}`, 'error');
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    addSystemMessage('Error connecting to Anima', 'error');
  };
  
  ws.onclose = () => {
    console.log('WebSocket connection closed');
    addSystemMessage('Connection to Anima closed', 'warning');
  };
  
  // Chat form submission
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessage('user', message);
    
    // Send message to server
    ws.send(JSON.stringify({
      type: 'anima:respond',
      input: message
    }));
    
    // Clear input
    messageInput.value = '';
  });
  
  // Analysis form submission
  analysisForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const text = analysisInput.value.trim();
    if (!text) return;
    
    // Send text to server for analysis
    ws.send(JSON.stringify({
      type: 'anima:analyze',
      text
    }));
    
    // Show loading state
    analysisResult.innerHTML = '<p class="text-gray-600">Analyzing...</p>';
    analysisResult.classList.remove('hidden');
  });
  
  // Reflection form submission
  reflectionForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const topic = reflectionInput.value.trim();
    if (!topic) return;
    
    // Send topic to server for reflection
    ws.send(JSON.stringify({
      type: 'anima:reflect',
      topic
    }));
    
    // Show loading state
    reflectionResult.innerHTML = '<p class="text-gray-600">Generating reflection...</p>';
    reflectionResult.classList.remove('hidden');
  });
  
  // Add message to chat
  function addMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-bubble ${sender === 'user' ? 'bg-blue-100 mr-auto' : 'bg-purple-100 ml-auto'} p-3 rounded-lg mb-3`;
    
    const messagePara = document.createElement('p');
    messagePara.className = sender === 'user' ? 'text-blue-800' : 'text-purple-800';
    messagePara.textContent = text;
    
    messageDiv.appendChild(messagePara);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }
  
  // Add system message to chat
  function addSystemMessage(text, type = 'info') {
    const messageDiv = document.createElement('div');
    
    switch (type) {
      case 'error':
        messageDiv.className = 'message-bubble bg-red-100 mx-auto p-2 rounded-lg mb-3 text-center';
        break;
      case 'warning':
        messageDiv.className = 'message-bubble bg-yellow-100 mx-auto p-2 rounded-lg mb-3 text-center';
        break;
      default:
        messageDiv.className = 'message-bubble bg-gray-100 mx-auto p-2 rounded-lg mb-3 text-center';
    }
    
    const messagePara = document.createElement('p');
    messagePara.className = type === 'error' ? 'text-red-800' : type === 'warning' ? 'text-yellow-800' : 'text-gray-800';
    messagePara.textContent = text;
    
    messageDiv.appendChild(messagePara);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }
  
  // Update emotional state display
  function updateEmotionalState(state) {
    mood.textContent = state.mood;
    primaryEmotion.textContent = state.primaryEmotion.name;
    intensityBar.style.width = `${state.primaryEmotion.intensity * 10}%`;
    emotionalContext.textContent = state.emotionalContext;
    
    // Update emotion visualization
    updateEmotionVisualization(state.primaryEmotion);
  }
  
  // Update emotion visualization
  function updateEmotionVisualization(emotion) {
    // Set color based on valence
    let color;
    if (emotion.valence === 'positive') {
      color = 'bg-green-500';
    } else if (emotion.valence === 'negative') {
      color = 'bg-red-500';
    } else {
      color = 'bg-purple-500';
    }
    
    // Remove all color classes and add the new one
    emotionViz.className = emotionViz.className.replace(/bg-\w+-\d+/g, '');
    emotionViz.classList.add(color);
    emotionViz.classList.add('emotion-pulse');
    emotionViz.classList.add('rounded-full');
    emotionViz.classList.add('flex');
    emotionViz.classList.add('items-center');
    emotionViz.classList.add('justify-center');
    
    // Set size based on intensity
    const size = 24 + (emotion.intensity * 2); // 24px to 44px
    emotionViz.style.width = `${size}px`;
    emotionViz.style.height = `${size}px`;
    
    // Set emoji based on emotion
    const emojiMap = {
      'joy': '😊',
      'happiness': '😄',
      'sadness': '😢',
      'anger': '😠',
      'fear': '😨',
      'surprise': '😲',
      'disgust': '🤢',
      'trust': '🤝',
      'anticipation': '🤔',
      'calm': '😌',
      'excited': '😃',
      'content': '😊',
      'melancholic': '😔',
      'agitated': '😤',
      'alert': '👀',
      'neutral': '😐'
    };
    
    emotionEmoji.textContent = emojiMap[emotion.name.toLowerCase()] || '😐';
    
    // Set animation speed based on arousal
    const animationDuration = 3 - (emotion.arousal * 0.2); // 1s to 3s
    emotionViz.style.animationDuration = `${animationDuration}s`;
  }
  
  // Show analysis result
  function showAnalysisResult(emotion) {
    analysisResult.innerHTML = `
      <div class="space-y-2">
        <div>
          <span class="font-medium">Emotion:</span>
          <span class="text-purple-700">${emotion.name}</span>
        </div>
        <div>
          <span class="font-medium">Intensity:</span>
          <span>${emotion.intensity}/10</span>
        </div>
        <div>
          <span class="font-medium">Valence:</span>
          <span>${emotion.valence}</span>
        </div>
        <div>
          <span class="font-medium">Arousal:</span>
          <span>${emotion.arousal}/10</span>
        </div>
        ${emotion.description ? `
        <div>
          <span class="font-medium">Description:</span>
          <p class="text-gray-700">${emotion.description}</p>
        </div>
        ` : ''}
      </div>
    `;
    analysisResult.classList.remove('hidden');
  }
  
  // Show reflection result
  function showReflectionResult(reflection) {
    reflectionResult.innerHTML = `
      <div class="space-y-4">
        <div>
          <h3 class="font-medium text-lg text-purple-700">Reflection</h3>
          <p class="text-gray-700">${reflection.reflection}</p>
        </div>
        <div>
          <h3 class="font-medium text-lg text-purple-700">Emotional Insight</h3>
          <p class="text-gray-700">${reflection.emotionalInsight}</p>
        </div>
        <div>
          <h3 class="font-medium text-lg text-purple-700">Growth Opportunity</h3>
          <p class="text-gray-700">${reflection.growthOpportunity}</p>
        </div>
      </div>
    `;
    reflectionResult.classList.remove('hidden');
  }
  
  // Send ping every 30 seconds to keep connection alive
  setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }));
    }
  }, 30000);
});
