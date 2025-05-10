# SoulCoreHub Smithy API Model

This directory contains the Smithy API model for SoulCoreHub. The model defines the API endpoints, resources, and data structures used by the SoulCoreHub service.

## Directory Structure

- `model/`: Contains the Smithy model files
  - `soulcorehub-service.smithy`: Main API model for SoulCoreHub
  - `soulcorehub-apps.smithy`: API model for SoulCoreHub Apps
  - `soulcorehub-common.smithy`: Common types and structures
- `dependencies/`: Contains Smithy dependencies
  - `api.smithy`: AWS API traits
  - `auth.smithy`: AWS Auth traits
  - `protocols.smithy`: AWS Protocol traits
  - `validation.smithy`: Smithy validation framework
  - `http.smithy`: HTTP traits
  - `traits.smithy`: Additional traits

## Building the Model

To validate the model, run:

```bash
smithy validate model/
```

## API Overview

### SoulCoreHub API

The main SoulCoreHub API provides endpoints for:

- Client management
- Memory state management
- Agent management
- Command execution

### SoulCoreHub Apps API

The SoulCoreHub Apps API provides endpoints for:

- App management
- App function invocation

## AWS CDK Integration

The API model is used to generate AWS CDK code for deploying the API to AWS. The CDK code is located in the `cdk-app` directory.

## Domain Integration

The API is deployed to the `soulcorehub.io` domain using AWS Route 53 and AWS Certificate Manager.

## Security

The API uses SigV4 authentication and API keys for security. All endpoints require authentication except for the status endpoint.

## Deployment

The API is deployed using AWS CodePipeline and AWS CodeBuild. The deployment pipeline is defined in the `cdk-app/lib/codecatalyst-stack.ts` file.
