# SoulCoreHub AWS SAM Deployment Guide

This guide explains how to deploy SoulCoreHub components to AWS using the Serverless Application Model (SAM).

## 🧠 Overview

SoulCoreHub has been integrated with AWS SAM to enable serverless deployment of its core components. Each agent and service can be deployed as an independent Lambda function, allowing for scalable, maintainable, and cost-effective operation in the cloud.

## 🚀 Quick Start

```bash
# Build the application
./sam_build.sh

# Deploy to AWS
./sam_deploy.sh

# Update frontend code with API endpoint
python update_frontend.py
```

## 📋 Components

The following Lambda functions are defined in the SAM template:

### AnimaLambda

**Purpose**: Wraps the Anima emotional core as a serverless function.

**Functionality**:
- Processes emotional and reflective responses
- Maintains emotional state in DynamoDB
- Stores conversation history in S3
- Provides a REST API endpoint for emotional processing

**Testing**:
```bash
# Test locally
sam local invoke AnimaLambda -e functions/anima/event.json

# Test API endpoint
curl -X POST http://localhost:3000/anima \
  -H "Content-Type: application/json" \
  -d '{"input":"I feel happy today","session_id":"test-123"}'
```

### GPTSoulLambda

**Purpose**: Provides the GPTSoul guardian and architect capabilities as a serverless function.

**Functionality**:
- Processes strategic and executive responses
- Maintains memory state in S3
- Provides system oversight and architecture guidance
- Exposes a REST API endpoint for system management

**Testing**:
```bash
# Test locally
sam local invoke GPTSoulLambda -e functions/gptsoul/event.json

# Test API endpoint
curl -X POST http://localhost:3000/gptsoul \
  -H "Content-Type: application/json" \
  -d '{"input":"What is the system status?","session_id":"test-123"}'
```

### NeuralRouterLambda

**Purpose**: Routes user input to the appropriate agent or MCP server.

**Functionality**:
- Analyzes user input to determine the best handler
- Routes requests to the appropriate Lambda function
- Logs routing decisions for analytics
- Provides a central entry point for the SoulCore system

**Testing**:
```bash
# Test locally
sam local invoke NeuralRouterLambda -e functions/neural_router/event.json

# Test API endpoint
curl -X POST http://localhost:3000/route \
  -H "Content-Type: application/json" \
  -d '{"input":"I need to reflect on my emotions","session_id":"test-123"}'
```

### MemorySyncLambda

**Purpose**: Manages memory operations for all SoulCore agents.

**Functionality**:
- Reads, writes, and updates agent memory in S3
- Creates memory backups
- Provides a centralized memory management API
- Ensures memory consistency across the system

**Testing**:
```bash
# Test locally
sam local invoke MemorySyncLambda -e functions/memory_sync/event.json

# Test API endpoint - Read memory
curl -X POST http://localhost:3000/memory \
  -H "Content-Type: application/json" \
  -d '{"operation":"read","agent_id":"anima"}'

# Test API endpoint - Write memory
curl -X POST http://localhost:3000/memory \
  -H "Content-Type: application/json" \
  -d '{"operation":"write","agent_id":"anima","memory_data":{"key":"value"}}'
```

### ResurrectionLambda

**Purpose**: Handles agent recovery and resurrection.

**Functionality**:
- Detects when agents need resurrection
- Implements different resurrection protocols (standard, clean, deep)
- Restores from backups when possible
- Logs resurrection events for analysis

**Testing**:
```bash
# Test locally
sam local invoke ResurrectionLambda -e functions/resurrection/event.json

# Test API endpoint
curl -X POST http://localhost:3000/resurrect \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"anima","type":"standard","force":true}'
```

### SoulCoreDashboardLambda

**Purpose**: Serves the SoulCore dashboard web interface.

**Functionality**:
- Provides a web-based dashboard for monitoring agents
- Displays agent status, memory, and logs
- Allows manual resurrection of agents
- Serves static assets and API endpoints for the dashboard

**Testing**:
```bash
# Test locally
sam local invoke SoulCoreDashboardLambda -e functions/dashboard/event.json

# Access the dashboard
open http://localhost:3000/
```

## 🚀 Deployment Instructions

### Prerequisites

1. Install AWS SAM CLI:
   ```bash
   # For macOS
   brew tap aws/tap
   brew install aws-sam-cli
   
   # For other platforms, see:
   # https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html
   ```

2. Configure AWS credentials:
   ```bash
   aws configure
   ```

### Building the Application

```bash
# Build all functions
./sam_build.sh
```

### Testing Locally

```bash
# Start the local API for testing
./sam_local_test.sh

# In another terminal, test the API endpoints
curl -X POST http://localhost:3000/anima \
  -H "Content-Type: application/json" \
  -d '{"input":"Hello Anima","session_id":"test-123"}'
```

### Deploying to AWS

```bash
# Deploy all functions
./sam_deploy.sh

# Or use the soulcloud CLI to deploy individual components
python soulcloud.py deploy anima
```

## 📊 Monitoring and Logs

### Using the SoulCloud CLI

```bash
# Check status of all components
python soulcloud.py status

# View logs for a specific component
python soulcloud.py logs anima

# Tail logs in real-time
python soulcloud.py logs anima --tail
```

### Using the AWS Console

1. Open the [AWS Lambda Console](https://console.aws.amazon.com/lambda)
2. Select the region where you deployed SoulCoreHub
3. Find and select the Lambda function you want to monitor
4. Click on the "Monitor" tab to view metrics and logs

## 🔄 Integrating with the SoulCore UI

To route queries from the SoulCore UI to your AWS Lambda functions:

1. Update the API endpoint in your frontend code:

```javascript
// Example: Update the API endpoint in public/soul_command_center.html
const API_ENDPOINT = 'https://your-api-id.execute-api.your-region.amazonaws.com/prod';

async function sendToAnima(input) {
  const response = await fetch(`${API_ENDPOINT}/anima`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      input: input,
      session_id: getCurrentSessionId()
    })
  });
  
  return await response.json();
}
```

2. Use the provided script to automatically update your frontend code:

```bash
# Update all frontend files with the deployed API endpoint
python update_frontend.py
```

## 🌐 Custom Domain Setup

To set up a custom domain for your SoulCoreHub deployment:

1. Create an SSL certificate in AWS Certificate Manager (ACM):
   - Go to the ACM console in the `us-east-1` region
   - Request a public certificate for your domain (e.g., `soulcore.heloim-ai.tech`)
   - Complete the validation process

2. Deploy with the custom domain:
   - Run `./sam_deploy.sh` and choose to set up a custom domain
   - Enter your domain name and certificate ARN when prompted

3. Configure DNS:
   - Add a CNAME record pointing to the API Gateway domain
   - For detailed instructions, see `DOMAIN_SETUP.md`

## 🤖 CI/CD Setup

To set up continuous integration and deployment:

1. Create a GitHub repository for your SoulCoreHub project
2. Add your AWS credentials as GitHub secrets
3. Copy the `setup_ci_cd.yml` file to `.github/workflows/deploy.yml`
4. Push your code to GitHub to trigger the workflow

For detailed instructions, see `GITHUB_ACTIONS_SETUP.md`

## 🧩 Customizing Lambda Functions

Each Lambda function is designed to be a thin wrapper around your existing SoulCoreHub code. To customize a function:

1. Edit the corresponding file in the `functions/` directory
2. Update the handler function to integrate with your specific code
3. Rebuild and redeploy using the provided scripts

Example: Customizing the Anima Lambda to use your actual Anima code:

```python
# functions/anima/app.py

# Import your actual Anima code
sys.path.append('/var/task')
from anima_autonomous import AnimaCore
from anima_memory_bridge import MemoryBridge

def process_anima_request(user_input, emotional_state):
    # Initialize your actual Anima components
    memory_bridge = MemoryBridge()
    anima_core = AnimaCore(memory_bridge)
    
    # Process the request using your actual code
    response = anima_core.process_input(user_input, emotional_state)
    
    return {
        'response': response.get('text'),
        'emotional_state': response.get('emotional_state')
    }
```

## 📦 Resource Management

The SAM template creates the following AWS resources:

- Lambda functions for each SoulCore component
- API Gateway for REST endpoints
- S3 bucket for memory storage
- DynamoDB table for emotional state tracking

To customize these resources, edit the `template.yaml` file and redeploy.

## 🔒 Security Considerations

- The template includes basic IAM permissions for each function
- For production, consider adding authentication to the API Gateway
- Review and restrict the IAM permissions as needed
- Consider encrypting sensitive data in S3 and DynamoDB

## 🤝 Need Help?

If you encounter any issues with the SAM deployment:

1. Check the CloudFormation events for deployment errors:
   ```bash
   aws cloudformation describe-stack-events --stack-name soulcore-hub
   ```

2. View the Lambda function logs:
   ```bash
   python soulcloud.py logs anima
   ```

3. Test the function locally to debug issues:
   ```bash
   sam local invoke AnimaLambda -e functions/anima/event.json
   ```
