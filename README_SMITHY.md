# SoulCoreHub Smithy Integration

This document provides a comprehensive guide to the Smithy integration in SoulCoreHub. Smithy is used to define the API model in a language-agnostic way, enabling consistent API implementations across multiple platforms.

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [API Model](#api-model)
4. [Client SDKs](#client-sdks)
5. [Lambda Handlers](#lambda-handlers)
6. [GitLab CI/CD Integration](#gitlab-cicd-integration)
7. [Usage Guide](#usage-guide)

## Overview

Smithy is AWS's Interface Definition Language (IDL) that allows you to define APIs in a language-agnostic way. In SoulCoreHub, we use Smithy to:

- Define our API model in a single source of truth
- Generate client SDKs for multiple languages (TypeScript, Python, etc.)
- Generate server-side code for AWS Lambda handlers
- Generate OpenAPI specifications for API Gateway
- Ensure consistent API behavior across all platforms

## Project Structure

The Smithy integration is organized as follows:

```
smithy/
├── build.gradle           # Gradle build file for Smithy
├── settings.gradle        # Gradle settings
├── smithy-build.json      # Smithy build configuration
├── model/                 # Smithy model files
│   └── soulcorehub.smithy # Main API model
├── handlers/              # Lambda handlers
│   ├── build.gradle       # Gradle build file for handlers
│   └── src/               # Handler source code
└── integration/           # Integration tests
```

## API Model

The API model is defined in `smithy/model/soulcorehub.smithy`. It includes:

- **Service Definition**: The main SoulCoreHub API service
- **Operations**: API operations like GetAgent, InvokeAgent, etc.
- **Structures**: Input and output structures for operations
- **Error Types**: Standard error responses

The model is organized into logical sections:

1. **Agent Operations**: Operations for managing and invoking agents
2. **Content Operations**: Operations for managing content
3. **Commerce Operations**: Operations for managing products
4. **Cultural Operations**: Operations for managing worlds and worldbuilding
5. **System Operations**: Operations for system management

## Client SDKs

Smithy generates client SDKs for multiple languages:

### TypeScript Client

The TypeScript client is generated for frontend applications:

```typescript
import { SoulCoreHubClient } from '@soulcorehub/api-client';

const client = new SoulCoreHubClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.soulcorehub.com'
});

// Invoke an agent
const response = await client.invokeAgent({
  agentId: 'gptsoul-1',
  prompt: 'Hello, GPTSoul!'
});

console.log(response.response);
```

### Python Client

The Python client is generated for CLI and backend applications:

```python
from soulcorehub_api_client import SoulCoreHubClient

client = SoulCoreHubClient(
    api_key='your-api-key',
    base_url='https://api.soulcorehub.com'
)

# Invoke an agent
response = client.invoke_agent(
    agent_id='gptsoul-1',
    prompt='Hello, GPTSoul!'
)

print(response.response)
```

## Lambda Handlers

Lambda handlers are implemented for each API operation. They follow a consistent pattern:

1. Receive the input structure from API Gateway
2. Validate the input
3. Process the request (e.g., query DynamoDB, invoke an agent)
4. Return the output structure

Example handler for GetAgent:

```java
public class GetAgentHandler implements RequestHandler<GetAgentInput, GetAgentOutput> {
    @Override
    public GetAgentOutput handleRequest(GetAgentInput input, Context context) {
        // Validate input
        if (input.getAgentId() == null || input.getAgentId().isEmpty()) {
            throw new IllegalArgumentException("Agent ID cannot be null or empty");
        }
        
        // Get agent from DynamoDB
        Agent agent = getAgentFromDynamoDB(input.getAgentId());
        
        // Return output
        GetAgentOutput output = new GetAgentOutput();
        output.setAgent(agent);
        return output;
    }
}
```

## GitLab CI/CD Integration

The GitLab CI/CD pipeline is configured to:

1. Validate the Smithy model
2. Generate client SDKs
3. Build and test the Lambda handlers
4. Deploy the API to AWS

The pipeline is defined in `.gitlab-ci.yml` and includes stages for:

- **Validate**: Validate the Smithy model
- **Build**: Build the Lambda handlers and generate client SDKs
- **Test**: Run tests for the Lambda handlers and client SDKs
- **Package**: Package the Lambda handlers for deployment
- **Deploy**: Deploy the API to AWS

## Usage Guide

### Building the Smithy Model

To build the Smithy model and generate client SDKs:

```bash
cd smithy
./gradlew smithyBuild
```

This will:
- Validate the Smithy model
- Generate OpenAPI specifications
- Generate client SDKs for TypeScript and Python

### Deploying the API

To deploy the API to AWS:

```bash
cd smithy
./gradlew deploy
```

This will:
- Build the Lambda handlers
- Package the Lambda handlers
- Deploy the API to AWS using CloudFormation

### Using the CLI

The CLI is built on top of the Python client SDK:

```bash
# List agents
./cli/soulcore.py agent list

# Invoke an agent
./cli/soulcore.py agent invoke gptsoul-1 "Hello, GPTSoul!"

# Get system status
./cli/soulcore.py system status
```

### Using the Terminal UI

The Terminal UI provides a command-line interface for interacting with SoulCoreHub:

```bash
# Open the terminal UI
./cli/soulcore.py system terminal
```

This will open a terminal interface where you can enter commands:

```
SoulCoreHub Terminal v1.0.0
Type "help" for available commands

$ agent invoke gptsoul-1 "Hello, GPTSoul!"
As GPTSoul, I am here to guide and assist. Your query about "Hello, GPTSoul!" is important.
I would recommend approaching this with strategic thinking and careful planning.
Remember that every challenge is an opportunity for growth and innovation.

Tokens: 75 (prompt: 5, completion: 70)
Processing time: 523 ms
```

## Conclusion

The Smithy integration provides a robust foundation for the SoulCoreHub API. By defining the API model in a language-agnostic way, we ensure consistent behavior across all platforms and enable rapid development of new features.
