/**
 * SoulCoreHub Stripe Payment Routes
 * 
 * This module provides API routes for Stripe payment processing:
 * - Subscription management
 * - Customer portal
 * - Webhook handling
 * - Usage tracking
 */

const express = require('express');
const router = express.Router();
const stripeHandler = require('./stripe_handler');
const { authMiddleware, authorizeRoles } = require('../auth/auth_middleware');

// In production, this would be a database connection
// For now, we'll use an in-memory store for demonstration
const userSubscriptions = {};

/**
 * @route POST /payments/create-customer
 * @desc Create a new Stripe customer
 * @access Private
 */
router.post('/create-customer', authMiddleware, async (req, res) => {
  try {
    const { id, email, name } = req.user;
    
    // Create customer in Stripe
    const result = await stripeHandler.createCustomer({ id, email, name });
    
    if (!result.success) {
      return res.status(400).json({
        success: false,
        error: result.error,
        message: 'Failed to create customer'
      });
    }
    
    // Store customer ID in user record
    // In a real app, this would update the database
    userSubscriptions[id] = {
      customerId: result.customerId,
      subscriptions: []
    };
    
    return res.json({
      success: true,
      message: 'Customer created successfully',
      customerId: result.customerId
    });
  } catch (error) {
    console.error('Create customer error:', error);
    return res.status(500).json({
      success: false,
      error: 'Server error',
      message: 'An error occurred while creating the customer'
    });
  }
});

/**
 * @route POST /payments/create-subscription
 * @desc Create a new subscription
 * @access Private
 */
router.post('/create-subscription', authMiddleware, async (req, res) => {
  try {
    const { planTier } = req.body;
    const userId = req.user.id;
    
    // Validate plan tier
    if (!planTier || !stripeHandler.SUBSCRIPTION_PLANS[planTier]) {
      return res.status(400).json({
        success: false,
        error: 'Invalid plan tier',
        message: 'Please provide a valid subscription plan tier'
      });
    }
    
    // Check if user has a customer ID
    if (!userSubscriptions[userId] || !userSubscriptions[userId].customerId) {
      return res.status(400).json({
        success: false,
        error: 'Customer not found',
        message: 'Please create a customer first'
      });
    }
    
    // Create subscription
    const result = await stripeHandler.createSubscription(
      userSubscriptions[userId].customerId,
      planTier
    );
    
    if (!result.success) {
      return res.status(400).json({
        success: false,
        error: result.error,
        message: 'Failed to create subscription'
      });
    }
    
    // Store subscription in user record
    if (!userSubscriptions[userId].subscriptions) {
      userSubscriptions[userId].subscriptions = [];
    }
    
    userSubscriptions[userId].subscriptions.push({
      id: result.subscriptionId,
      tier: planTier,
      status: 'incomplete',
      createdAt: new Date().toISOString()
    });
    
    return res.json({
      success: true,
      message: 'Subscription created successfully',
      subscriptionId: result.subscriptionId,
      clientSecret: result.clientSecret
    });
  } catch (error) {
    console.error('Create subscription error:', error);
    return res.status(500).json({
      success: false,
      error: 'Server error',
      message: 'An error occurred while creating the subscription'
    });
  }
});

/**
 * @route POST /payments/update-subscription
 * @desc Update a subscription to a new plan
 * @access Private
 */
router.post('/update-subscription', authMiddleware, async (req, res) => {
  try {
    const { subscriptionId, newPlanTier } = req.body;
    const userId = req.user.id;
    
    // Validate input
    if (!subscriptionId || !newPlanTier) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields',
        message: 'Subscription ID and new plan tier are required'
      });
    }
    
    // Validate plan tier
    if (!stripeHandler.SUBSCRIPTION_PLANS[newPlanTier]) {
      return res.status(400).json({
        success: false,
        error: 'Invalid plan tier',
        message: 'Please provide a valid subscription plan tier'
      });
    }
    
    // Check if user has this subscription
    if (!userSubscriptions[userId] || 
        !userSubscriptions[userId].subscriptions ||
        !userSubscriptions[userId].subscriptions.some(sub => sub.id === subscriptionId)) {
      return res.status(403).json({
        success: false,
        error: 'Subscription not found',
        message: 'You do not have permission to update this subscription'
      });
    }
    
    // Update subscription
    const result = await stripeHandler.updateSubscription(subscriptionId, newPlanTier);
    
    if (!result.success) {
      return res.status(400).json({
        success: false,
        error: result.error,
        message: 'Failed to update subscription'
      });
    }
    
    // Update subscription in user record
    const subIndex = userSubscriptions[userId].subscriptions.findIndex(
      sub => sub.id === subscriptionId
    );
    
    if (subIndex !== -1) {
      userSubscriptions[userId].subscriptions[subIndex].tier = newPlanTier;
      userSubscriptions[userId].subscriptions[subIndex].updatedAt = new Date().toISOString();
    }
    
    return res.json({
      success: true,
      message: 'Subscription updated successfully',
      subscriptionId: result.subscriptionId
    });
  } catch (error) {
    console.error('Update subscription error:', error);
    return res.status(500).json({
      success: false,
      error: 'Server error',
      message: 'An error occurred while updating the subscription'
    });
  }
});

/**
 * @route POST /payments/cancel-subscription
 * @desc Cancel a subscription
 * @access Private
 */
router.post('/cancel-subscription', authMiddleware, async (req, res) => {
  try {
    const { subscriptionId } = req.body;
    const userId = req.user.id;
    
    // Validate input
    if (!subscriptionId) {
      return res.status(400).json({
        success: false,
        error: 'Missing subscription ID',
        message: 'Subscription ID is required'
      });
    }
    
    // Check if user has this subscription
    if (!userSubscriptions[userId] || 
        !userSubscriptions[userId].subscriptions ||
        !userSubscriptions[userId].subscriptions.some(sub => sub.id === subscriptionId)) {
      return res.status(403).json({
        success: false,
        error: 'Subscription not found',
        message: 'You do not have permission to cancel this subscription'
      });
    }
    
    // Cancel subscription
    const result = await stripeHandler.cancelSubscription(subscriptionId);
    
    if (!result.success) {
      return res.status(400).json({
        success: false,
        error: result.error,
        message: 'Failed to cancel subscription'
      });
    }
    
    // Update subscription in user record
    const subIndex = userSubscriptions[userId].subscriptions.findIndex(
      sub => sub.id === subscriptionId
    );
    
    if (subIndex !== -1) {
      userSubscriptions[userId].subscriptions[subIndex].status = 'cancelling';
      userSubscriptions[userId].subscriptions[subIndex].cancelAt = result.cancelAt;
      userSubscriptions[userId].subscriptions[subIndex].updatedAt = new Date().toISOString();
    }
    
    return res.json({
      success: true,
      message: 'Subscription cancelled successfully',
      cancelAt: result.cancelAt
    });
  } catch (error) {
    console.error('Cancel subscription error:', error);
    return res.status(500).json({
      success: false,
      error: 'Server error',
      message: 'An error occurred while cancelling the subscription'
    });
  }
});

/**
 * @route POST /payments/record-usage
 * @desc Record usage for a metered subscription
 * @access Private
 */
router.post('/record-usage', authMiddleware, async (req, res) => {
  try {
    const { subscriptionItemId, quantity, action } = req.body;
    
    // Validate input
    if (!subscriptionItemId || !quantity || !action) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields',
        message: 'Subscription item ID, quantity, and action are required'
      });
    }
    
    // Record usage
    const result = await stripeHandler.recordUsage(subscriptionItemId, quantity, action);
    
    if (!result.success) {
      return res.status(400).json({
        success: false,
        error: result.error,
        message: 'Failed to record usage'
      });
    }
    
    return res.json({
      success: true,
      message: 'Usage recorded successfully',
      usageRecordId: result.usageRecordId
    });
  } catch (error) {
    console.error('Record usage error:', error);
    return res.status(500).json({
      success: false,
      error: 'Server error',
      message: 'An error occurred while recording usage'
    });
  }
});

/**
 * @route POST /payments/create-portal-session
 * @desc Create a Stripe customer portal session
 * @access Private
 */
router.post('/create-portal-session', authMiddleware, async (req, res) => {
  try {
    const { returnUrl } = req.body;
    const userId = req.user.id;
    
    // Validate input
    if (!returnUrl) {
      return res.status(400).json({
        success: false,
        error: 'Missing return URL',
        message: 'Return URL is required'
      });
    }
    
    // Check if user has a customer ID
    if (!userSubscriptions[userId] || !userSubscriptions[userId].customerId) {
      return res.status(400).json({
        success: false,
        error: 'Customer not found',
        message: 'No Stripe customer found for this user'
      });
    }
    
    // Create portal session
    const result = await stripeHandler.createPortalSession(
      userSubscriptions[userId].customerId,
      returnUrl
    );
    
    if (!result.success) {
      return res.status(400).json({
        success: false,
        error: result.error,
        message: 'Failed to create portal session'
      });
    }
    
    return res.json({
      success: true,
      url: result.url
    });
  } catch (error) {
    console.error('Create portal session error:', error);
    return res.status(500).json({
      success: false,
      error: 'Server error',
      message: 'An error occurred while creating the portal session'
    });
  }
});

/**
 * @route POST /payments/webhook
 * @desc Handle Stripe webhook events
 * @access Public
 */
router.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  try {
    const signature = req.headers['stripe-signature'];
    
    if (!signature) {
      return res.status(400).json({
        success: false,
        error: 'Missing Stripe signature',
        message: 'Stripe signature is required'
      });
    }
    
    // Process webhook
    const result = await stripeHandler.handleWebhook(req.body, signature);
    
    if (!result.success) {
      return res.status(400).json({
        success: false,
        error: result.error,
        message: 'Failed to process webhook'
      });
    }
    
    // Return success
    return res.json({ received: true });
  } catch (error) {
    console.error('Webhook error:', error);
    return res.status(500).json({
      success: false,
      error: 'Server error',
      message: 'An error occurred while processing the webhook'
    });
  }
});

/**
 * @route GET /payments/subscriptions
 * @desc Get user's subscriptions
 * @access Private
 */
router.get('/subscriptions', authMiddleware, async (req, res) => {
  try {
    const userId = req.user.id;
    
    // Check if user has subscriptions
    if (!userSubscriptions[userId] || !userSubscriptions[userId].subscriptions) {
      return res.json({
        success: true,
        subscriptions: []
      });
    }
    
    return res.json({
      success: true,
      subscriptions: userSubscriptions[userId].subscriptions
    });
  } catch (error) {
    console.error('Get subscriptions error:', error);
    return res.status(500).json({
      success: false,
      error: 'Server error',
      message: 'An error occurred while fetching subscriptions'
    });
  }
});

/**
 * @route GET /payments/customer
 * @desc Get user's Stripe customer info
 * @access Private
 */
router.get('/customer', authMiddleware, async (req, res) => {
  try {
    const userId = req.user.id;
    
    // Check if user has a customer ID
    if (!userSubscriptions[userId] || !userSubscriptions[userId].customerId) {
      return res.json({
        success: true,
        hasCustomer: false
      });
    }
    
    return res.json({
      success: true,
      hasCustomer: true,
      customerId: userSubscriptions[userId].customerId
    });
  } catch (error) {
    console.error('Get customer error:', error);
    return res.status(500).json({
      success: false,
      error: 'Server error',
      message: 'An error occurred while fetching customer info'
    });
  }
});

module.exports = router;
