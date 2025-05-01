#!/usr/bin/env python3
"""
Psynet Monetization Module for SoulCoreHub
-----------------------------------------
This module provides monetization capabilities for the Psynet predictive
visualization system within SoulCoreHub.
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class PsynetMonetization:
    """Monetization system for Psynet predictive visualization"""
    
    def __init__(self):
        self.name = "Psynet Monetization"
        self.status = "active"
        self.description = "Monetization system for Psynet predictive visualization"
        self.config = self._load_config()
        self.subscription_tiers = self.config.get("subscription_tiers", {})
        self.pay_per_prediction = self.config.get("pay_per_prediction", {})
        self.data_marketplace = self.config.get("data_marketplace", {})
        
        self.active_subscriptions = {}
        self.prediction_transactions = []
        self.marketplace_listings = []
        self.revenue_stats = {
            "total_revenue": 0.0,
            "subscription_revenue": 0.0,
            "prediction_revenue": 0.0,
            "marketplace_revenue": 0.0
        }
        
        # Load initial marketplace listings
        self._initialize_marketplace()
        
        print(f"[{datetime.now()}] Psynet Monetization initialized")
    
    def _load_config(self):
        """Load monetization configuration"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  "config", "psynet_config.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get("monetization_models", {})
            else:
                print(f"Config file not found: {config_path}")
                return {}
        except Exception as e:
            print(f"Error loading Psynet monetization config: {e}")
            return {}
    
    def _initialize_marketplace(self):
        """Initialize the data marketplace with sample listings"""
        # In a real implementation, these would be loaded from a database
        self.marketplace_listings = [
            {
                "id": "market_trends_2025",
                "title": "Market Trends 2025",
                "description": "Comprehensive prediction of market trends for 2025",
                "category": "market",
                "price": 499.99,
                "confidence": 0.85,
                "seller": "market_analysis_agent",
                "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
                "preview_available": True,
                "sales_count": 12
            },
            {
                "id": "consumer_behavior_q3",
                "title": "Consumer Behavior Q3 2025",
                "description": "Detailed prediction of consumer behavior patterns for Q3 2025",
                "category": "behavior",
                "price": 349.99,
                "confidence": 0.82,
                "seller": "behavior_analysis_agent",
                "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
                "preview_available": True,
                "sales_count": 8
            },
            {
                "id": "tech_innovation_map",
                "title": "Technology Innovation Map 2025-2026",
                "description": "Visual map of predicted technology innovations over the next two years",
                "category": "technology",
                "price": 599.99,
                "confidence": 0.78,
                "seller": "innovation_tracking_agent",
                "created_at": (datetime.now() - timedelta(days=7)).isoformat(),
                "preview_available": True,
                "sales_count": 15
            },
            {
                "id": "ai_society_evolution",
                "title": "AI Society Evolution Projection",
                "description": "Detailed prediction of AI Society structural evolution over 12 months",
                "category": "society",
                "price": 799.99,
                "confidence": 0.88,
                "seller": "society_analysis_agent",
                "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
                "preview_available": True,
                "sales_count": 6
            }
        ]
    
    def subscribe_user(self, user_id, tier_name, payment_method):
        """Subscribe a user to a specific tier"""
        print(f"[{datetime.now()}] Processing subscription for user {user_id} to {tier_name} tier")
        
        if tier_name not in self.subscription_tiers:
            return {
                "success": False,
                "error": "Invalid subscription tier",
                "available_tiers": list(self.subscription_tiers.keys())
            }
        
        tier = self.subscription_tiers[tier_name]
        
        # In a real implementation, this would process payment
        # For now, we'll simulate a successful payment
        
        subscription = {
            "user_id": user_id,
            "tier": tier_name,
            "price": tier["price_monthly"],
            "features": {
                "prediction_types": tier["prediction_types"],
                "visualization_quality": tier["visualization_quality"],
                "prediction_horizon": tier["prediction_horizon"]
            },
            "start_date": datetime.now().isoformat(),
            "next_billing_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "active"
        }
        
        # Store subscription
        self.active_subscriptions[user_id] = subscription
        
        # Update revenue stats
        self.revenue_stats["subscription_revenue"] += tier["price_monthly"]
        self.revenue_stats["total_revenue"] += tier["price_monthly"]
        
        return {
            "success": True,
            "subscription": subscription,
            "message": f"Successfully subscribed to {tier_name} tier"
        }
    
    def cancel_subscription(self, user_id):
        """Cancel a user's subscription"""
        print(f"[{datetime.now()}] Cancelling subscription for user {user_id}")
        
        if user_id not in self.active_subscriptions:
            return {
                "success": False,
                "error": "No active subscription found for this user"
            }
        
        # Update subscription status
        self.active_subscriptions[user_id]["status"] = "cancelled"
        self.active_subscriptions[user_id]["end_date"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": "Subscription successfully cancelled"
        }
    
    def process_prediction_purchase(self, user_id, prediction_type, parameters):
        """Process a pay-per-prediction purchase"""
        print(f"[{datetime.now()}] Processing prediction purchase for user {user_id}")
        
        if not self.pay_per_prediction.get("enabled", False):
            return {
                "success": False,
                "error": "Pay-per-prediction is not enabled"
            }
        
        # Calculate price based on parameters
        base_price = self.pay_per_prediction.get("base_price", 9.99)
        factors = self.pay_per_prediction.get("factors", {})
        
        # Apply time horizon factor
        time_horizon = parameters.get("time_horizon", 30)
        time_factor = 1.0 + (time_horizon / 30.0) * factors.get("time_horizon_multiplier", 0.1)
        
        # Apply visualization factor
        visualization = parameters.get("visualize", False)
        visual_factor = factors.get("visualization_multiplier", 2.0) if visualization else 1.0
        
        # Calculate final price
        price = base_price * time_factor * visual_factor
        
        # In a real implementation, this would process payment
        # For now, we'll simulate a successful payment
        
        transaction = {
            "user_id": user_id,
            "prediction_type": prediction_type,
            "parameters": parameters,
            "price": price,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # Store transaction
        self.prediction_transactions.append(transaction)
        
        # Update revenue stats
        self.revenue_stats["prediction_revenue"] += price
        self.revenue_stats["total_revenue"] += price
        
        return {
            "success": True,
            "transaction": transaction,
            "message": f"Successfully purchased {prediction_type} prediction"
        }
    
    def list_marketplace_item(self, seller_id, item_data):
        """List a new item on the data marketplace"""
        print(f"[{datetime.now()}] Listing new marketplace item from {seller_id}")
        
        if not self.data_marketplace.get("enabled", False):
            return {
                "success": False,
                "error": "Data marketplace is not enabled"
            }
        
        # Validate required fields
        required_fields = ["title", "description", "category", "price", "confidence"]
        for field in required_fields:
            if field not in item_data:
                return {
                    "success": False,
                    "error": f"Missing required field: {field}"
                }
        
        # Check confidence threshold
        min_confidence = self.data_marketplace.get("minimum_confidence_threshold", 0.8)
        if item_data["confidence"] < min_confidence:
            return {
                "success": False,
                "error": f"Confidence level below minimum threshold of {min_confidence}"
            }
        
        # Create marketplace listing
        item_id = f"item_{int(time.time())}_{seller_id}"
        listing = {
            "id": item_id,
            "title": item_data["title"],
            "description": item_data["description"],
            "category": item_data["category"],
            "price": item_data["price"],
            "confidence": item_data["confidence"],
            "seller": seller_id,
            "created_at": datetime.now().isoformat(),
            "preview_available": item_data.get("preview_available", False),
            "sales_count": 0
        }
        
        # Store listing
        self.marketplace_listings.append(listing)
        
        return {
            "success": True,
            "listing": listing,
            "message": "Item successfully listed on marketplace"
        }
    
    def purchase_marketplace_item(self, user_id, item_id):
        """Purchase an item from the data marketplace"""
        print(f"[{datetime.now()}] Processing marketplace purchase for user {user_id}, item {item_id}")
        
        # Find the item
        item = None
        for listing in self.marketplace_listings:
            if listing["id"] == item_id:
                item = listing
                break
        
        if not item:
            return {
                "success": False,
                "error": "Item not found in marketplace"
            }
        
        # In a real implementation, this would process payment
        # For now, we'll simulate a successful payment
        
        # Calculate marketplace commission
        commission_rate = self.data_marketplace.get("commission_rate", 0.15)
        commission = item["price"] * commission_rate
        seller_amount = item["price"] - commission
        
        transaction = {
            "user_id": user_id,
            "item_id": item_id,
            "item_title": item["title"],
            "price": item["price"],
            "seller": item["seller"],
            "commission": commission,
            "seller_amount": seller_amount,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # Update item sales count
        for listing in self.marketplace_listings:
            if listing["id"] == item_id:
                listing["sales_count"] += 1
                break
        
        # Update revenue stats
        self.revenue_stats["marketplace_revenue"] += commission
        self.revenue_stats["total_revenue"] += commission
        
        return {
            "success": True,
            "transaction": transaction,
            "message": f"Successfully purchased {item['title']}"
        }
    
    def get_subscription_tier_details(self, tier_name=None):
        """Get details for subscription tiers"""
        if tier_name:
            if tier_name in self.subscription_tiers:
                return {
                    "success": True,
                    "tier": tier_name,
                    "details": self.subscription_tiers[tier_name]
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid subscription tier",
                    "available_tiers": list(self.subscription_tiers.keys())
                }
        else:
            return {
                "success": True,
                "tiers": self.subscription_tiers
            }
    
    def get_user_subscription(self, user_id):
        """Get subscription details for a user"""
        if user_id in self.active_subscriptions:
            return {
                "success": True,
                "subscription": self.active_subscriptions[user_id]
            }
        else:
            return {
                "success": False,
                "error": "No active subscription found for this user"
            }
    
    def get_marketplace_listings(self, category=None, seller_id=None, limit=10):
        """Get listings from the data marketplace"""
        filtered_listings = self.marketplace_listings
        
        if category:
            filtered_listings = [item for item in filtered_listings if item["category"] == category]
        
        if seller_id:
            filtered_listings = [item for item in filtered_listings if item["seller"] == seller_id]
        
        # Sort by creation date (newest first)
        filtered_listings.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply limit
        filtered_listings = filtered_listings[:limit]
        
        return {
            "success": True,
            "listings": filtered_listings,
            "total": len(filtered_listings)
        }
    
    def get_revenue_report(self, period="all_time"):
        """Get revenue report for the specified period"""
        # In a real implementation, this would filter by date range
        # For now, we'll return the overall stats
        
        return {
            "success": True,
            "period": period,
            "revenue": self.revenue_stats,
            "breakdown": {
                "subscription": {
                    "basic": self.revenue_stats["subscription_revenue"] * 0.3,
                    "professional": self.revenue_stats["subscription_revenue"] * 0.5,
                    "enterprise": self.revenue_stats["subscription_revenue"] * 0.2
                },
                "prediction_types": {
                    "market": self.revenue_stats["prediction_revenue"] * 0.4,
                    "behavior": self.revenue_stats["prediction_revenue"] * 0.3,
                    "performance": self.revenue_stats["prediction_revenue"] * 0.2,
                    "society": self.revenue_stats["prediction_revenue"] * 0.1
                },
                "marketplace_categories": {
                    "market": self.revenue_stats["marketplace_revenue"] * 0.35,
                    "behavior": self.revenue_stats["marketplace_revenue"] * 0.25,
                    "technology": self.revenue_stats["marketplace_revenue"] * 0.3,
                    "society": self.revenue_stats["marketplace_revenue"] * 0.1
                }
            }
        }
    
    def get_user_transaction_history(self, user_id):
        """Get transaction history for a user"""
        # Filter transactions for this user
        user_transactions = [t for t in self.prediction_transactions if t["user_id"] == user_id]
        
        return {
            "success": True,
            "user_id": user_id,
            "transactions": user_transactions,
            "total_spent": sum(t["price"] for t in user_transactions)
        }

# For testing
if __name__ == "__main__":
    monetization = PsynetMonetization()
    print("Psynet Monetization initialized in standalone mode")
    
    # Test subscription
    test_subscription = monetization.subscribe_user("test_user_1", "professional", "credit_card")
    print(f"Test subscription created: {test_subscription['success']}")
    
    # Test prediction purchase
    test_purchase = monetization.process_prediction_purchase(
        "test_user_2", 
        "market", 
        {"time_horizon": 60, "visualize": True}
    )
    print(f"Test prediction purchase: {test_purchase['success']}")
    
    # Test marketplace listing
    test_listing = monetization.list_marketplace_item(
        "test_seller_1",
        {
            "title": "Test Market Prediction",
            "description": "A test market prediction for testing",
            "category": "market",
            "price": 199.99,
            "confidence": 0.85
        }
    )
    print(f"Test marketplace listing: {test_listing['success']}")
    
    # Test marketplace purchase
    if monetization.marketplace_listings:
        test_item_id = monetization.marketplace_listings[0]["id"]
        test_market_purchase = monetization.purchase_marketplace_item("test_user_3", test_item_id)
        print(f"Test marketplace purchase: {test_market_purchase['success']}")
    
    # Test revenue report
    test_report = monetization.get_revenue_report()
    print(f"Revenue report: Total revenue: ${test_report['revenue']['total_revenue']:.2f}")
