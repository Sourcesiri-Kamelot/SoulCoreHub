# SoulCoreHub AWS SAM & Stripe Integration

This document outlines how to use the AWS SAM integration with Stripe metered billing in SoulCoreHub.

## Overview

SoulCoreHub now includes a complete AWS SAM integration with Stripe metered billing capabilities. This allows you to:

1. Deploy serverless applications using AWS SAM
2. Track usage with Stripe's metered billing
3. Chain Lambda functions with S3, DynamoDB, and EventBridge
4. Manage all of this through Anima's command system

## Prerequisites

- AWS CLI configured (`aws configure`)
- AWS SAM CLI installed
- Stripe account with API keys
- SoulCoreHub environment set up

## Setup

### 1. Configure AWS Credentials

Make sure your AWS credentials are properly configured:

```bash
aws configure
```

### 2. Set Up Stripe API Keys

Create a `.env` file in the project root with your Stripe API keys:

```
STRIPE_API_KEY=sk_test_your_test_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

Or add them to AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
    --name SoulCoreSecrets \
    --secret-string '{"STRIPE_API_KEY":"sk_test_your_test_key","STRIPE_WEBHOOK_SECRET":"whsec_your_webhook_secret"}'
```

### 3. Add Stripe Billing to SAM Template

```bash
python anima_builder_sam.py add-stripe
```

## Usage

### Using the SAM Script Runner

The `sam_script_runner.sh` script provides a unified interface for AWS SAM commands:

```bash
# Initialize a new SAM application
./scripts/sam_script_runner.sh init

# Build the SAM application
./scripts/sam_script_runner.sh build

# Deploy the SAM application to AWS
./scripts/sam_script_runner.sh deploy

# Run the application locally
./scripts/sam_script_runner.sh local

# View Lambda function logs
./scripts/sam_script_runner.sh logs function-name

# Validate the SAM template
./scripts/sam_script_runner.sh validate

# Record Stripe usage
./scripts/sam_script_runner.sh stripe user_id=123 units=5 reason="api_call"
```

### Using Anima Builder SAM

The `anima_builder_sam.py` script provides a Python interface for AWS SAM commands:

```bash
# Initialize a new SAM application
python anima_builder_sam.py init

# Build the SAM application
python anima_builder_sam.py build

# Deploy the SAM application to AWS
python anima_builder_sam.py deploy

# Run the application locally
python anima_builder_sam.py local

# View Lambda function logs
python anima_builder_sam.py logs function-name

# Validate the SAM template
python anima_builder_sam.py validate

# Record Stripe usage
python anima_builder_sam.py stripe --user_id 123 --units 5 --reason "api_call"

# Add Stripe billing function to the SAM template
python anima_builder_sam.py add-stripe

# Create Lambda chaining example
python anima_builder_sam.py create-chaining
```

### Using Anima Commands

You can use the SAM commands directly from Anima:

```
anima sam_init
anima sam_build
anima sam_deploy
anima sam_local
anima sam_logs function-name
anima sam_validate
anima sam_stripe user_id=123 units=5 reason="api_call"
anima sam_add_stripe
anima sam_create_chaining
```

## Stripe Metered Billing

The Stripe billing integration allows you to track usage for metered subscriptions:

1. Create a subscription in Stripe with a metered plan
2. Store the subscription details in DynamoDB
3. Record usage as users interact with your application

### Recording Usage

```python
# Using the Anima Builder SAM
from anima_builder_sam import AnimaBuilderSAM

builder = AnimaBuilderSAM()
builder.record_stripe_usage(user_id="123", units=5, reason="api_call")
```

```bash
# Using the SAM Script Runner
./scripts/sam_script_runner.sh stripe user_id=123 units=5 reason="api_call"
```

## Lambda Chaining

The Lambda chaining example demonstrates how to:

1. Receive data in a Lambda function
2. Store the data in S3
3. Record metadata in DynamoDB
4. Send an event to EventBridge

This pattern is useful for building event-driven architectures and processing pipelines.

### Creating the Chaining Example

```bash
python anima_builder_sam.py create-chaining
```

## Troubleshooting

### Common Issues

1. **AWS SAM CLI not installed**:
   ```
   brew install aws-sam-cli
   ```

2. **AWS credentials not configured**:
   ```
   aws configure
   ```

3. **Stripe API key issues**:
   - Check that your Stripe API key is correctly set in the environment or Secrets Manager
   - Verify that the key has the necessary permissions

4. **Deployment failures**:
   - Check CloudFormation events: `aws cloudformation describe-stack-events --stack-name soulcore-hub`
   - Check Lambda logs: `./scripts/sam_script_runner.sh logs function-name`

### Getting Help

For more help, run:

```bash
./scripts/sam_script_runner.sh help
```

Or:

```bash
python anima_builder_sam.py --help
```
