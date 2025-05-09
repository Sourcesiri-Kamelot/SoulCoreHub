/**
 * AWS Secrets Manager Integration
 * 
 * This module provides functions to securely retrieve secrets from AWS Secrets Manager.
 */

const AWS = require('aws-sdk');

// Initialize AWS SDK with region
const region = process.env.AWS_REGION || 'us-east-1';
AWS.config.update({ region });

// Create Secrets Manager client
const secretsManager = new AWS.SecretsManager();

/**
 * Retrieve a secret from AWS Secrets Manager
 * @param {string} secretName - Name of the secret to retrieve
 * @returns {Promise<Object>} - Parsed secret value as an object
 */
async function getSecrets(secretName) {
  try {
    const data = await secretsManager.getSecretValue({ SecretId: secretName }).promise();
    
    // Parse and return the secret string
    if ('SecretString' in data) {
      return JSON.parse(data.SecretString);
    } else {
      // Handle binary secrets if needed
      const buff = Buffer.from(data.SecretBinary, 'base64');
      return JSON.parse(buff.toString('ascii'));
    }
  } catch (error) {
    console.error(`Error retrieving secret ${secretName}:`, error);
    throw error;
  }
}

/**
 * Get a specific secret value by key
 * @param {string} secretName - Name of the secret to retrieve
 * @param {string} key - Key of the specific secret value to retrieve
 * @returns {Promise<string>} - The specific secret value
 */
async function getSecretValue(secretName, key) {
  const secrets = await getSecrets(secretName);
  return secrets[key];
}

/**
 * Fallback function to get secrets from environment variables
 * when AWS Secrets Manager is not available (e.g., local development)
 * @param {string} key - Environment variable name
 * @param {string} defaultValue - Default value if not found
 * @returns {string} - The environment variable value or default
 */
function getEnvSecret(key, defaultValue = '') {
  return process.env[key] || defaultValue;
}

module.exports = {
  getSecrets,
  getSecretValue,
  getEnvSecret
};
