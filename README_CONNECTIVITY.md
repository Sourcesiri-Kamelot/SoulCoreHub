# SoulCoreHub Connectivity Guide

This document outlines the connectivity architecture for SoulCoreHub, including API Gateway, WebSocket support, and security features.

## Architecture Overview

SoulCoreHub uses a modern, secure connectivity architecture:

```
Client <---> API Gateway <---> Services
  |                |
  |                v
  +-----> WebSocket Server
```

## API Gateway

The API Gateway (`api/api_gateway.js`) serves as the entry point for all HTTP requests and provides:

- Route management
- Authentication and authorization
- Rate limiting
- Security headers
- CORS configuration

### Key Features

- **Authentication Middleware**: JWT-based authentication for protected routes
- **Rate Limiting**: Prevents abuse by limiting requests per IP
- **Security Headers**: Implements best practices for web security
- **CORS**: Configurable cross-origin resource sharing

## WebSocket Support

Real-time communication is handled by the WebSocket server (`api/websocket_handler.js`):

- Subscription-based messaging
- Authentication for secure connections
- Topic-based broadcasting
- Support for Market Whisperer real-time data

### WebSocket Topics

| Topic | Description | Authentication | Subscription Tier |
|-------|-------------|----------------|------------------|
| `system:status` | System status updates | No | All |
| `system:announcements` | System announcements | No | All |
| `market:summary` | Market summary data | Yes | All |
| `market:detail` | Detailed market data | Yes | Pro+ |
| `trading:signals` | Trading signals | Yes | Pro+ |
| `trading:advanced` | Advanced trading data | Yes | Enterprise/Trader Pro |
| `agent:status` | Agent status updates | Yes | Enterprise |

## Security

Security is implemented at multiple levels:

- **Authentication**: JWT-based with token refresh
- **Authorization**: Role-based access control
- **Input Validation**: Validation and sanitization of all inputs
- **Rate Limiting**: Protection against brute force and DoS attacks
- **Security Headers**: Protection against common web vulnerabilities

## AWS Integration

SoulCoreHub integrates with AWS services for enhanced security and scalability:

- **Secrets Manager**: Secure storage of sensitive credentials
- **API Gateway**: When deployed to AWS, uses AWS API Gateway
- **Lambda**: Serverless functions for specific operations
- **CloudFront**: CDN for static assets
- **S3**: Storage for user uploads and generated content

## Stripe Integration

Payment processing is handled securely through Stripe:

- **Subscription Management**: Tiered subscription model
- **Metered Billing**: Usage-based billing for API calls
- **Marketplace Transactions**: Support for marketplace payments
- **Customer Portal**: Self-service subscription management
- **Webhook Handling**: Real-time event processing

## Getting Started

### Prerequisites

- Node.js 14+
- AWS CLI configured (for AWS features)
- Stripe account (for payment features)

### Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. Start the server:
   ```bash
   npm start
   ```

### Testing Connectivity

1. Test HTTP API:
   ```bash
   curl http://localhost:3000/api/status
   ```

2. Test WebSocket:
   ```javascript
   const ws = new WebSocket('ws://localhost:3000');
   ws.onopen = () => {
     ws.send(JSON.stringify({ type: 'ping' }));
   };
   ws.onmessage = (event) => {
     console.log('Received:', JSON.parse(event.data));
   };
   ```

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   - Check that JWT_SECRET is properly set in .env
   - Verify token expiration and format

2. **WebSocket Connection Issues**:
   - Ensure the server is running
   - Check for firewall or proxy issues
   - Verify client is using the correct WebSocket URL

3. **Stripe Integration Problems**:
   - Verify Stripe API keys are correct
   - Check webhook configuration in Stripe dashboard
   - Look for detailed errors in server logs

### Logs

Important logs are available at:

- Server logs: Standard output
- WebSocket events: `logs/websocket.log`
- Payment events: `logs/payments.log`
- Authentication events: `logs/auth.log`

## Next Steps

1. **Database Integration**: Add persistent storage with MongoDB or PostgreSQL
2. **Caching Layer**: Implement Redis for improved performance
3. **Monitoring**: Add Prometheus/Grafana for real-time monitoring
4. **CI/CD**: Set up automated testing and deployment
5. **Containerization**: Dockerize the application for easier deployment
