# User Plan Lambda Function

This Lambda function retrieves a user's active Stripe plan from a DynamoDB table and returns it as a JSON response for frontend use.

## Features

- Retrieves user subscription plan from DynamoDB
- Falls back to "free" plan if user not found
- Supports plan override via query parameter for testing
- Includes CORS headers for frontend access
- Validates and sanitizes input

## Deployment

### Prerequisites

- AWS CLI installed and configured
- AWS SAM CLI installed
- Node.js and npm installed

### Deploy with SAM

1. Navigate to the function directory:
   ```
   cd /Users/helo.im.ai/SoulCoreHub/lambda/getUserPlan
   ```

2. Deploy the function:
   ```
   sam deploy --guided
   ```

3. Follow the prompts to complete the deployment.

## Testing

You can test the function using the AWS Lambda console or by invoking it with the AWS CLI:

```
aws lambda invoke --function-name GetUserPlanFunction --payload file://test-event.json output.json
```

### Test with Query Parameters

- Test with userId: `https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/user-plan?userId=test-user-123`
- Test with plan override: `https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/user-plan?plan=pro`

## API Response

Successful response:
```json
{
  "userPlan": "pro",
  "stripeCustomerId": "cus_xxxxxxxx"
}
```

Error response:
```json
{
  "error": "Failed to retrieve user plan",
  "message": "Error message details"
}
```

Created by Helo Im AI Inc. Est. 2024
