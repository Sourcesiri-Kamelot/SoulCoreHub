# SoulCoreHub AWS Deployment Guide

This guide provides step-by-step instructions for deploying SoulCoreHub to AWS using the Serverless Application Model (SAM).

## 🚀 Prerequisites

Before you begin, make sure you have the following:

1. **AWS Account**: Active AWS account with appropriate permissions
2. **AWS CLI**: Installed and configured with your credentials
3. **AWS SAM CLI**: Installed for serverless application deployment
4. **Python 3.9+**: Required for local development and testing

## 🛠️ Setup

### 1. Configure AWS CLI

```bash
aws configure
```

Enter your AWS Access Key ID, Secret Access Key, default region (e.g., us-east-1), and output format (json).

### 2. Install AWS SAM CLI

```bash
# For macOS
brew tap aws/tap
brew install aws-sam-cli

# For other platforms, see:
# https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html
```

## 🚀 Simplified Deployment

For a quick and easy deployment, use the simplified deployment script:

```bash
./scripts/simplified_deploy.sh
```

This script will:
1. Build the SAM application
2. Deploy it to AWS
3. Save the API endpoint to your .env file

## 🧪 Testing the Deployment

After deployment, you can test the API endpoints:

```bash
./scripts/test_api.sh
```

This script will test the Anima, Neural Router, and Memory Sync endpoints.

## 🔧 Manual Deployment

If you prefer to deploy manually or need more control:

### 1. Build the SAM application

```bash
sam build
```

### 2. Deploy the SAM application

```bash
sam deploy --config-env evolve
```

### 3. Get the API endpoint

```bash
aws cloudformation describe-stacks --stack-name soulcore-hub --query "Stacks[0].Outputs[?OutputKey=='SoulCoreApi'].OutputValue" --output text
```

## 🔄 Updating the Deployment

To update an existing deployment:

1. Make your changes to the code
2. Run the simplified deployment script:

```bash
./scripts/simplified_deploy.sh
```

## 🧹 Cleaning Up

To delete the deployment and all associated resources:

```bash
aws cloudformation delete-stack --stack-name soulcore-hub
```

## 🔍 Troubleshooting

### Stack Creation Failed

If you see an error like:

```
Stack:arn:aws:cloudformation:us-east-1:XXXXXXXXXXXX:stack/soulcore-hub/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX is in ROLLBACK_COMPLETE state and can not be updated.
```

Delete the stack and try again:

```bash
aws cloudformation delete-stack --stack-name soulcore-hub
# Wait for deletion to complete
aws cloudformation wait stack-delete-complete --stack-name soulcore-hub
# Then redeploy
./scripts/simplified_deploy.sh
```

### Permission Issues

If you encounter permission issues:

```bash
# Check your IAM permissions
aws iam get-user
# Ensure you have the necessary permissions for CloudFormation, Lambda, API Gateway, etc.
```

### Lambda Function Errors

To check the logs for a Lambda function:

```bash
# Get the function name
aws lambda list-functions --query "Functions[?contains(FunctionName, 'soulcore-hub')].FunctionName" --output text

# Get the logs
aws logs filter-log-events --log-group-name "/aws/lambda/FUNCTION_NAME"
```

## 📊 Monitoring

### CloudWatch Logs

```bash
# View logs for a specific Lambda function
aws logs filter-log-events --log-group-name "/aws/lambda/soulcore-hub-AnimaLambda-XXXXXXXXXXXX"
```

### CloudWatch Metrics

You can view metrics for your Lambda functions, API Gateway, and other resources in the AWS Console:

1. Open the [CloudWatch Console](https://console.aws.amazon.com/cloudwatch)
2. Navigate to Metrics
3. Select the appropriate namespace (AWS Lambda, API Gateway, etc.)

## 🔒 Security Considerations

1. **IAM Permissions**: Review and restrict IAM permissions as needed
2. **API Gateway**: Consider adding authentication to your API endpoints
3. **Secrets**: Use AWS Secrets Manager for sensitive information
4. **Encryption**: Enable encryption for S3 buckets and DynamoDB tables

## 📈 Scaling Considerations

The serverless architecture will automatically scale based on demand:

1. **Lambda Concurrency**: Default limit is 1000 concurrent executions
2. **API Gateway**: Default limit is 10,000 requests per second
3. **DynamoDB**: Uses on-demand capacity by default

If you need higher limits, contact AWS Support.

## 🤝 Need Help?

If you encounter any issues with the deployment:

1. Check the CloudFormation events:
   ```bash
   aws cloudformation describe-stack-events --stack-name soulcore-hub
   ```

2. Check the Lambda function logs:
   ```bash
   aws logs filter-log-events --log-group-name "/aws/lambda/soulcore-hub-AnimaLambda-XXXXXXXXXXXX"
   ```

3. Test the Lambda function locally:
   ```bash
   sam local invoke AnimaLambda -e functions/anima/event.json
   ```
