/**
 * SoulCoreHub Stripe Payment Integration
 * 
 * This module handles Stripe payment processing for:
 * - Subscription management
 * - Metered billing
 * - One-time purchases
 * - Marketplace transactions
 */

const { getSecrets } = require('../aws/secrets_manager');
let stripe;

// Subscription plan IDs - these would be created in the Stripe dashboard
const SUBSCRIPTION_PLANS = {
  free: null, // Free tier doesn't have a Stripe plan
  pro: 'price_pro_monthly',
  enterprise: 'price_enterprise_monthly',
  trader: 'price_trader_monthly',
  trader_pro: 'price_trader_pro_monthly'
};

// Initialize Stripe with API key from secrets
async function initStripe() {
  try {
    const secrets = await getSecrets('SoulCoreSecrets');
    const apiKey = secrets.STRIPE_API_KEY || process.env.STRIPE_API_KEY;
    
    if (!apiKey) {
      throw new Error('Stripe API key not found');
    }
    
    stripe = require('stripe')(apiKey);
    console.log('Stripe initialized successfully');
    return true;
  } catch (error) {
    console.error('Failed to initialize Stripe:', error);
    return false;
  }
}

/**
 * Create a new customer in Stripe
 * @param {Object} userData - User data including email and name
 * @returns {Object} - Stripe customer object
 */
async function createCustomer(userData) {
  if (!stripe) await initStripe();
  
  try {
    const customer = await stripe.customers.create({
      email: userData.email,
      name: userData.name,
      metadata: {
        userId: userData.id
      }
    });
    
    return {
      success: true,
      customerId: customer.id,
      customer
    };
  } catch (error) {
    console.error('Error creating Stripe customer:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Create a subscription for a customer
 * @param {string} customerId - Stripe customer ID
 * @param {string} planTier - Subscription tier (pro, enterprise, etc.)
 * @returns {Object} - Subscription details
 */
async function createSubscription(customerId, planTier) {
  if (!stripe) await initStripe();
  
  try {
    // Get price ID for the plan tier
    const priceId = SUBSCRIPTION_PLANS[planTier];
    
    if (!priceId) {
      throw new Error(`Invalid plan tier: ${planTier}`);
    }
    
    // Create the subscription
    const subscription = await stripe.subscriptions.create({
      customer: customerId,
      items: [{ price: priceId }],
      payment_behavior: 'default_incomplete',
      expand: ['latest_invoice.payment_intent'],
    });
    
    return {
      success: true,
      subscriptionId: subscription.id,
      clientSecret: subscription.latest_invoice.payment_intent.client_secret,
      subscription
    };
  } catch (error) {
    console.error('Error creating subscription:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Update a subscription to a new plan
 * @param {string} subscriptionId - Stripe subscription ID
 * @param {string} newPlanTier - New subscription tier
 * @returns {Object} - Updated subscription details
 */
async function updateSubscription(subscriptionId, newPlanTier) {
  if (!stripe) await initStripe();
  
  try {
    // Get price ID for the new plan tier
    const priceId = SUBSCRIPTION_PLANS[newPlanTier];
    
    if (!priceId) {
      throw new Error(`Invalid plan tier: ${newPlanTier}`);
    }
    
    // Get the subscription
    const subscription = await stripe.subscriptions.retrieve(subscriptionId);
    
    // Update the subscription item
    const updatedSubscription = await stripe.subscriptions.update(
      subscriptionId,
      {
        items: [
          {
            id: subscription.items.data[0].id,
            price: priceId,
          },
        ],
        proration_behavior: 'create_prorations',
      }
    );
    
    return {
      success: true,
      subscriptionId: updatedSubscription.id,
      subscription: updatedSubscription
    };
  } catch (error) {
    console.error('Error updating subscription:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Cancel a subscription
 * @param {string} subscriptionId - Stripe subscription ID
 * @returns {Object} - Cancellation result
 */
async function cancelSubscription(subscriptionId) {
  if (!stripe) await initStripe();
  
  try {
    const subscription = await stripe.subscriptions.update(
      subscriptionId,
      { cancel_at_period_end: true }
    );
    
    return {
      success: true,
      subscriptionId: subscription.id,
      cancelAt: new Date(subscription.cancel_at * 1000).toISOString(),
      subscription
    };
  } catch (error) {
    console.error('Error cancelling subscription:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Record usage for a metered subscription
 * @param {string} subscriptionItemId - Stripe subscription item ID
 * @param {number} quantity - Usage quantity to record
 * @param {string} action - Description of the action (e.g., 'api_call', 'prediction')
 * @returns {Object} - Usage record result
 */
async function recordUsage(subscriptionItemId, quantity, action) {
  if (!stripe) await initStripe();
  
  try {
    const usageRecord = await stripe.subscriptionItems.createUsageRecord(
      subscriptionItemId,
      {
        quantity: quantity,
        timestamp: 'now',
        action: action
      }
    );
    
    return {
      success: true,
      usageRecordId: usageRecord.id,
      usageRecord
    };
  } catch (error) {
    console.error('Error recording usage:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Create a checkout session for a one-time purchase
 * @param {string} customerId - Stripe customer ID
 * @param {string} priceId - Stripe price ID
 * @param {string} successUrl - URL to redirect on success
 * @param {string} cancelUrl - URL to redirect on cancel
 * @returns {Object} - Checkout session details
 */
async function createCheckoutSession(customerId, priceId, successUrl, cancelUrl) {
  if (!stripe) await initStripe();
  
  try {
    const session = await stripe.checkout.sessions.create({
      customer: customerId,
      payment_method_types: ['card'],
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      mode: 'payment',
      success_url: successUrl,
      cancel_url: cancelUrl,
    });
    
    return {
      success: true,
      sessionId: session.id,
      url: session.url
    };
  } catch (error) {
    console.error('Error creating checkout session:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Create a customer portal session
 * @param {string} customerId - Stripe customer ID
 * @param {string} returnUrl - URL to return to after the portal session
 * @returns {Object} - Portal session details
 */
async function createPortalSession(customerId, returnUrl) {
  if (!stripe) await initStripe();
  
  try {
    const session = await stripe.billingPortal.sessions.create({
      customer: customerId,
      return_url: returnUrl,
    });
    
    return {
      success: true,
      url: session.url
    };
  } catch (error) {
    console.error('Error creating portal session:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Process a marketplace transaction
 * @param {string} customerId - Stripe customer ID of the buyer
 * @param {string} sellerId - Stripe account ID of the seller
 * @param {number} amount - Amount in cents
 * @param {number} platformFee - Platform fee in cents
 * @param {string} description - Transaction description
 * @returns {Object} - Payment intent details
 */
async function processMarketplaceTransaction(customerId, sellerId, amount, platformFee, description) {
  if (!stripe) await initStripe();
  
  try {
    // Create a payment intent
    const paymentIntent = await stripe.paymentIntents.create({
      amount: amount,
      currency: 'usd',
      customer: customerId,
      description: description,
      application_fee_amount: platformFee,
      transfer_data: {
        destination: sellerId,
      },
    });
    
    return {
      success: true,
      paymentIntentId: paymentIntent.id,
      clientSecret: paymentIntent.client_secret
    };
  } catch (error) {
    console.error('Error processing marketplace transaction:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Verify and process a webhook event from Stripe
 * @param {string} payload - Raw request body
 * @param {string} signature - Stripe signature header
 * @returns {Object} - Processed event
 */
async function handleWebhook(payload, signature) {
  if (!stripe) await initStripe();
  
  try {
    // Get webhook secret from secrets
    const secrets = await getSecrets('SoulCoreSecrets');
    const webhookSecret = secrets.STRIPE_WEBHOOK_SECRET || process.env.STRIPE_WEBHOOK_SECRET;
    
    if (!webhookSecret) {
      throw new Error('Stripe webhook secret not found');
    }
    
    // Verify signature
    const event = stripe.webhooks.constructEvent(payload, signature, webhookSecret);
    
    // Process different event types
    switch (event.type) {
      case 'customer.subscription.created':
        // Handle subscription created
        console.log('Subscription created:', event.data.object.id);
        break;
        
      case 'customer.subscription.updated':
        // Handle subscription updated
        console.log('Subscription updated:', event.data.object.id);
        break;
        
      case 'customer.subscription.deleted':
        // Handle subscription deleted
        console.log('Subscription deleted:', event.data.object.id);
        break;
        
      case 'invoice.payment_succeeded':
        // Handle successful payment
        console.log('Payment succeeded for invoice:', event.data.object.id);
        break;
        
      case 'invoice.payment_failed':
        // Handle failed payment
        console.log('Payment failed for invoice:', event.data.object.id);
        break;
        
      // Add more event types as needed
        
      default:
        console.log(`Unhandled event type: ${event.type}`);
    }
    
    return {
      success: true,
      event
    };
  } catch (error) {
    console.error('Error handling webhook:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

module.exports = {
  initStripe,
  createCustomer,
  createSubscription,
  updateSubscription,
  cancelSubscription,
  recordUsage,
  createCheckoutSession,
  createPortalSession,
  processMarketplaceTransaction,
  handleWebhook,
  SUBSCRIPTION_PLANS
};
