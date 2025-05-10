const AWS = require('aws-sdk');
const dynamoDB = new AWS.DynamoDB.DocumentClient();

const MEMORY_TABLE = process.env.MEMORY_TABLE;

exports.handler = async (event) => {
  console.log('Event:', JSON.stringify(event, null, 2));
  
  // Get the HTTP method and path
  const httpMethod = event.httpMethod;
  const path = event.path;
  
  try {
    // Get memory state
    if (httpMethod === 'GET' && path.match(/^\/memory\/[^\/]+$/)) {
      return await getMemoryState(event);
    }
    
    // Update memory state
    if (httpMethod === 'PUT' && path.match(/^\/memory\/[^\/]+$/)) {
      return await updateMemoryState(event);
    }
    
    // Search memory
    if (httpMethod === 'POST' && path.match(/^\/memory\/[^\/]+\/search$/)) {
      return await searchMemory(event);
    }
    
    // Purge memory
    if (httpMethod === 'DELETE' && path.match(/^\/memory\/[^\/]+$/)) {
      return await purgeMemory(event);
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

async function getMemoryState(event) {
  const memoryId = event.pathParameters.memoryId;
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
    TableName: MEMORY_TABLE,
    Key: { memoryId }
  }).promise();
  
  if (!result.Item) {
    return {
      statusCode: 404,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Memory not found',
        resourceType: 'Memory',
        resourceId: memoryId
      })
    };
  }
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      memoryId,
      state: result.Item.state,
      lastUpdated: result.Item.lastUpdated
    })
  };
}

async function updateMemoryState(event) {
  const memoryId = event.pathParameters.memoryId;
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
  
  if (!body.state) {
    return {
      statusCode: 400,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'State is required'
      })
    };
  }
  
  // TODO: Validate token
  
  const mergeStrategy = event.queryStringParameters?.mergeStrategy || 'REPLACE';
  const updatedAt = new Date().toISOString();
  
  // Check if memory exists
  const existingMemory = await dynamoDB.get({
    TableName: MEMORY_TABLE,
    Key: { memoryId }
  }).promise();
  
  let state = body.state;
  
  if (existingMemory.Item && mergeStrategy !== 'REPLACE') {
    if (mergeStrategy === 'MERGE') {
      state = { ...existingMemory.Item.state, ...body.state };
    } else if (mergeStrategy === 'APPEND') {
      // Handle append strategy based on the data structure
      // This is a simplified implementation
      if (Array.isArray(existingMemory.Item.state) && Array.isArray(body.state)) {
        state = [...existingMemory.Item.state, ...body.state];
      } else {
        state = body.state;
      }
    }
  }
  
  await dynamoDB.put({
    TableName: MEMORY_TABLE,
    Item: {
      memoryId,
      state,
      lastUpdated: updatedAt
    }
  }).promise();
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      memoryId,
      updatedAt
    })
  };
}

async function searchMemory(event) {
  const memoryId = event.pathParameters.memoryId;
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
  
  if (!body.query) {
    return {
      statusCode: 400,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Query is required'
      })
    };
  }
  
  // TODO: Validate token
  
  const result = await dynamoDB.get({
    TableName: MEMORY_TABLE,
    Key: { memoryId }
  }).promise();
  
  if (!result.Item) {
    return {
      statusCode: 404,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Memory not found',
        resourceType: 'Memory',
        resourceId: memoryId
      })
    };
  }
  
  // This is a simplified implementation of search
  // In a real implementation, you would use a search engine or more sophisticated search logic
  const searchResults = [];
  const maxResults = event.queryStringParameters?.maxResults || 10;
  
  // Mock search results
  searchResults.push({
    id: 'result-1',
    content: `Result for query: ${body.query}`,
    score: 0.95
  });
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      memoryId,
      results: searchResults,
      searchedAt: new Date().toISOString()
    })
  };
}

async function purgeMemory(event) {
  const memoryId = event.pathParameters.memoryId;
  const token = event.headers['X-Api-Token'];
  const purgeType = event.queryStringParameters?.purgeType || 'FULL';
  
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
  
  if (purgeType === 'FULL') {
    await dynamoDB.delete({
      TableName: MEMORY_TABLE,
      Key: { memoryId }
    }).promise();
  } else if (purgeType === 'PARTIAL') {
    // Implement partial purge logic
    // This is a simplified implementation
    await dynamoDB.update({
      TableName: MEMORY_TABLE,
      Key: { memoryId },
      UpdateExpression: 'SET state = :emptyState',
      ExpressionAttributeValues: {
        ':emptyState': {}
      }
    }).promise();
  }
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      memoryId,
      purgedAt: new Date().toISOString()
    })
  };
}
