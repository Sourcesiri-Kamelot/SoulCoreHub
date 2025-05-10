const AWS = require('aws-sdk');
const dynamoDB = new AWS.DynamoDB.DocumentClient();
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');

const CLIENTS_TABLE = process.env.CLIENTS_TABLE;

exports.handler = async (event) => {
  console.log('Event:', JSON.stringify(event, null, 2));
  
  // Get the HTTP method and path
  const httpMethod = event.httpMethod;
  const path = event.path;
  
  try {
    // Register client
    if (httpMethod === 'POST' && path === '/clients') {
      return await registerClient(event);
    }
    
    // Get client details
    if (httpMethod === 'GET' && path.match(/^\/clients\/[^\/]+$/)) {
      return await getClientDetails(event);
    }
    
    // Authenticate client
    if (httpMethod === 'POST' && path.match(/^\/clients\/[^\/]+\/authenticate$/)) {
      return await authenticateClient(event);
    }
    
    // Update client config
    if (httpMethod === 'PUT' && path.match(/^\/clients\/[^\/]+\/config$/)) {
      return await updateClientConfig(event);
    }
    
    // Handle unknown endpoints
    return {
      statusCode: 404,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Not found'
      })
    };
  } catch (error) {
    console.error('Error:', error);
    
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Internal server error'
      })
    };
  }
};

async function registerClient(event) {
  const body = JSON.parse(event.body);
  
  if (!body.clientName || !body.clientType) {
    return {
      statusCode: 400,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Client name and type are required'
      })
    };
  }
  
  const clientId = uuidv4();
  const apiKey = crypto.randomBytes(32).toString('hex');
  const createdAt = new Date().toISOString();
  
  const client = {
    clientId,
    clientName: body.clientName,
    clientType: body.clientType,
    apiKey,
    createdAt,
    lastActive: createdAt
  };
  
  if (body.callbackUrl) {
    client.callbackUrl = body.callbackUrl;
  }
  
  if (body.metadata) {
    client.metadata = body.metadata;
  }
  
  await dynamoDB.put({
    TableName: CLIENTS_TABLE,
    Item: client
  }).promise();
  
  return {
    statusCode: 201,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      clientId,
      apiKey,
      createdAt
    })
  };
}

async function getClientDetails(event) {
  const clientId = event.pathParameters.clientId;
  
  const result = await dynamoDB.get({
    TableName: CLIENTS_TABLE,
    Key: { clientId }
  }).promise();
  
  if (!result.Item) {
    return {
      statusCode: 404,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Client not found',
        resourceType: 'Client',
        resourceId: clientId
      })
    };
  }
  
  const client = result.Item;
  
  // Don't return the API key
  delete client.apiKey;
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(client)
  };
}

async function authenticateClient(event) {
  const clientId = event.pathParameters.clientId;
  const body = JSON.parse(event.body);
  
  if (!body.apiKey) {
    return {
      statusCode: 400,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'API key is required'
      })
    };
  }
  
  const result = await dynamoDB.get({
    TableName: CLIENTS_TABLE,
    Key: { clientId }
  }).promise();
  
  if (!result.Item) {
    return {
      statusCode: 404,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Client not found',
        resourceType: 'Client',
        resourceId: clientId
      })
    };
  }
  
  if (result.Item.apiKey !== body.apiKey) {
    return {
      statusCode: 401,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Invalid API key'
      })
    };
  }
  
  // Update last active timestamp
  await dynamoDB.update({
    TableName: CLIENTS_TABLE,
    Key: { clientId },
    UpdateExpression: 'SET lastActive = :lastActive',
    ExpressionAttributeValues: {
      ':lastActive': new Date().toISOString()
    }
  }).promise();
  
  // Generate a token that expires in 24 hours
  const expiresAt = new Date();
  expiresAt.setHours(expiresAt.getHours() + 24);
  
  const token = crypto.randomBytes(64).toString('hex');
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      token,
      expiresAt: expiresAt.toISOString()
    })
  };
}

async function updateClientConfig(event) {
  const clientId = event.pathParameters.clientId;
  const body = JSON.parse(event.body);
  
  const result = await dynamoDB.get({
    TableName: CLIENTS_TABLE,
    Key: { clientId }
  }).promise();
  
  if (!result.Item) {
    return {
      statusCode: 404,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Client not found',
        resourceType: 'Client',
        resourceId: clientId
      })
    };
  }
  
  const updateExpressions = [];
  const expressionAttributeValues = {};
  
  if (body.clientName) {
    updateExpressions.push('clientName = :clientName');
    expressionAttributeValues[':clientName'] = body.clientName;
  }
  
  if (body.callbackUrl) {
    updateExpressions.push('callbackUrl = :callbackUrl');
    expressionAttributeValues[':callbackUrl'] = body.callbackUrl;
  }
  
  if (body.metadata) {
    updateExpressions.push('metadata = :metadata');
    expressionAttributeValues[':metadata'] = body.metadata;
  }
  
  if (updateExpressions.length === 0) {
    return {
      statusCode: 400,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'No updates provided'
      })
    };
  }
  
  updateExpressions.push('updatedAt = :updatedAt');
  expressionAttributeValues[':updatedAt'] = new Date().toISOString();
  
  await dynamoDB.update({
    TableName: CLIENTS_TABLE,
    Key: { clientId },
    UpdateExpression: 'SET ' + updateExpressions.join(', '),
    ExpressionAttributeValues: expressionAttributeValues
  }).promise();
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      clientId,
      updatedAt: expressionAttributeValues[':updatedAt']
    })
  };
}
