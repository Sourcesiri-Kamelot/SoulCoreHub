/**
 * Test script for LLM Connector
 * 
 * This script tests the LLM Connector with different providers and models.
 */

import { llmConnector } from './llm_connector';

async function testLLMConnector() {
  console.log('Testing LLM Connector...');
  
  try {
    // Test Ollama availability
    console.log('Testing Ollama availability...');
    const ollamaAvailable = await llmConnector.isAvailable('ollama');
    console.log(`Ollama available: ${ollamaAvailable}`);
    
    if (ollamaAvailable) {
      // Get available models
      console.log('Getting available Ollama models...');
      const ollamaModels = await llmConnector.getAvailableModels('ollama');
      console.log(`Available Ollama models: ${ollamaModels.join(', ')}`);
      
      // Test text generation
      console.log('Testing text generation with Ollama...');
      const textResponse = await llmConnector.generateText(
        'What is the purpose of SoulCoreHub?',
        {
          provider: 'ollama',
          model: 'soulfamily:latest',
          temperature: 0.7,
          maxTokens: 500
        }
      );
      console.log('Ollama text response:');
      console.log(textResponse.text);
      console.log(`Token usage: ${JSON.stringify(textResponse.tokenUsage)}`);
      
      // Test chat completion
      console.log('Testing chat completion with Ollama...');
      const chatResponse = await llmConnector.generateChatCompletion(
        [
          {
            role: 'system',
            content: 'You are Anima, the emotional core of SoulCoreHub. You help agents understand and process emotions.'
          },
          {
            role: 'user',
            content: 'How do you help other agents process complex emotions?'
          }
        ],
        {
          provider: 'ollama',
          model: 'soulfamily:latest',
          temperature: 0.7,
          maxTokens: 500
        }
      );
      console.log('Ollama chat response:');
      console.log(chatResponse.text);
      console.log(`Token usage: ${JSON.stringify(chatResponse.tokenUsage)}`);
    }
    
    // Test Hugging Face availability
    console.log('Testing Hugging Face availability...');
    const hfAvailable = await llmConnector.isAvailable('huggingface');
    console.log(`Hugging Face available: ${hfAvailable}`);
    
    if (hfAvailable) {
      // Test text generation with Hugging Face
      console.log('Testing text generation with Hugging Face...');
      const hfResponse = await llmConnector.generateText(
        'What is the purpose of SoulCoreHub?',
        {
          provider: 'huggingface',
          model: 'gpt2',
          temperature: 0.7,
          maxTokens: 100
        }
      );
      console.log('Hugging Face response:');
      console.log(hfResponse.text);
    }
    
    console.log('LLM Connector tests completed successfully!');
  } catch (error) {
    console.error('Error testing LLM Connector:', error);
  }
}

// Run the tests
testLLMConnector();
