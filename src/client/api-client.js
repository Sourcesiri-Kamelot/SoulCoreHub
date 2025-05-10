/**
 * SoulCoreHub API Client
 * 
 * This module provides a client for interacting with the SoulCoreHub API.
 */

import RequestSigner from './request-signer';

class ApiClient {
  /**
   * Create a new ApiClient instance
   * 
   * @param {string} apiEndpoint - The base API endpoint URL
   * @param {string} apiKey - The API key for authentication
   * @param {string} apiSecret - The API secret for signing requests
   */
  constructor(apiEndpoint, apiKey, apiSecret) {
    this.apiEndpoint = apiEndpoint;
    this.requestSigner = new RequestSigner(apiKey, apiSecret);
    this.sessionId = this._generateSessionId();
    this.userId = localStorage.getItem('userId') || 'anonymous';
  }

  /**
   * Generate a unique session ID
   * 
   * @returns {string} - A unique session ID
   * @private
   */
  _generateSessionId() {
    return 'session-' + Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }

  /**
   * Set the user ID
   * 
   * @param {string} userId - The user ID
   */
  setUserId(userId) {
    this.userId = userId;
    localStorage.setItem('userId', userId);
  }

  /**
   * Send a message to Anima
   * 
   * @param {string} input - The user's input message
   * @returns {Promise<Object>} - Anima's response
   */
  async sendToAnima(input) {
    const data = {
      input,
      session_id: this.sessionId,
      user_id: this.userId
    };

    return this.requestSigner.makeRequest(`${this.apiEndpoint}/anima`, data);
  }

  /**
   * Send a message to the Neural Router
   * 
   * @param {string} input - The user's input message
   * @returns {Promise<Object>} - The routed response
   */
  async sendToRouter(input) {
    const data = {
      input,
      session_id: this.sessionId,
      user_id: this.userId
    };

    return this.requestSigner.makeRequest(`${this.apiEndpoint}/route`, data);
  }

  /**
   * Perform a memory operation
   * 
   * @param {string} operation - The memory operation (read, write, backup, restore)
   * @param {string} agentId - The agent ID
   * @param {Object} memoryData - The memory data (for write operation)
   * @returns {Promise<Object>} - The memory operation result
   */
  async memoryOperation(operation, agentId, memoryData = null) {
    const data = {
      operation,
      agent_id: agentId,
      user_id: this.userId
    };

    if (memoryData) {
      data.memory_data = memoryData;
    }

    return this.requestSigner.makeRequest(`${this.apiEndpoint}/memory`, data);
  }
}

export default ApiClient;
