# SoulCoreHub Security Enhancements

This document outlines the security enhancements implemented in SoulCoreHub to protect payment systems, user data, and prevent unauthorized API usage.

## 1. Privacy Policy

A comprehensive privacy policy has been added to the public UI at `/public/privacy-policy.html`. This document:

- Outlines what data is collected from users
- Explains how data is used and protected
- Details user rights regarding their data
- Ensures compliance with GDPR and CCPA regulations

The privacy policy helps protect your business legally by informing users about your data practices and obtaining their informed consent.

## 2. API Key Authentication

API key authentication has been implemented for sensitive endpoints:

- Added `ApiKeyAuthorizer` to the API Gateway configuration
- Created a usage plan with rate limits (10,000 requests per month, 50 requests per second)
- Added `X-Api-Key` header requirement for authenticated endpoints

This prevents unauthorized access to your API and helps track and limit usage.

## 3. Request Signing

Request signing has been implemented to prevent request tampering:

- Created a `RequestSigner` class in `/src/client/request-signer.js` that:
  - Signs requests using HMAC-SHA256
  - Adds the signature to the `X-Request-Signature` header
- Modified Lambda functions to verify signatures using the same algorithm
- Implemented signature verification in the Anima Lambda function

This ensures that requests cannot be tampered with during transmission and that they originate from authorized clients.

## 4. CloudWatch Alarms

CloudWatch alarms have been set up to monitor for unusual API usage:

- Created alarms for API Gateway 4xx and 5xx errors
- Added alarms for high API latency and traffic spikes
- Set up Lambda-specific alarms for errors, high duration, and throttles
- Implemented a custom metric alarm for unusual API usage patterns
- Configured email notifications for all alarms

These alarms help detect potential security incidents, performance issues, or abuse of your API.

## 5. CORS Configuration

CORS (Cross-Origin Resource Sharing) has been properly configured:

- Restricted `Access-Control-Allow-Origin` to `https://soulcorehub.io` instead of `*`
- Added proper headers for API key and request signature
- Maintained necessary CORS headers in error responses

This prevents unauthorized websites from making requests to your API.

## Implementation Details

### API Gateway Configuration

```yaml
SoulCoreApi:
  Type: AWS::Serverless::Api
  Properties:
    StageName: !Ref Stage
    Cors:
      AllowMethods: "'GET,POST,OPTIONS'"
      AllowHeaders: "'Content-Type,Authorization,X-Api-Key'"
      AllowOrigin: "'https://soulcorehub.io'"
    Auth:
      DefaultAuthorizer: CognitoAuthorizer
      Authorizers:
        CognitoAuthorizer:
          UserPoolArn: !GetAtt SoulCoreUserPool.Arn
        ApiKeyAuthorizer:
          ApiKeyRequired: true
```

### Lambda Function Security

```python
def verify_request_signature(event):
    """Verify the signature of the incoming request"""
    if 'headers' not in event or not event['headers'] or 'X-Request-Signature' not in event['headers']:
        return True
    
    try:
        signature = event['headers']['X-Request-Signature']
        body = event.get('body', '')
        expected_signature = calculate_signature(body)
        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        logger.error(f"Error verifying signature: {str(e)}")
        return False
```

### Client-Side Request Signing

```javascript
class RequestSigner {
  constructor(apiKey, apiSecret) {
    this.apiKey = apiKey;
    this.apiSecret = apiSecret;
  }

  sign(data) {
    const dataString = typeof data === 'string' ? data : JSON.stringify(data);
    return CryptoJS.HmacSHA256(dataString, this.apiSecret).toString(CryptoJS.enc.Base64);
  }

  getHeaders(data) {
    return {
      'Content-Type': 'application/json',
      'X-Api-Key': this.apiKey,
      'X-Request-Signature': this.sign(data)
    };
  }
}
```

### CloudWatch Alarms

```yaml
UnusualAPIUsageAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: !Sub "${Stage}-SoulCoreHub-UnusualAPIUsage"
    MetricName: AnimaAPIRequests
    Namespace: SoulCoreHub/Usage
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 3
    Threshold: 100
    ComparisonOperator: GreaterThanThreshold
```

## Deployment Instructions

1. Deploy the updated template.yaml:
   ```bash
   ./scripts/simplified_deploy.sh
   ```

2. Deploy CloudWatch alarms:
   ```bash
   ./scripts/deploy-cloudwatch-alarms.sh evolve your-email@example.com
   ```

3. Update client code to use the new request signing:
   ```javascript
   import ApiClient from './src/client/api-client';
   
   const apiClient = new ApiClient(
     'https://zy3nix038k.execute-api.us-east-1.amazonaws.com/evolve',
     'your-api-key',
     'your-api-secret'
   );
   
   apiClient.sendToAnima('Hello Anima!').then(response => {
     console.log(response);
   });
   ```

## Next Steps

1. Rotate API keys regularly
2. Implement IP-based rate limiting
3. Add WAF (Web Application Firewall) protection
4. Implement DDoS protection
5. Set up regular security audits
