# SoulCoreHub Payment Integration Guide

This document outlines the payment integration architecture for SoulCoreHub, implemented with Stripe.

## Payment Architecture

SoulCoreHub uses Stripe for all payment processing:

```
Client <---> SoulCoreHub Server <---> Stripe API
  ^                 |                    ^
  |                 v                    |
  +-----> Stripe.js Elements             |
                    |                    |
                    +--------------------+
```

## Subscription Tiers

SoulCoreHub offers the following subscription tiers:

### Free Tier
- Access to Anima agent (emotional core) with daily limits
- 10 messages per day with basic capabilities
- 1 "deep action" per day (complex task execution)
- Public community access
- Basic templates and examples

### Pro Tier ($9.99/month)
- Full access to Anima and GPTSoul
- 100 messages per day across agents
- 10 deep actions per day
- Private workspace storage (100MB)
- Priority response time

### Enterprise Tier ($49.99/month)
- Full access to all agents (including Azür and EvoVe)
- Unlimited messages
- 50 deep actions per day
- 1GB workspace storage
- Custom agent training
- API access for integration

### Trader Tier ($19.99/month)
- Access to Market Whisperer AI
- Real-time trading signals
- Market analysis
- Risk assessment tools
- 10 trading signals per day

### Trader Pro Tier ($39.99/month)
- All Trader features
- Advanced technical analysis
- Portfolio optimization
- Custom trading strategies
- Historical backtesting
- 50 trading signals per day

## Payment Components

### Stripe Handler

The Stripe handler (`payments/stripe_handler.js`) provides:

- Customer management
- Subscription creation and management
- Usage tracking for metered billing
- One-time purchases
- Marketplace transactions
- Webhook handling

### Payment Routes

The payment routes (`payments/stripe_routes.js`) provide API endpoints for:

- Creating customers
- Managing subscriptions
- Recording usage
- Creating checkout sessions
- Managing customer portal sessions
- Handling webhooks

## Implementation Details

### Customer Creation

```javascript
// Create a customer in Stripe
const result = await stripeHandler.createCustomer({
  id: userId,
  email: userEmail,
  name: userName
});

// Store customer ID in user record
userSubscriptions[userId] = {
  customerId: result.customerId,
  subscriptions: []
};
```

### Subscription Creation

```javascript
// Create a subscription for a customer
const result = await stripeHandler.createSubscription(
  customerId,
  'pro' // Subscription tier
);

// Store subscription in user record
userSubscriptions[userId].subscriptions.push({
  id: result.subscriptionId,
  tier: 'pro',
  status: 'incomplete',
  createdAt: new Date().toISOString()
});
```

### Metered Billing

```javascript
// Record usage for a metered subscription
const result = await stripeHandler.recordUsage(
  subscriptionItemId,
  5, // Quantity
  'api_call' // Action
);
```

### Webhook Handling

```javascript
// Verify and process a webhook event from Stripe
const result = await stripeHandler.handleWebhook(
  req.body, // Raw request body
  req.headers['stripe-signature'] // Stripe signature header
);

// Process different event types
switch (result.event.type) {
  case 'customer.subscription.created':
    // Handle subscription created
    break;
  case 'invoice.payment_succeeded':
    // Handle successful payment
    break;
  // ...
}
```

## Customer Portal

SoulCoreHub provides a customer portal for self-service subscription management:

```javascript
// Create a customer portal session
const result = await stripeHandler.createPortalSession(
  customerId,
  'https://soulcorehub.com/account' // Return URL
);

// Redirect to the portal
res.redirect(result.url);
```

## Marketplace Transactions

For the Market Whisperer AI marketplace:

```javascript
// Process a marketplace transaction
const result = await stripeHandler.processMarketplaceTransaction(
  buyerCustomerId,
  sellerAccountId,
  5000, // Amount in cents
  500, // Platform fee in cents
  'Purchase of Market Analysis Report' // Description
);
```

## Security Considerations

- **API Keys**: Stripe API keys are stored in AWS Secrets Manager
- **Webhook Signatures**: All webhook events are verified with signatures
- **PCI Compliance**: Card details never touch our servers
- **Audit Logging**: All payment events are logged for auditing

## Testing

### Test Mode

All development and testing should use Stripe test mode:

```
STRIPE_API_KEY=sk_test_...
```

### Test Cards

Use these test cards for testing:

- **Success**: 4242 4242 4242 4242
- **Requires Authentication**: 4000 0025 0000 3155
- **Declined**: 4000 0000 0000 0002

### Testing Webhooks

Use the Stripe CLI to test webhooks locally:

```bash
stripe listen --forward-to localhost:3000/payments/webhook
```

## Deployment

When deploying to production:

1. Update Stripe API keys to production keys
2. Configure webhook endpoints in the Stripe dashboard
3. Set up proper error handling and monitoring
4. Test the entire payment flow in production mode

## Troubleshooting

### Common Issues

1. **Webhook Verification Failures**:
   - Check that the webhook secret is correct
   - Ensure the raw body is being passed to the verification function

2. **Subscription Creation Failures**:
   - Verify that the price ID exists in Stripe
   - Check that the customer ID is valid

3. **Payment Method Issues**:
   - Ensure the customer has a valid payment method
   - Check for card authentication requirements

### Logs

Payment-related logs are available in:

- Server logs: Standard output
- Payment events: `logs/payments.log`

## Next Steps

1. **Analytics**: Implement payment analytics and reporting
2. **Dunning Management**: Handle failed payments and retries
3. **Promotions**: Add support for coupons and promotions
4. **Invoicing**: Customize invoice templates and emails
5. **Tax Management**: Implement tax calculation and reporting
