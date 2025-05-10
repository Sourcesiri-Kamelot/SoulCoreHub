/**
 * SoulCoreHub Request Signer
 * 
 * This module provides functionality to sign API requests to prevent tampering.
 */

import CryptoJS from 'crypto-js';

class RequestSigner {
  /**
   * Create a new RequestSigner instance
   * 
   * @param {string} apiKey - The API key for authentication
   * @param {string} apiSecret - The API secret for signing requests
   */
  constructor(apiKey, apiSecret) {
    this.apiKey = apiKey;
    this.apiSecret = apiSecret;
  }

  /**
   * Sign a request payload
   * 
   * @param {Object|string} data - The request data to sign
   * @returns {string} - The signature
   */
  sign(data) {
    const dataString = typeof data === 'string' ? data : JSON.stringify(data);
    return CryptoJS.HmacSHA256(dataString, this.apiSecret).toString(CryptoJS.enc.Base64);
  }

  /**
   * Get headers with authentication and signature
   * 
   * @param {Object|string} data - The request data to sign
   * @returns {Object} - Headers object with authentication and signature
   */
  getHeaders(data) {
    return {
      'Content-Type': 'application/json',
      'X-Api-Key': this.apiKey,
      'X-Request-Signature': this.sign(data)
    };
  }

  /**
   * Make a signed API request
   * 
   * @param {string} url - The API endpoint URL
   * @param {Object} data - The request data
   * @returns {Promise<Object>} - The API response
   */
  async makeRequest(url, data) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: this.getHeaders(data),
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }
}

export default RequestSigner;
