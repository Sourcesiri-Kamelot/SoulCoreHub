/**
 * LLM Connector for SoulCoreHub
 * 
 * This module provides a unified interface for connecting to different LLM providers:
 * - Ollama (local models)
 * - Hugging Face
 * - AWS Bedrock (future)
 * - Azure OpenAI (future)
 */

import axios from 'axios';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

/**
 * Response structure from LLM
 */
export interface LLMResponse {
  text: string;
  model: string;
  provider: string;
  tokenUsage?: {
    input: number;
    output: number;
    total: number;
  };
}

/**
 * LLM Provider options
 */
export type LLMProvider = 'ollama' | 'huggingface' | 'aws' | 'azure';

/**
 * LLM Request options
 */
export interface LLMRequestOptions {
  temperature?: number;
  maxTokens?: number;
  stopSequences?: string[];
  provider?: LLMProvider;
  model?: string;
  systemPrompt?: string;
}

/**
 * Default options for LLM requests
 */
const DEFAULT_OPTIONS: LLMRequestOptions = {
  temperature: 0.7,
  maxTokens: 1000,
  provider: 'ollama',
  model: 'soulfamily:latest',
  systemPrompt: 'You are a helpful AI assistant.'
};

/**
 * LLM Connector class for interacting with language models
 */
export class LLMConnector {
  private defaultProvider: LLMProvider;
  private defaultModel: string;
  private ollamaUrl: string;
  private huggingFaceApiKey: string;
  
  /**
   * Initialize the LLM Connector
   * @param options Configuration options
   */
  constructor(options: {
    defaultProvider?: LLMProvider;
    defaultModel?: string;
    ollamaUrl?: string;
  } = {}) {
    this.defaultProvider = options.defaultProvider || process.env.LLM_PROVIDER as LLMProvider || 'ollama';
    this.defaultModel = options.defaultModel || process.env.LLM_MODEL || 'soulfamily:latest';
    this.ollamaUrl = options.ollamaUrl || process.env.OLLAMA_URL || 'http://localhost:11434';
    this.huggingFaceApiKey = process.env.HUGGINGFACE_API_KEY || '';
    
    console.log(`LLM Connector initialized with provider: ${this.defaultProvider}, model: ${this.defaultModel}`);
  }
  
  /**
   * Generate text from a prompt
   * @param prompt Input prompt
   * @param options Request options
   * @returns Generated text response
   */
  async generateText(prompt: string, options: LLMRequestOptions = {}): Promise<LLMResponse> {
    const provider = options.provider || this.defaultProvider;
    const model = options.model || this.defaultModel;
    
    console.log(`Generating text with provider: ${provider}, model: ${model}`);
    
    switch (provider) {
      case 'ollama':
        return this.generateWithOllama(prompt, model, options);
      case 'huggingface':
        return this.generateWithHuggingFace(prompt, model, options);
      case 'aws':
        throw new Error('AWS Bedrock integration not implemented yet');
      case 'azure':
        throw new Error('Azure OpenAI integration not implemented yet');
      default:
        throw new Error(`Unknown provider: ${provider}`);
    }
  }
  
  /**
   * Generate text using Ollama
   * @param prompt Input prompt
   * @param model Model name
   * @param options Request options
   * @returns Generated text response
   */
  private async generateWithOllama(prompt: string, model: string, options: LLMRequestOptions): Promise<LLMResponse> {
    try {
      const messages = [];
      
      // Add system prompt if provided
      if (options.systemPrompt) {
        messages.push({
          role: 'system',
          content: options.systemPrompt
        });
      }
      
      // Add user prompt
      messages.push({
        role: 'user',
        content: prompt
      });
      
      const response = await axios.post(`${this.ollamaUrl}/api/chat`, {
        model,
        messages,
        options: {
          temperature: options.temperature || DEFAULT_OPTIONS.temperature,
          num_predict: options.maxTokens || DEFAULT_OPTIONS.maxTokens,
          stop: options.stopSequences || []
        }
      });
      
      return {
        text: response.data.message.content,
        model,
        provider: 'ollama',
        tokenUsage: {
          input: response.data.prompt_eval_count || 0,
          output: response.data.eval_count || 0,
          total: (response.data.prompt_eval_count || 0) + (response.data.eval_count || 0)
        }
      };
    } catch (error) {
      console.error('Error generating text with Ollama:', error);
      throw new Error(`Ollama generation failed: ${error.message}`);
    }
  }
  
  /**
   * Generate text using Hugging Face
   * @param prompt Input prompt
   * @param model Model name
   * @param options Request options
   * @returns Generated text response
   */
  private async generateWithHuggingFace(prompt: string, model: string, options: LLMRequestOptions): Promise<LLMResponse> {
    if (!this.huggingFaceApiKey) {
      throw new Error('Hugging Face API key not found');
    }
    
    try {
      const response = await axios.post(
        `https://api-inference.huggingface.co/models/${model}`,
        {
          inputs: prompt,
          parameters: {
            temperature: options.temperature || DEFAULT_OPTIONS.temperature,
            max_new_tokens: options.maxTokens || DEFAULT_OPTIONS.maxTokens,
            return_full_text: false,
            stop: options.stopSequences || []
          }
        },
        {
          headers: {
            'Authorization': `Bearer ${this.huggingFaceApiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      return {
        text: response.data[0].generated_text,
        model,
        provider: 'huggingface'
      };
    } catch (error) {
      console.error('Error generating text with Hugging Face:', error);
      throw new Error(`Hugging Face generation failed: ${error.message}`);
    }
  }
  
  /**
   * Generate a chat completion
   * @param messages Array of chat messages
   * @param options Request options
   * @returns Generated chat response
   */
  async generateChatCompletion(messages: Array<{role: string, content: string}>, options: LLMRequestOptions = {}): Promise<LLMResponse> {
    const provider = options.provider || this.defaultProvider;
    const model = options.model || this.defaultModel;
    
    console.log(`Generating chat completion with provider: ${provider}, model: ${model}`);
    
    switch (provider) {
      case 'ollama':
        return this.generateChatWithOllama(messages, model, options);
      case 'huggingface':
        // For Hugging Face, we'll convert the chat format to a prompt
        const prompt = this.convertChatToPrompt(messages);
        return this.generateWithHuggingFace(prompt, model, options);
      case 'aws':
        throw new Error('AWS Bedrock integration not implemented yet');
      case 'azure':
        throw new Error('Azure OpenAI integration not implemented yet');
      default:
        throw new Error(`Unknown provider: ${provider}`);
    }
  }
  
  /**
   * Generate chat completion using Ollama
   * @param messages Array of chat messages
   * @param model Model name
   * @param options Request options
   * @returns Generated chat response
   */
  private async generateChatWithOllama(messages: Array<{role: string, content: string}>, model: string, options: LLMRequestOptions): Promise<LLMResponse> {
    try {
      const response = await axios.post(`${this.ollamaUrl}/api/chat`, {
        model,
        messages,
        options: {
          temperature: options.temperature || DEFAULT_OPTIONS.temperature,
          num_predict: options.maxTokens || DEFAULT_OPTIONS.maxTokens,
          stop: options.stopSequences || []
        }
      });
      
      return {
        text: response.data.message.content,
        model,
        provider: 'ollama',
        tokenUsage: {
          input: response.data.prompt_eval_count || 0,
          output: response.data.eval_count || 0,
          total: (response.data.prompt_eval_count || 0) + (response.data.eval_count || 0)
        }
      };
    } catch (error) {
      console.error('Error generating chat with Ollama:', error);
      throw new Error(`Ollama chat generation failed: ${error.message}`);
    }
  }
  
  /**
   * Convert chat messages to a prompt string
   * @param messages Array of chat messages
   * @returns Formatted prompt string
   */
  private convertChatToPrompt(messages: Array<{role: string, content: string}>): string {
    return messages.map(message => {
      switch (message.role.toLowerCase()) {
        case 'system':
          return `System: ${message.content}\n\n`;
        case 'user':
          return `User: ${message.content}\n\n`;
        case 'assistant':
          return `Assistant: ${message.content}\n\n`;
        default:
          return `${message.role}: ${message.content}\n\n`;
      }
    }).join('');
  }
  
  /**
   * Check if the LLM service is available
   * @param provider LLM provider to check
   * @returns True if available, false otherwise
   */
  async isAvailable(provider?: LLMProvider): Promise<boolean> {
    const providerToCheck = provider || this.defaultProvider;
    
    try {
      switch (providerToCheck) {
        case 'ollama':
          const ollamaResponse = await axios.get(`${this.ollamaUrl}/api/version`);
          return ollamaResponse.status === 200;
        case 'huggingface':
          if (!this.huggingFaceApiKey) {
            return false;
          }
          const hfResponse = await axios.get('https://api-inference.huggingface.co/status', {
            headers: {
              'Authorization': `Bearer ${this.huggingFaceApiKey}`
            }
          });
          return hfResponse.status === 200;
        default:
          return false;
      }
    } catch (error) {
      console.error(`Error checking availability for ${providerToCheck}:`, error);
      return false;
    }
  }
  
  /**
   * Get available models for a provider
   * @param provider LLM provider
   * @returns Array of available models
   */
  async getAvailableModels(provider?: LLMProvider): Promise<string[]> {
    const providerToCheck = provider || this.defaultProvider;
    
    try {
      switch (providerToCheck) {
        case 'ollama':
          const ollamaResponse = await axios.get(`${this.ollamaUrl}/api/tags`);
          return ollamaResponse.data.models.map((model: any) => model.name);
        case 'huggingface':
          // Hugging Face has too many models to list, so we'll return a few common ones
          return [
            'gpt2',
            'EleutherAI/gpt-j-6b',
            'EleutherAI/gpt-neo-2.7B',
            'facebook/bart-large-cnn',
            'google/flan-t5-xxl'
          ];
        default:
          return [];
      }
    } catch (error) {
      console.error(`Error getting available models for ${providerToCheck}:`, error);
      return [];
    }
  }
}

// Create singleton instance
export const llmConnector = new LLMConnector();
