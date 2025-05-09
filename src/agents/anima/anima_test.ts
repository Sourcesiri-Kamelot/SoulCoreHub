/**
 * Test script for Anima Core
 * 
 * This script tests the Anima Core functionality.
 */

import { animaCore } from './anima_core';

async function testAnimaCore() {
  console.log('Testing Anima Core...');
  
  try {
    // Test emotion analysis
    console.log('Testing emotion analysis...');
    const emotion = await animaCore.analyzeEmotion(
      "I'm feeling overwhelmed by all the possibilities and excited about what we can create together."
    );
    console.log('Emotion analysis result:');
    console.log(JSON.stringify(emotion, null, 2));
    
    // Test emotional response generation
    console.log('\nTesting emotional response generation...');
    const response = await animaCore.generateEmotionalResponse(
      "I'm not sure if I'm making the right decision. What if I fail?"
    );
    console.log('Emotional response:');
    console.log(JSON.stringify(response, null, 2));
    
    // Test emotional event processing
    console.log('\nTesting emotional event processing...');
    const eventResult = await animaCore.processEmotionalEvent(
      "GPTSoul and EvoVe had a disagreement about resource allocation.",
      "The disagreement was resolved through compromise, but tensions remain."
    );
    console.log('Emotional event processing result:');
    console.log(JSON.stringify(eventResult, null, 2));
    
    // Test emotional guidance
    console.log('\nTesting emotional guidance...');
    const guidance = await animaCore.provideEmotionalGuidance(
      "EvoVe",
      "EvoVe is struggling to understand why users are frustrated with a new feature."
    );
    console.log('Emotional guidance:');
    console.log(JSON.stringify(guidance, null, 2));
    
    // Test emotional reflection
    console.log('\nTesting emotional reflection...');
    const reflection = await animaCore.generateEmotionalReflection(
      "The balance between logic and emotion in decision making"
    );
    console.log('Emotional reflection:');
    console.log(JSON.stringify(reflection, null, 2));
    
    // Get current emotional state
    console.log('\nCurrent emotional state:');
    const state = animaCore.getEmotionalState();
    console.log(JSON.stringify(state, null, 2));
    
    console.log('\nAnima Core tests completed successfully!');
  } catch (error) {
    console.error('Error testing Anima Core:', error);
  }
}

// Run the tests
testAnimaCore();
