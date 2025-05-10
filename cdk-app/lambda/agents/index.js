const AWS = require('aws-sdk');
const dynamoDB = new AWS.DynamoDB.DocumentClient();
const { v4: uuidv4 } = require('uuid');

const AGENTS_TABLE = process.env.AGENTS_TABLE;

exports.handler = async (event) => {
  console.log('Event:', JSON.stringify(event, null, 2));
  
  // Get the HTTP method and path
  const httpMethod = event.httpMethod;
  const path = event.path;
  
  try {
    // Get agent status
    if (httpMethod === 'GET' && path.match(/^\/agents\/[^\/]+\/status$/)) {
      return await getAgentStatus(event);
    }
    
    // Invoke agent
    if (httpMethod === 'POST' && path.match(/^\/agents\/[^\/]+\/invoke$/)) {
      return await invokeAgent(event);
    }
    
    // Update agent config
    if (httpMethod === 'PUT' && path.match(/^\/agents\/[^\/]+\/config$/)) {
      return await updateAgentConfig(event);
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

async function getAgentStatus(event) {
  const agentId = event.pathParameters.agentId;
  
  const result = await dynamoDB.get({
    TableName: AGENTS_TABLE,
    Key: { agentId }
  }).promise();
  
  if (!result.Item) {
    return {
      statusCode: 404,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Agent not found',
        resourceType: 'Agent',
        resourceId: agentId
      })
    };
  }
  
  const agent = result.Item;
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      agentId: agent.agentId,
      agentName: agent.agentName,
      status: agent.status,
      lastActive: agent.lastActive,
      capabilities: agent.capabilities,
      metadata: agent.metadata
    })
  };
}

async function invokeAgent(event) {
  const agentId = event.pathParameters.agentId;
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
  
  if (!body.action) {
    return {
      statusCode: 400,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Action is required'
      })
    };
  }
  
  // TODO: Validate token
  
  const result = await dynamoDB.get({
    TableName: AGENTS_TABLE,
    Key: { agentId }
  }).promise();
  
  if (!result.Item) {
    return {
      statusCode: 404,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Agent not found',
        resourceType: 'Agent',
        resourceId: agentId
      })
    };
  }
  
  const agent = result.Item;
  
  if (agent.status !== 'ACTIVE') {
    return {
      statusCode: 400,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Agent is not active',
        agentId,
        errorCode: 'AGENT_NOT_ACTIVE',
        details: {
          currentStatus: agent.status
        }
      })
    };
  }
  
  // Update last active timestamp
  await dynamoDB.update({
    TableName: AGENTS_TABLE,
    Key: { agentId },
    UpdateExpression: 'SET lastActive = :lastActive',
    ExpressionAttributeValues: {
      ':lastActive': new Date().toISOString()
    }
  }).promise();
  
  // Process the action
  // This is a simplified implementation
  const invocationId = uuidv4();
  const invokedAt = new Date().toISOString();
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      invocationId,
      result: {
        status: 'SUCCESS',
        data: `Executed action: ${body.action}`
      },
      invokedAt
    })
  };
}

async function updateAgentConfig(event) {
  const agentId = event.pathParameters.agentId;
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
    TableName: AGENTS_TABLE,
    Key: { agentId }
  }).promise();
  
  if (!result.Item) {
    return {
      statusCode: 404,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Agent not found',
        resourceType: 'Agent',
        resourceId: agentId
      })
    };
  }
  
  const updateExpressions = [];
  const expressionAttributeValues = {};
  
  if (body.agentName) {
    updateExpressions.push('agentName = :agentName');
    expressionAttributeValues[':agentName'] = body.agentName;
  }
  
  if (body.capabilities) {
    updateExpressions.push('capabilities = :capabilities');
    expressionAttributeValues[':capabilities'] = body.capabilities;
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
    TableName: AGENTS_TABLE,
    Key: { agentId },
    UpdateExpression: 'SET ' + updateExpressions.join(', '),
    ExpressionAttributeValues: expressionAttributeValues
  }).promise();
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      agentId,
      updatedAt: expressionAttributeValues[':updatedAt']
    })
  };
}
