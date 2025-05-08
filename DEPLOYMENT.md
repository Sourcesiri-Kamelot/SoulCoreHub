# SoulCoreHub Deployment Guide

This guide covers the deployment of SoulCoreHub's backend services and frontend application.

## AWS Lambda Function Deployment

### Prerequisites
- AWS CLI installed and configured
- AWS SAM CLI installed
- Node.js and npm installed

### Deploy the User Plan Lambda Function

1. Navigate to the Lambda function directory:
   ```
   cd /Users/helo.im.ai/SoulCoreHub/lambda/getUserPlan
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Deploy using SAM:
   ```
   sam deploy --guided
   ```

4. Follow the prompts to complete the deployment:
   - Stack Name: `soulcorehub-user-plan`
   - AWS Region: Choose your preferred region
   - Confirm changes before deploy: `Y`
   - Allow SAM CLI IAM role creation: `Y`
   - Save arguments to configuration file: `Y`

5. Note the API endpoint URL from the outputs:
   ```
   UserPlanApiUrl: https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/user-plan
   ```

### Create DynamoDB Table

1. Create the UserSubscriptions table:
   ```
   aws dynamodb create-table \
     --table-name UserSubscriptions \
     --attribute-definitions AttributeName=userId,AttributeType=S \
     --key-schema AttributeName=userId,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST
   ```

2. Add sample data for testing:
   ```
   aws dynamodb put-item \
     --table-name UserSubscriptions \
     --item '{
       "userId": {"S": "test-user-123"},
       "planId": {"S": "pro"},
       "stripeCustomerId": {"S": "cus_test123"},
       "updatedAt": {"S": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}
     }'
   ```

## Frontend Configuration

1. Update the API URL in the useUserPlan hook:
   ```
   cd /Users/helo.im.ai/SoulCoreHub/src/hooks
   ```

2. Edit `useUserPlan.js` and update the API_URL constant with your Lambda function URL:
   ```javascript
   const API_URL = 'https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/user-plan';
   ```

## Testing the Integration

1. Start the frontend application:
   ```
   cd /Users/helo.im.ai/SoulCoreHub
   npm start
   ```

2. Test with different plans using URL parameters:
   ```
   http://localhost:3000?plan=free
   http://localhost:3000?plan=pro
   http://localhost:3000?plan=business
   http://localhost:3000?plan=enterprise
   ```

3. Test with the Lambda function:
   ```
   http://localhost:3000?userId=test-user-123
   ```

## Troubleshooting

### CORS Issues
If you encounter CORS issues, verify that the Lambda function has the correct CORS headers:
```javascript
const headers = {
  'Access-Control-Allow-Origin': '*', // Update with your domain in production
  'Access-Control-Allow-Headers': 'Content-Type,Authorization',
  'Access-Control-Allow-Methods': 'GET,OPTIONS'
};
```

### Authentication Issues
If the Lambda function cannot retrieve the user ID from the token:
1. Check that the token is being sent correctly in the Authorization header
2. Verify that the token decoding logic is correct
3. Test with the userId query parameter as a fallback

### DynamoDB Issues
If the Lambda function cannot retrieve data from DynamoDB:
1. Verify that the table exists and has the correct schema
2. Check that the Lambda function has the necessary IAM permissions
3. Test the DynamoDB access using the AWS CLI

Created by Helo Im AI Inc. Est. 2024
