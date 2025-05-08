const AWS = require('aws-sdk');
const dynamoDB = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
  // Set up CORS headers for frontend access
  const headers = {
    'Access-Control-Allow-Origin': '*', // Update with your domain in production
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,OPTIONS'
  };
  
  // Handle preflight OPTIONS request
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ message: 'CORS preflight successful' })
    };
  }
  
  try {
    // Get userId from query parameters, JWT token, or session
    let userId;
    
    // Check query parameters first (for testing and overrides)
    if (event.queryStringParameters && event.queryStringParameters.userId) {
      userId = event.queryStringParameters.userId;
    } 
    // Check authorization header for JWT token
    else if (event.headers && event.headers.Authorization) {
      // In a real implementation, you would decode the JWT token
      // For this example, we'll assume the userId is extracted from the token
      userId = extractUserIdFromToken(event.headers.Authorization);
    }
    
    // If no userId found, return 400 Bad Request
    if (!userId) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Missing userId parameter' })
      };
    }
    
    // Check for plan override (for developer testing)
    const planOverride = event.queryStringParameters?.plan;
    if (planOverride) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          userPlan: planOverride,
          stripeCustomerId: 'override_mode',
          isOverride: true
        })
      };
    }
    
    // Query DynamoDB for user subscription
    const params = {
      TableName: 'UserSubscriptions',
      Key: { userId }
    };
    
    const result = await dynamoDB.get(params).promise();
    
    // If user found, return their plan info
    if (result.Item) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          userPlan: result.Item.planId,
          stripeCustomerId: result.Item.stripeCustomerId
        })
      };
    }
    
    // If user not found, return default "free" plan
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        userPlan: 'free',
        stripeCustomerId: null
      })
    };
    
  } catch (error) {
    console.error('Error retrieving user plan:', error);
    
    // Return error response
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        error: 'Failed to retrieve user plan',
        message: error.message
      })
    };
  }
};

// Helper function to extract userId from JWT token
function extractUserIdFromToken(authHeader) {
  // In a real implementation, you would decode the JWT token
  // For this example, we'll return a placeholder
  return 'user123';
}
