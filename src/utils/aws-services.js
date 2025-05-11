/**
 * AWS Services Utility for SoulCoreHub
 * 
 * This file contains utility functions for interacting with AWS services.
 */

const AWS = require('aws-sdk');
const awsConfig = require('../config/aws-config');

// Configure AWS SDK
AWS.config.region = awsConfig.region;

// Initialize AWS services
const cognitoIdentityServiceProvider = new AWS.CognitoIdentityServiceProvider();
const cognitoIdentity = new AWS.CognitoIdentity();
const comprehend = new AWS.Comprehend();
const codeBuild = new AWS.CodeBuild();

/**
 * Cognito Authentication Functions
 */
const cognitoAuth = {
  /**
   * Sign up a new user
   * @param {string} username - The username
   * @param {string} password - The password
   * @param {string} email - The email address
   * @returns {Promise} - The sign up result
   */
  signUp: async (username, password, email) => {
    const params = {
      ClientId: awsConfig.cognito.userPoolWebClientId,
      Username: username,
      Password: password,
      UserAttributes: [
        {
          Name: 'email',
          Value: email,
        },
      ],
    };
    
    return cognitoIdentityServiceProvider.signUp(params).promise();
  },
  
  /**
   * Confirm a user's registration
   * @param {string} username - The username
   * @param {string} confirmationCode - The confirmation code
   * @returns {Promise} - The confirmation result
   */
  confirmSignUp: async (username, confirmationCode) => {
    const params = {
      ClientId: awsConfig.cognito.userPoolWebClientId,
      Username: username,
      ConfirmationCode: confirmationCode,
    };
    
    return cognitoIdentityServiceProvider.confirmSignUp(params).promise();
  },
  
  /**
   * Sign in a user
   * @param {string} username - The username
   * @param {string} password - The password
   * @returns {Promise} - The sign in result
   */
  signIn: async (username, password) => {
    const params = {
      AuthFlow: 'USER_PASSWORD_AUTH',
      ClientId: awsConfig.cognito.userPoolWebClientId,
      AuthParameters: {
        USERNAME: username,
        PASSWORD: password,
      },
    };
    
    return cognitoIdentityServiceProvider.initiateAuth(params).promise();
  },
};

/**
 * Comprehend Text Analysis Functions
 */
const textAnalysis = {
  /**
   * Detect sentiment in text
   * @param {string} text - The text to analyze
   * @returns {Promise} - The sentiment analysis result
   */
  detectSentiment: async (text) => {
    const params = {
      Text: text,
      LanguageCode: 'en',
    };
    
    return comprehend.detectSentiment(params).promise();
  },
  
  /**
   * Detect key phrases in text
   * @param {string} text - The text to analyze
   * @returns {Promise} - The key phrases analysis result
   */
  detectKeyPhrases: async (text) => {
    const params = {
      Text: text,
      LanguageCode: 'en',
    };
    
    return comprehend.detectKeyPhrases(params).promise();
  },
  
  /**
   * Detect entities in text
   * @param {string} text - The text to analyze
   * @returns {Promise} - The entities analysis result
   */
  detectEntities: async (text) => {
    const params = {
      Text: text,
      LanguageCode: 'en',
    };
    
    return comprehend.detectEntities(params).promise();
  },
};

/**
 * CodeBuild Functions
 */
const buildServices = {
  /**
   * Start a build
   * @returns {Promise} - The build result
   */
  startBuild: async () => {
    const params = {
      projectName: awsConfig.codeBuild.projectName,
    };
    
    return codeBuild.startBuild(params).promise();
  },
  
  /**
   * Get build status
   * @param {string} buildId - The build ID
   * @returns {Promise} - The build status
   */
  getBuildStatus: async (buildId) => {
    const params = {
      ids: [buildId],
    };
    
    return codeBuild.batchGetBuilds(params).promise();
  },
};

module.exports = {
  cognitoAuth,
  textAnalysis,
  buildServices,
};
