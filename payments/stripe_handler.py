#!/usr/bin/env python3
"""
SoulCoreHub Stripe Payment Integration

This module handles Stripe payment processing for:
- Subscription management
- Metered billing
- One-time purchases
- Marketplace transactions
"""

import os
import json
import time
from datetime import datetime
import stripe
from ..aws.secrets_manager import get_secrets, get_secret_value

# Subscription plan IDs - these would be created in the Stripe dashboard
SUBSCRIPTION_PLANS = {
    "free": None,  # Free tier doesn't have a Stripe plan
    "pro": "price_pro_monthly",
    "enterprise": "price_enterprise_monthly",
    "trader": "price_trader_monthly",
    "trader_pro": "price_trader_pro_monthly"
}

# Initialize Stripe with API key from secrets
def init_stripe():
    """Initialize Stripe with API key from secrets"""
    try:
        secrets = get_secrets('SoulCoreSecrets')
        api_key = secrets.get('STRIPE_API_KEY') or os.environ.get('STRIPE_API_KEY')
        
        if not api_key:
            raise ValueError('Stripe API key not found')
        
        stripe.api_key = api_key
        print(f"[{datetime.now()}] Stripe initialized successfully")
        return True
    except Exception as e:
        print(f"[{datetime.now()}] Failed to initialize Stripe: {e}")
        return False

class StripeHandler:
    """Handler for Stripe payment processing"""
    
    def __init__(self):
        """Initialize the Stripe handler"""
        self.initialized = init_stripe()
    
    def create_customer(self, user_data):
        """
        Create a new customer in Stripe
        
        Args:
            user_data (dict): User data including email and name
            
        Returns:
            dict: Result with customer ID if successful
        """
        if not self.initialized:
            self.initialized = init_stripe()
        
        try:
            customer = stripe.Customer.create(
                email=user_data.get('email'),
                name=user_data.get('name'),
                metadata={
                    'userId': user_data.get('id')
                }
            )
            
            return {
                'success': True,
                'customer_id': customer.id,
                'customer': customer
            }
        except Exception as e:
            print(f"[{datetime.now()}] Error creating Stripe customer: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_subscription(self, customer_id, plan_tier):
        """
        Create a subscription for a customer
        
        Args:
            customer_id (str): Stripe customer ID
            plan_tier (str): Subscription tier (pro, enterprise, etc.)
            
        Returns:
            dict: Subscription details
        """
        if not self.initialized:
            self.initialized = init_stripe()
        
        try:
            # Get price ID for the plan tier
            price_id = SUBSCRIPTION_PLANS.get(plan_tier)
            
            if not price_id:
                raise ValueError(f"Invalid plan tier: {plan_tier}")
            
            # Create the subscription
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent'],
            )
            
            return {
                'success': True,
                'subscription_id': subscription.id,
                'client_secret': subscription.latest_invoice.payment_intent.client_secret,
                'subscription': subscription
            }
        except Exception as e:
            print(f"[{datetime.now()}] Error creating subscription: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_subscription(self, subscription_id, new_plan_tier):
        """
        Update a subscription to a new plan
        
        Args:
            subscription_id (str): Stripe subscription ID
            new_plan_tier (str): New subscription tier
            
        Returns:
            dict: Updated subscription details
        """
        if not self.initialized:
            self.initialized = init_stripe()
        
        try:
            # Get price ID for the new plan tier
            price_id = SUBSCRIPTION_PLANS.get(new_plan_tier)
            
            if not price_id:
                raise ValueError(f"Invalid plan tier: {new_plan_tier}")
            
            # Get the subscription
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Update the subscription item
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[
                    {
                        'id': subscription['items']['data'][0]['id'],
                        'price': price_id,
                    },
                ],
                proration_behavior='create_prorations',
            )
            
            return {
                'success': True,
                'subscription_id': updated_subscription.id,
                'subscription': updated_subscription
            }
        except Exception as e:
            print(f"[{datetime.now()}] Error updating subscription: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_subscription(self, subscription_id):
        """
        Cancel a subscription
        
        Args:
            subscription_id (str): Stripe subscription ID
            
        Returns:
            dict: Cancellation result
        """
        if not self.initialized:
            self.initialized = init_stripe()
        
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            
            return {
                'success': True,
                'subscription_id': subscription.id,
                'cancel_at': datetime.fromtimestamp(subscription.cancel_at).isoformat(),
                'subscription': subscription
            }
        except Exception as e:
            print(f"[{datetime.now()}] Error cancelling subscription: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def record_usage(self, subscription_item_id, quantity, action):
        """
        Record usage for a metered subscription
        
        Args:
            subscription_item_id (str): Stripe subscription item ID
            quantity (int): Usage quantity to record
            action (str): Description of the action (e.g., 'api_call', 'prediction')
            
        Returns:
            dict: Usage record result
        """
        if not self.initialized:
            self.initialized = init_stripe()
        
        try:
            usage_record = stripe.SubscriptionItem.create_usage_record(
                subscription_item_id,
                quantity=quantity,
                timestamp=int(time.time()),
                action=action
            )
            
            return {
                'success': True,
                'usage_record_id': usage_record.id,
                'usage_record': usage_record
            }
        except Exception as e:
            print(f"[{datetime.now()}] Error recording usage: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_checkout_session(self, customer_id, price_id, success_url, cancel_url):
        """
        Create a checkout session for a one-time purchase
        
        Args:
            customer_id (str): Stripe customer ID
            price_id (str): Stripe price ID
            success_url (str): URL to redirect on success
            cancel_url (str): URL to redirect on cancel
            
        Returns:
            dict: Checkout session details
        """
        if not self.initialized:
            self.initialized = init_stripe()
        
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': price_id,
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
            )
            
            return {
                'success': True,
                'session_id': session.id,
                'url': session.url
            }
        except Exception as e:
            print(f"[{datetime.now()}] Error creating checkout session: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_portal_session(self, customer_id, return_url):
        """
        Create a customer portal session
        
        Args:
            customer_id (str): Stripe customer ID
            return_url (str): URL to return to after the portal session
            
        Returns:
            dict: Portal session details
        """
        if not self.initialized:
            self.initialized = init_stripe()
        
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            
            return {
                'success': True,
                'url': session.url
            }
        except Exception as e:
            print(f"[{datetime.now()}] Error creating portal session: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_marketplace_transaction(self, customer_id, seller_id, amount, platform_fee, description):
        """
        Process a marketplace transaction
        
        Args:
            customer_id (str): Stripe customer ID of the buyer
            seller_id (str): Stripe account ID of the seller
            amount (int): Amount in cents
            platform_fee (int): Platform fee in cents
            description (str): Transaction description
            
        Returns:
            dict: Payment intent details
        """
        if not self.initialized:
            self.initialized = init_stripe()
        
        try:
            # Create a payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                customer=customer_id,
                description=description,
                application_fee_amount=platform_fee,
                transfer_data={
                    'destination': seller_id,
                },
            )
            
            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'client_secret': payment_intent.client_secret
            }
        except Exception as e:
            print(f"[{datetime.now()}] Error processing marketplace transaction: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_webhook(self, payload, signature):
        """
        Verify and process a webhook event from Stripe
        
        Args:
            payload (str): Raw request body
            signature (str): Stripe signature header
            
        Returns:
            dict: Processed event
        """
        if not self.initialized:
            self.initialized = init_stripe()
        
        try:
            # Get webhook secret from secrets
            secrets = get_secrets('SoulCoreSecrets')
            webhook_secret = secrets.get('STRIPE_WEBHOOK_SECRET') or os.environ.get('STRIPE_WEBHOOK_SECRET')
            
            if not webhook_secret:
                raise ValueError('Stripe webhook secret not found')
            
            # Verify signature
            event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
            
            # Process different event types
            event_type = event['type']
            
            if event_type == 'customer.subscription.created':
                # Handle subscription created
                print(f"[{datetime.now()}] Subscription created: {event['data']['object']['id']}")
                
            elif event_type == 'customer.subscription.updated':
                # Handle subscription updated
                print(f"[{datetime.now()}] Subscription updated: {event['data']['object']['id']}")
                
            elif event_type == 'customer.subscription.deleted':
                # Handle subscription deleted
                print(f"[{datetime.now()}] Subscription deleted: {event['data']['object']['id']}")
                
            elif event_type == 'invoice.payment_succeeded':
                # Handle successful payment
                print(f"[{datetime.now()}] Payment succeeded for invoice: {event['data']['object']['id']}")
                
            elif event_type == 'invoice.payment_failed':
                # Handle failed payment
                print(f"[{datetime.now()}] Payment failed for invoice: {event['data']['object']['id']}")
                
            else:
                # Handle other event types
                print(f"[{datetime.now()}] Unhandled event type: {event_type}")
            
            return {
                'success': True,
                'event': event
            }
        except Exception as e:
            print(f"[{datetime.now()}] Error handling webhook: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Create a singleton instance
stripe_handler = StripeHandler()

# For testing
if __name__ == "__main__":
    handler = StripeHandler()
    print("Stripe handler initialized in standalone mode")
    
    # Test creating a customer
    test_user = {
        'id': 'test_user_123',
        'email': 'test@example.com',
        'name': 'Test User'
    }
    
    result = handler.create_customer(test_user)
    print(f"Create customer result: {result['success']}")
    
    if result['success']:
        customer_id = result['customer_id']
        
        # Test creating a subscription
        sub_result = handler.create_subscription(customer_id, 'pro')
        print(f"Create subscription result: {sub_result['success']}")
        
        if sub_result['success']:
            subscription_id = sub_result['subscription_id']
            
            # Test updating a subscription
            update_result = handler.update_subscription(subscription_id, 'enterprise')
            print(f"Update subscription result: {update_result['success']}")
            
            # Test cancelling a subscription
            cancel_result = handler.cancel_subscription(subscription_id)
            print(f"Cancel subscription result: {cancel_result['success']}")
