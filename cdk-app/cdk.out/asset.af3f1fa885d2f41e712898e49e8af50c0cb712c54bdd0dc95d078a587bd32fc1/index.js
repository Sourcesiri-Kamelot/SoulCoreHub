exports.handler = async (event) => {
  console.log('Event:', JSON.stringify(event, null, 2));
  
  // Get the HTTP method and path
  const httpMethod = event.httpMethod;
  const path = event.path;
  
  // Handle status endpoint
  if (httpMethod === 'GET' && path === '/status') {
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        status: 'ACTIVE',
        version: '1.0.0',
        uptime: 1000,
        activeAgents: 5,
        activeClients: 10,
        memoryUsage: 0.75,
        systemMessages: ['System is operational', 'All services running']
      })
    };
  }
  
  // Handle execute endpoint
  if (httpMethod === 'POST' && path === '/execute') {
    try {
      const body = JSON.parse(event.body);
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
      
      if (!body.command) {
        return {
          statusCode: 400,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message: 'Command is required'
          })
        };
      }
      
      // Process the command
      const result = {
        executionId: 'exec-' + Date.now(),
        result: {
          status: 'SUCCESS',
          data: `Executed command: ${body.command}`
        },
        executedAt: new Date().toISOString()
      };
      
      return {
        statusCode: 200,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(result)
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
};
