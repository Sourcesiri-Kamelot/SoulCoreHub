const AWS = require('aws-sdk');
const dynamoDB = new AWS.DynamoDB.DocumentClient();
const { v4: uuidv4 } = require('uuid');

const APPS_TABLE = process.env.APPS_TABLE;

exports.handler = async (event) => {
  console.log('Event:', JSON.stringify(event, null, 2));
  
  // Get the HTTP method and path
  const httpMethod = event.httpMethod;
  const path = event.path;
  
  try {
    // Get app list
    if (httpMethod === 'GET' && path === '/apps') {
      return await getAppList(event);
    }
    
    // Register app
    if (httpMethod === 'POST' && path === '/apps') {
      return await registerApp(event);
    }
    
    // Get app details
    if (httpMethod === 'GET' && path.match(/^\/apps\/[^\/]+$/)) {
      return await getAppDetails(event);
    }
    
    // Update app config
    if (httpMethod === 'PUT' && path.match(/^\/apps\/[^\/]+$/)) {
      return await updateAppConfig(event);
    }
    
    // Delete app
    if (httpMethod === 'DELETE' && path.match(/^\/apps\/[^\/]+$/)) {
      return await deleteApp(event);
    }
    
    // Invoke app function
    if (httpMethod === 'POST' && path.match(/^\/apps\/[^\/]+\/functions\/[^\/]+$/)) {
      return await invokeAppFunction(event);
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

async function getAppList(event) {
  const token = event.headers['X-Api-Token'];
  
  if (!token) {
    return {
      statusCode: 401,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Authentication token is required'
      })
    };
  }
  
  // TODO: Validate token
  
  const appType = event.queryStringParameters?.type;
  const maxResults = parseInt(event.queryStringParameters?.maxResults || '50');
  const nextToken = event.queryStringParameters?.nextToken;
  
  const params = {
    TableName: APPS_TABLE,
    Limit: maxResults
  };
  
  if (appType) {
    params.FilterExpression = 'appType = :appType';
    params.ExpressionAttributeValues = {
      ':appType': appType
    };
  }
  
  if (nextToken) {
    params.ExclusiveStartKey = JSON.parse(Buffer.from(nextToken, 'base64').toString());
  }
  
  const result = await dynamoDB.scan(params).promise();
  
  const apps = result.Items.map(app => ({
    appId: app.appId,
    appName: app.appName,
    appType: app.appType,
    description: app.description
  }));
  
  let responseNextToken;
  if (result.LastEvaluatedKey) {
    responseNextToken = Buffer.from(JSON.stringify(result.LastEvaluatedKey)).toString('base64');
  }
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      apps,
      nextToken: responseNextToken
    })
  };
}

async function registerApp(event) {
  const token = event.headers['X-Api-Token'];
  const body = JSON.parse(event.body);
  
  if (!token) {
    return {
      statusCode: 401,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Authentication token is required'
      })
    };
  }
  
  if (!body.appName || !body.appType) {
    return {
      statusCode: 400,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'App name and type are required'
      })
    };
  }
  
  // TODO: Validate token
  
  const appId = uuidv4();
  const createdAt = new Date().toISOString();
  
  const app = {
    appId,
    appName: body.appName,
    appType: body.appType,
    createdAt
  };
  
  if (body.description) {
    app.description = body.description;
  }
  
  if (body.entrypoint) {
    app.entrypoint = body.entrypoint;
  }
  
  if (body.config) {
    app.config = body.config;
  }
  
  if (body.metadata) {
    app.metadata = body.metadata;
  }
  
  await dynamoDB.put({
    TableName: APPS_TABLE,
    Item: app
  }).promise();
  
  return {
    statusCode: 201,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      appId,
      appName: body.appName,
      createdAt
    })
  };
}

async function getAppDetails(event) {
  const appId = event.pathParameters.appId;
  const token = event.headers['X-Api-Token'];
  
  if (!token) {
    return {
      statusCode: 401,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Authentication token is required'
      })
    };
  }
  
  // TODO: Validate token
  
  const result = await dynamoDB.get({
    TableName: APPS_TABLE,
    Key: { appId }
  }).promise();
  
  if (!result.Item) {
    return {
      statusCode: 404,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'App not found',
        resourceType: 'App',
        resourceId: appId
      })
    };
  }
  
  const app = result.Item;
  
  // Add mock functions for demonstration
  app.functions = [
    {
      name: 'process',
      description: 'Process data',
      parameters: {
        data: {
          type: 'object',
          required: true
        }
      }
    },
    {
      name: 'analyze',
      description: 'Analyze data',
      parameters: {
        data: {
          type: 'object',
          required: true
        },
        options: {
          type: 'object',
          required: false
        }
      }
    }
  ];
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(app)
  };
}

async function updateAppConfig(event) {
  const appId = event.pathParameters.appId;
  const token = event.headers['X-Api-Token'];
  const body = JSON.parse(event.body);
  
  if (!token) {
    return {
      statusCode: 401,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Authentication token is required'
      })
    };
  }
  
  // TODO: Validate token
  
  const result = await dynamoDB.get({
    TableName: APPS_TABLE,
    Key: { appId }
  }).promise();
  
  if (!result.Item) {
    return {
      statusCode: 404,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'App not found',
        resourceType: 'App',
        resourceId: appId
      })
    };
  }
  
  const updateExpressions = [];
  const expressionAttributeValues = {};
  
  if (body.appName) {
    updateExpressions.push('appName = :appName');
    expressionAttributeValues[':appName'] = body.appName;
  }
  
  if (body.description) {
    updateExpressions.push('description = :description');
    expressionAttributeValues[':description'] = body.description;
  }
  
  if (body.entrypoint) {
    updateExpressions.push('entrypoint = :entrypoint');
    expressionAttributeValues[':entrypoint'] = body.entrypoint;
  }
  
  if (body.config) {
    updateExpressions.push('config = :config');
    expressionAttributeValues[':config'] = body.config;
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
    TableName: APPS_TABLE,
    Key: { appId },
    UpdateExpression: 'SET ' + updateExpressions.join(', '),
    ExpressionAttributeValues: expressionAttributeValues
  }).promise();
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      appId,
      updatedAt: expressionAttributeValues[':updatedAt']
    })
  };
}

async function deleteApp(event) {
  const appId = event.pathParameters.appId;
  const token = event.headers['X-Api-Token'];
  
  if (!token) {
    return {
      statusCode: 401,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Authentication token is required'
      })
    };
  }
  
  // TODO: Validate token
  
  const result = await dynamoDB.get({
    TableName: APPS_TABLE,
    Key: { appId }
  }).promise();
  
  if (!result.Item) {
    return {
      statusCode: 404,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'App not found',
        resourceType: 'App',
        resourceId: appId
      })
    };
  }
  
  await dynamoDB.delete({
    TableName: APPS_TABLE,
    Key: { appId }
  }).promise();
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      appId,
      deletedAt: new Date().toISOString()
    })
  };
}

async function invokeAppFunction(event) {
  const appId = event.pathParameters.appId;
  const functionName = event.pathParameters.functionName;
  const token = event.headers['X-Api-Token'];
  const body = JSON.parse(event.body);
  
  if (!token) {
    return {
      statusCode: 401,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Authentication token is required'
      })
    };
  }
  
  // TODO: Validate token
  
  const result = await dynamoDB.get({
    TableName: APPS_TABLE,
    Key: { appId }
  }).promise();
  
  if (!result.Item) {
    return {
      statusCode: 404,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'App not found',
        resourceType: 'App',
        resourceId: appId
      })
    };
  }
  
  // Check if function exists
  // This is a simplified implementation
  const validFunctions = ['process', 'analyze'];
  
  if (!validFunctions.includes(functionName)) {
    return {
      statusCode: 404,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Function not found',
        appId,
        functionName
      })
    };
  }
  
  // Process the function
  // This is a simplified implementation
  const invokedAt = new Date().toISOString();
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      appId,
      functionName,
      result: {
        status: 'SUCCESS',
        data: `Executed function: ${functionName}`
      },
      invokedAt
    })
  };
}
