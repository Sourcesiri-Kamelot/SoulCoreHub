/**
 * SoulCoreHub - Hugging Face Integration Module
 * 
 * This module provides a comprehensive integration with Hugging Face's AI models
 * and serves as a bridge between SoulCoreHub's agents and Hugging Face's capabilities.
 * 
 * @author SoulCoreHub
 * @version 1.0.0
 */

const { InferenceClient } = require('@huggingface/inference');
const { HfAgent } = require('@huggingface/agents');
const { HfInference } = require('@huggingface/inference');
const fs = require('fs');
const path = require('path');
const EventEmitter = require('events');

// Create event emitter for cross-component communication
const hfEvents = new EventEmitter();

// Initialize Hugging Face client with the provided token
const HF_TOKEN = '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';
const hf = new InferenceClient(HF_TOKEN);
const inference = new HfInference(HF_TOKEN);

// Agent for more complex tasks
const agent = new HfAgent(HF_TOKEN);

/**
 * Core Hugging Face service class that provides access to various AI capabilities
 */
class HuggingFaceService {
  constructor() {
    this.modelCache = new Map();
    this.lastUsedModels = [];
    this.eventLog = [];
    
    // Load configuration if exists
    this.config = this._loadConfig();
    
    // Log initialization
    this._logEvent('HuggingFaceService initialized');
  }
  
  /**
   * Generate text using a specified model
   * @param {string} prompt - The input prompt
   * @param {string} model - Optional model name (defaults to config default)
   * @returns {Promise<string>} Generated text
   */
  async generateText(prompt, model = this.config.defaultTextModel) {
    try {
      this._logEvent(`Generating text with model: ${model}`);
      
      const result = await hf.textGeneration({
        model: model,
        inputs: prompt,
        parameters: {
          max_new_tokens: 250,
          temperature: 0.7,
          top_p: 0.95,
          return_full_text: false
        }
      });
      
      this._updateModelUsage(model);
      return result.generated_text;
    } catch (error) {
      this._logEvent(`Error generating text: ${error.message}`, 'error');
      throw error;
    }
  }
  
  /**
   * Generate an image from text prompt
   * @param {string} prompt - Text description of the image
   * @param {string} model - Optional model name
   * @returns {Promise<Buffer>} Image data
   */
  async generateImage(prompt, model = this.config.defaultImageModel) {
    try {
      this._logEvent(`Generating image with model: ${model}`);
      
      const result = await hf.textToImage({
        model: model,
        inputs: prompt,
        parameters: {
          negative_prompt: "blurry, bad quality, distorted",
          guidance_scale: 7.5
        }
      });
      
      this._updateModelUsage(model);
      return result;
    } catch (error) {
      this._logEvent(`Error generating image: ${error.message}`, 'error');
      throw error;
    }
  }
  
  /**
   * Perform sentiment analysis on text
   * @param {string} text - Input text to analyze
   * @returns {Promise<Object>} Sentiment analysis results
   */
  async analyzeSentiment(text) {
    try {
      const model = this.config.sentimentModel;
      this._logEvent(`Analyzing sentiment with model: ${model}`);
      
      const result = await hf.textClassification({
        model: model,
        inputs: text
      });
      
      this._updateModelUsage(model);
      return result;
    } catch (error) {
      this._logEvent(`Error analyzing sentiment: ${error.message}`, 'error');
      throw error;
    }
  }
  
  /**
   * Summarize a longer text
   * @param {string} text - Text to summarize
   * @returns {Promise<string>} Summarized text
   */
  async summarizeText(text) {
    try {
      const model = this.config.summarizationModel;
      this._logEvent(`Summarizing text with model: ${model}`);
      
      const result = await hf.summarization({
        model: model,
        inputs: text,
        parameters: {
          max_length: 100
        }
      });
      
      this._updateModelUsage(model);
      return result.summary_text;
    } catch (error) {
      this._logEvent(`Error summarizing text: ${error.message}`, 'error');
      throw error;
    }
  }
  
  /**
   * Execute a complex task using the Hugging Face agent
   * @param {string} task - Description of the task to perform
   * @returns {Promise<any>} Task result
   */
  async executeTask(task) {
    try {
      this._logEvent(`Executing task with agent: ${task}`);
      const result = await agent.run(task);
      return result;
    } catch (error) {
      this._logEvent(`Error executing task: ${error.message}`, 'error');
      throw error;
    }
  }
  
  /**
   * Get event logs for monitoring
   * @returns {Array} Event logs
   */
  getEventLogs() {
    return this.eventLog;
  }
  
  /**
   * Get statistics about model usage
   * @returns {Object} Usage statistics
   */
  getUsageStatistics() {
    return {
      totalCalls: this.eventLog.length,
      modelUsage: Array.from(this.modelCache.entries()),
      lastUsedModels: this.lastUsedModels
    };
  }
  
  /**
   * Load configuration from file or use defaults
   * @private
   * @returns {Object} Configuration object
   */
  _loadConfig() {
    try {
      // Try to load from config file
      const configPath = path.join(__dirname, 'config', 'huggingface_config.json');
      if (fs.existsSync(configPath)) {
        return JSON.parse(fs.readFileSync(configPath, 'utf8'));
      }
    } catch (error) {
      console.error('Error loading HuggingFace config:', error);
    }
    
    // Default configuration
    return {
      defaultTextModel: 'gpt2',
      defaultImageModel: 'stabilityai/stable-diffusion-2',
      sentimentModel: 'distilbert-base-uncased-finetuned-sst-2-english',
      summarizationModel: 'facebook/bart-large-cnn',
      maxHistoryItems: 50,
      logLevel: 'info'
    };
  }
  
  /**
   * Log an event to the internal event log
   * @private
   * @param {string} message - Event message
   * @param {string} level - Log level
   */
  _logEvent(message, level = 'info') {
    const event = {
      timestamp: new Date().toISOString(),
      message,
      level
    };
    
    this.eventLog.push(event);
    
    // Trim event log if it gets too large
    if (this.eventLog.length > this.config.maxHistoryItems) {
      this.eventLog.shift();
    }
    
    // Emit event for listeners
    hfEvents.emit('log', event);
    
    // Console log based on level
    if (level === 'error') {
      console.error(`[HuggingFace] ${message}`);
    } else if (this.config.logLevel === 'debug' || level === 'warn') {
      console.log(`[HuggingFace] ${message}`);
    }
  }
  
  /**
   * Update model usage statistics
   * @private
   * @param {string} model - Model name
   */
  _updateModelUsage(model) {
    // Update cache
    if (this.modelCache.has(model)) {
      this.modelCache.set(model, this.modelCache.get(model) + 1);
    } else {
      this.modelCache.set(model, 1);
    }
    
    // Update recently used models
    this.lastUsedModels = [model, ...this.lastUsedModels.filter(m => m !== model)].slice(0, 5);
  }
}

// Create singleton instance
const huggingFaceService = new HuggingFaceService();

module.exports = {
  huggingFaceService,
  hf,
  inference,
  agent,
  hfEvents
};
