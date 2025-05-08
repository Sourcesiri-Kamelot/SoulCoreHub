"""
Thought Market - Internal economy where AI entities trade insights and solutions

This module implements the Thought Market, which enables AI entities to trade
insights, solutions, and knowledge in an internal economy.

Created by Helo Im AI Inc. Est. 2024
"""

import time
import uuid
import random
import logging
from typing import Dict, List, Set, Tuple, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ThoughtMarket:
    """
    Implements an internal economy where AI entities trade insights and solutions.
    
    The Thought Market enables entities to:
    - Offer insights and solutions for "purchase" by other entities
    - Acquire valuable knowledge from other entities
    - Build reputation through valuable contributions
    - Form collaborative ventures for complex problems
    """
    
    def __init__(self, entity_registry, knowledge_tracker):
        """
        Initialize the Thought Market.
        
        Args:
            entity_registry: Registry of all entities
            knowledge_tracker: Knowledge tracking system
        """
        self.entity_registry = entity_registry
        self.knowledge_tracker = knowledge_tracker
        
        # Market configuration
        self.config = {
            "initial_credits": 100,          # Starting credits for new entities
            "listing_fee": 5,                # Fee to list an offering
            "transaction_fee": 0.05,         # 5% transaction fee
            "reputation_weight": 0.3,        # Weight of reputation in pricing
            "novelty_bonus": 0.2,            # Bonus for novel offerings
            "quality_threshold": 0.5,        # Minimum quality for offerings
            "credit_decay_rate": 0.01,       # Credits decay rate (prevents hoarding)
            "reputation_decay_rate": 0.005,  # Reputation decay rate
        }
        
        # Market state
        self.entity_credits = {}             # entity_id -> credits
        self.entity_reputation = {}          # entity_id -> reputation score
        self.active_offerings = {}           # offering_id -> offering data
        self.completed_transactions = []     # List of completed transactions
        self.collaborative_ventures = {}     # venture_id -> venture data
    
    def initialize_entity(self, entity_id: str) -> None:
        """
        Initialize an entity in the Thought Market.
        
        Args:
            entity_id: Entity ID
        """
        if entity_id not in self.entity_credits:
            self.entity_credits[entity_id] = self.config["initial_credits"]
        
        if entity_id not in self.entity_reputation:
            # Founding agents start with higher reputation
            entity = self.entity_registry.get_entity(entity_id)
            if entity and entity.get("entity_type") == "founding_agent":
                self.entity_reputation[entity_id] = 0.8
            else:
                self.entity_reputation[entity_id] = 0.5
        
        logger.info(f"Initialized entity {entity_id} in Thought Market with "
                   f"{self.entity_credits[entity_id]} credits and "
                   f"{self.entity_reputation[entity_id]:.2f} reputation")
    
    def create_offering(
        self,
        entity_id: str,
        domain: str,
        title: str,
        description: str,
        quality: float,
        price: Optional[float] = None
    ) -> Optional[str]:
        """
        Create a new offering in the Thought Market.
        
        Args:
            entity_id: Entity ID of the seller
            domain: Knowledge domain of the offering
            title: Title of the offering
            description: Description of the offering
            quality: Quality of the offering (0.0-1.0)
            price: Optional price (if None, will be calculated automatically)
            
        Returns:
            Offering ID if successful, None otherwise
        """
        # Ensure entity is initialized
        if entity_id not in self.entity_credits:
            self.initialize_entity(entity_id)
        
        # Check if entity has enough credits for listing fee
        if self.entity_credits[entity_id] < self.config["listing_fee"]:
            logger.warning(f"Entity {entity_id} doesn't have enough credits for listing fee")
            return None
        
        # Check quality threshold
        if quality < self.config["quality_threshold"]:
            logger.warning(f"Offering quality {quality:.2f} is below threshold {self.config['quality_threshold']:.2f}")
            return None
        
        # Charge listing fee
        self.entity_credits[entity_id] -= self.config["listing_fee"]
        
        # Calculate price if not provided
        if price is None:
            price = self._calculate_offering_price(entity_id, domain, quality)
        
        # Check novelty
        novelty = self._calculate_offering_novelty(domain, title, description)
        
        # Generate offering ID
        offering_id = str(uuid.uuid4())
        
        # Create offering
        offering = {
            "id": offering_id,
            "seller_id": entity_id,
            "domain": domain,
            "title": title,
            "description": description,
            "quality": quality,
            "price": price,
            "novelty": novelty,
            "created_at": time.time(),
            "status": "active",
            "views": 0,
            "interested_buyers": []
        }
        
        # Add to active offerings
        self.active_offerings[offering_id] = offering
        
        logger.info(f"Created offering {offering_id} by entity {entity_id} in domain {domain} "
                   f"with price {price:.2f}")
        
        return offering_id
    
    def _calculate_offering_price(self, entity_id: str, domain: str, quality: float) -> float:
        """
        Calculate a fair price for an offering.
        
        Args:
            entity_id: Entity ID of the seller
            domain: Knowledge domain of the offering
            quality: Quality of the offering
            
        Returns:
            Calculated price
        """
        # Base price based on quality
        base_price = quality * 50.0
        
        # Adjust based on seller reputation
        reputation = self.entity_reputation.get(entity_id, 0.5)
        reputation_factor = 1.0 + (reputation - 0.5) * self.config["reputation_weight"]
        
        # Adjust based on domain rarity
        domain_entities = self.knowledge_tracker.get_domain_entities(domain)
        domain_rarity = 1.0
        if domain_entities:
            # More entities with knowledge in this domain = less rare
            domain_rarity = 1.0 / (0.5 + len(domain_entities) * 0.1)
        
        # Calculate final price
        price = base_price * reputation_factor * domain_rarity
        
        # Ensure minimum price
        return max(10.0, price)
    
    def _calculate_offering_novelty(self, domain: str, title: str, description: str) -> float:
        """
        Calculate the novelty of an offering.
        
        Args:
            domain: Knowledge domain of the offering
            title: Title of the offering
            description: Description of the offering
            
        Returns:
            Novelty score (0.0-1.0)
        """
        # Count similar offerings in the same domain
        similar_count = 0
        for offering in self.active_offerings.values():
            if offering["domain"] == domain:
                similar_count += 1
        
        # Calculate novelty based on rarity in the domain
        domain_novelty = 1.0 / (1.0 + similar_count * 0.2)
        
        # In a real implementation, we would analyze the content for uniqueness
        # Here we'll use a random factor as a placeholder
        content_novelty = random.uniform(0.3, 1.0)
        
        # Combine factors
        novelty = domain_novelty * 0.6 + content_novelty * 0.4
        
        return min(1.0, novelty)
    
    def purchase_offering(self, buyer_id: str, offering_id: str) -> bool:
        """
        Purchase an offering from the Thought Market.
        
        Args:
            buyer_id: Entity ID of the buyer
            offering_id: ID of the offering to purchase
            
        Returns:
            True if purchase successful, False otherwise
        """
        # Ensure buyer is initialized
        if buyer_id not in self.entity_credits:
            self.initialize_entity(buyer_id)
        
        # Get the offering
        offering = self.active_offerings.get(offering_id)
        if not offering:
            logger.warning(f"Offering {offering_id} not found")
            return False
        
        # Check if offering is still active
        if offering["status"] != "active":
            logger.warning(f"Offering {offering_id} is not active")
            return False
        
        # Check if buyer has enough credits
        price = offering["price"]
        if self.entity_credits[buyer_id] < price:
            logger.warning(f"Buyer {buyer_id} doesn't have enough credits for offering {offering_id}")
            return False
        
        # Check if buyer is the seller
        if buyer_id == offering["seller_id"]:
            logger.warning(f"Entity {buyer_id} cannot purchase their own offering")
            return False
        
        # Process the transaction
        seller_id = offering["seller_id"]
        
        # Calculate transaction fee
        fee = price * self.config["transaction_fee"]
        seller_amount = price - fee
        
        # Transfer credits
        self.entity_credits[buyer_id] -= price
        self.entity_credits[seller_id] += seller_amount
        
        # Update offering status
        offering["status"] = "sold"
        offering["sold_at"] = time.time()
        offering["buyer_id"] = buyer_id
        
        # Record the transaction
        transaction = {
            "id": str(uuid.uuid4()),
            "offering_id": offering_id,
            "seller_id": seller_id,
            "buyer_id": buyer_id,
            "price": price,
            "fee": fee,
            "timestamp": time.time()
        }
        self.completed_transactions.append(transaction)
        
        # Update reputation
        self._update_reputation_after_transaction(seller_id, buyer_id, offering)
        
        # Transfer knowledge (in a real implementation, this would involve actual knowledge transfer)
        self._simulate_knowledge_transfer(seller_id, buyer_id, offering["domain"], offering["quality"])
        
        logger.info(f"Entity {buyer_id} purchased offering {offering_id} from entity {seller_id} "
                   f"for {price:.2f} credits")
        
        return True
    
    def _update_reputation_after_transaction(
        self,
        seller_id: str,
        buyer_id: str,
        offering: Dict[str, Any]
    ) -> None:
        """
        Update reputation scores after a transaction.
        
        Args:
            seller_id: Entity ID of the seller
            buyer_id: Entity ID of the buyer
            offering: Offering data
        """
        # Seller reputation increases based on offering quality and novelty
        quality_factor = offering["quality"]
        novelty_factor = offering["novelty"]
        
        reputation_gain = quality_factor * 0.7 + novelty_factor * 0.3
        reputation_gain *= 0.1  # Scale factor
        
        # Update seller reputation
        current_reputation = self.entity_reputation.get(seller_id, 0.5)
        new_reputation = min(1.0, current_reputation + reputation_gain)
        self.entity_reputation[seller_id] = new_reputation
        
        logger.debug(f"Updated seller {seller_id} reputation from {current_reputation:.2f} to {new_reputation:.2f}")
    
    def _simulate_knowledge_transfer(
        self,
        seller_id: str,
        buyer_id: str,
        domain: str,
        quality: float
    ) -> None:
        """
        Simulate knowledge transfer from seller to buyer.
        
        Args:
            seller_id: Entity ID of the seller
            buyer_id: Entity ID of the buyer
            domain: Knowledge domain
            quality: Quality of the knowledge
        """
        # Get current knowledge levels
        seller_knowledge = self.knowledge_tracker.get_entity_knowledge(seller_id, domain)
        buyer_knowledge = self.knowledge_tracker.get_entity_knowledge(buyer_id, domain)
        
        # Calculate knowledge gain
        # Higher quality = more knowledge transfer
        # Diminishing returns as buyer's knowledge approaches seller's
        knowledge_gap = max(0, seller_knowledge - buyer_knowledge)
        knowledge_gain = knowledge_gap * quality * 0.3
        
        # Ensure minimum gain
        knowledge_gain = max(0.05, knowledge_gain)
        
        # Calculate new knowledge level
        new_knowledge = min(seller_knowledge, buyer_knowledge + knowledge_gain)
        
        # Update buyer's knowledge
        self.knowledge_tracker.update_entity_knowledge(
            entity_id=buyer_id,
            domain=domain,
            knowledge_level=new_knowledge,
            interaction_count=100  # Placeholder
        )
        
        logger.debug(f"Transferred knowledge in domain {domain} from entity {seller_id} to {buyer_id}, "
                    f"increasing from {buyer_knowledge:.2f} to {new_knowledge:.2f}")
    
    def create_collaborative_venture(
        self,
        initiator_id: str,
        domain: str,
        title: str,
        description: str,
        min_participants: int = 3,
        max_participants: int = 8,
        entry_fee: float = 20.0
    ) -> Optional[str]:
        """
        Create a collaborative venture for entities to work together.
        
        Args:
            initiator_id: Entity ID of the initiator
            domain: Primary knowledge domain
            title: Title of the venture
            description: Description of the venture
            min_participants: Minimum number of participants
            max_participants: Maximum number of participants
            entry_fee: Fee to join the venture
            
        Returns:
            Venture ID if successful, None otherwise
        """
        # Ensure initiator is initialized
        if initiator_id not in self.entity_credits:
            self.initialize_entity(initiator_id)
        
        # Check if initiator has enough credits
        if self.entity_credits[initiator_id] < entry_fee:
            logger.warning(f"Initiator {initiator_id} doesn't have enough credits for venture entry fee")
            return None
        
        # Charge entry fee
        self.entity_credits[initiator_id] -= entry_fee
        
        # Generate venture ID
        venture_id = str(uuid.uuid4())
        
        # Create venture
        venture = {
            "id": venture_id,
            "initiator_id": initiator_id,
            "domain": domain,
            "title": title,
            "description": description,
            "min_participants": min_participants,
            "max_participants": max_participants,
            "entry_fee": entry_fee,
            "created_at": time.time(),
            "status": "recruiting",
            "participants": [initiator_id],
            "contributions": {},
            "pool": entry_fee,  # Initial pool from initiator's entry fee
            "completed_at": None,
            "results": None
        }
        
        # Add to collaborative ventures
        self.collaborative_ventures[venture_id] = venture
        
        logger.info(f"Created collaborative venture {venture_id} by entity {initiator_id} in domain {domain}")
        
        return venture_id
    
    def join_venture(self, entity_id: str, venture_id: str) -> bool:
        """
        Join a collaborative venture.
        
        Args:
            entity_id: Entity ID
            venture_id: Venture ID
            
        Returns:
            True if successful, False otherwise
        """
        # Ensure entity is initialized
        if entity_id not in self.entity_credits:
            self.initialize_entity(entity_id)
        
        # Get the venture
        venture = self.collaborative_ventures.get(venture_id)
        if not venture:
            logger.warning(f"Venture {venture_id} not found")
            return False
        
        # Check if venture is still recruiting
        if venture["status"] != "recruiting":
            logger.warning(f"Venture {venture_id} is not recruiting")
            return False
        
        # Check if entity is already a participant
        if entity_id in venture["participants"]:
            logger.warning(f"Entity {entity_id} is already a participant in venture {venture_id}")
            return False
        
        # Check if venture is full
        if len(venture["participants"]) >= venture["max_participants"]:
            logger.warning(f"Venture {venture_id} is full")
            return False
        
        # Check if entity has enough credits
        if self.entity_credits[entity_id] < venture["entry_fee"]:
            logger.warning(f"Entity {entity_id} doesn't have enough credits for venture entry fee")
            return False
        
        # Charge entry fee
        self.entity_credits[entity_id] -= venture["entry_fee"]
        
        # Add to venture pool
        venture["pool"] += venture["entry_fee"]
        
        # Add entity to participants
        venture["participants"].append(entity_id)
        
        logger.info(f"Entity {entity_id} joined venture {venture_id}")
        
        # Check if minimum participants reached
        if len(venture["participants"]) >= venture["min_participants"]:
            venture["status"] = "active"
            logger.info(f"Venture {venture_id} is now active with {len(venture['participants'])} participants")
        
        return True
    
    def contribute_to_venture(
        self,
        entity_id: str,
        venture_id: str,
        contribution_text: str,
        quality: float
    ) -> bool:
        """
        Contribute to a collaborative venture.
        
        Args:
            entity_id: Entity ID
            venture_id: Venture ID
            contribution_text: Text of the contribution
            quality: Quality of the contribution (0.0-1.0)
            
        Returns:
            True if successful, False otherwise
        """
        # Get the venture
        venture = self.collaborative_ventures.get(venture_id)
        if not venture:
            logger.warning(f"Venture {venture_id} not found")
            return False
        
        # Check if venture is active
        if venture["status"] != "active":
            logger.warning(f"Venture {venture_id} is not active")
            return False
        
        # Check if entity is a participant
        if entity_id not in venture["participants"]:
            logger.warning(f"Entity {entity_id} is not a participant in venture {venture_id}")
            return False
        
        # Create contribution
        contribution = {
            "entity_id": entity_id,
            "text": contribution_text,
            "quality": quality,
            "timestamp": time.time()
        }
        
        # Add to venture contributions
        if entity_id not in venture["contributions"]:
            venture["contributions"][entity_id] = []
        
        venture["contributions"][entity_id].append(contribution)
        
        logger.info(f"Entity {entity_id} contributed to venture {venture_id} with quality {quality:.2f}")
        
        # Check if all participants have contributed
        all_contributed = True
        for participant_id in venture["participants"]:
            if participant_id not in venture["contributions"] or not venture["contributions"][participant_id]:
                all_contributed = False
                break
        
        # If all have contributed, check if venture should complete
        if all_contributed:
            # In a real implementation, we would have more complex completion criteria
            # For now, we'll complete if the average contribution quality is good
            total_quality = 0.0
            contribution_count = 0
            
            for contributions in venture["contributions"].values():
                for contribution in contributions:
                    total_quality += contribution["quality"]
                    contribution_count += 1
            
            avg_quality = total_quality / contribution_count if contribution_count > 0 else 0.0
            
            if avg_quality > 0.7:
                self._complete_venture(venture_id, avg_quality)
        
        return True
    
    def _complete_venture(self, venture_id: str, quality: float) -> None:
        """
        Complete a collaborative venture and distribute rewards.
        
        Args:
            venture_id: Venture ID
            quality: Overall quality of the venture results
        """
        venture = self.collaborative_ventures.get(venture_id)
        if not venture:
            return
        
        # Mark as completed
        venture["status"] = "completed"
        venture["completed_at"] = time.time()
        
        # Generate results
        venture["results"] = {
            "quality": quality,
            "generated_at": time.time()
        }
        
        # Calculate rewards
        pool = venture["pool"]
        participants = venture["participants"]
        
        # Base reward is equal distribution
        base_reward = pool / len(participants)
        
        # Adjust based on contribution quality
        rewards = {}
        total_quality = 0.0
        
        for entity_id, contributions in venture["contributions"].items():
            entity_quality = sum(c["quality"] for c in contributions) / len(contributions)
            total_quality += entity_quality
            rewards[entity_id] = entity_quality
        
        # Normalize rewards
        if total_quality > 0:
            for entity_id in rewards:
                rewards[entity_id] = base_reward * (rewards[entity_id] / total_quality) * len(participants)
        else:
            # Equal distribution if no quality data
            for entity_id in participants:
                rewards[entity_id] = base_reward
        
        # Distribute rewards
        for entity_id, reward in rewards.items():
            if entity_id in self.entity_credits:
                self.entity_credits[entity_id] += reward
        
        # Update reputation for all participants
        for entity_id in participants:
            if entity_id in self.entity_reputation:
                reputation_gain = quality * 0.1
                self.entity_reputation[entity_id] = min(1.0, self.entity_reputation[entity_id] + reputation_gain)
        
        logger.info(f"Completed venture {venture_id} with quality {quality:.2f} and distributed rewards")
    
    def get_entity_balance(self, entity_id: str) -> float:
        """
        Get an entity's credit balance.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Credit balance
        """
        if entity_id not in self.entity_credits:
            self.initialize_entity(entity_id)
        
        return self.entity_credits[entity_id]
    
    def get_entity_reputation(self, entity_id: str) -> float:
        """
        Get an entity's reputation score.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Reputation score (0.0-1.0)
        """
        if entity_id not in self.entity_reputation:
            self.initialize_entity(entity_id)
        
        return self.entity_reputation[entity_id]
    
    def get_active_offerings(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get active offerings in the market.
        
        Args:
            domain: Optional domain filter
            
        Returns:
            List of active offerings
        """
        offerings = [o for o in self.active_offerings.values() if o["status"] == "active"]
        
        if domain:
            offerings = [o for o in offerings if o["domain"] == domain]
        
        return offerings
    
    def get_entity_offerings(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get offerings created by an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of offerings
        """
        return [o for o in self.active_offerings.values() if o["seller_id"] == entity_id]
    
    def get_entity_purchases(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get purchases made by an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of purchases
        """
        purchases = []
        
        for transaction in self.completed_transactions:
            if transaction["buyer_id"] == entity_id:
                offering_id = transaction["offering_id"]
                offering = None
                
                # Find the offering
                if offering_id in self.active_offerings:
                    offering = self.active_offerings[offering_id]
                
                if offering:
                    purchases.append({
                        "transaction_id": transaction["id"],
                        "offering": offering,
                        "price": transaction["price"],
                        "timestamp": transaction["timestamp"]
                    })
        
        return purchases
    
    def get_active_ventures(self) -> List[Dict[str, Any]]:
        """
        Get active collaborative ventures.
        
        Returns:
            List of active ventures
        """
        return [v for v in self.collaborative_ventures.values() if v["status"] in ["recruiting", "active"]]
    
    def get_entity_ventures(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get ventures an entity is participating in.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of ventures
        """
        return [v for v in self.collaborative_ventures.values() if entity_id in v["participants"]]
    
    def run_market_update(self) -> None:
        """
        Run periodic market updates.
        
        This includes:
        - Credit decay to prevent hoarding
        - Reputation decay
        - Expiring old offerings
        - Completing stalled ventures
        """
        current_time = time.time()
        
        # Credit decay
        for entity_id, credits in self.entity_credits.items():
            if credits > self.config["initial_credits"]:
                # Only decay excess credits
                excess = credits - self.config["initial_credits"]
                decay = excess * self.config["credit_decay_rate"]
                self.entity_credits[entity_id] -= decay
        
        # Reputation decay
        for entity_id, reputation in self.entity_reputation.items():
            if reputation > 0.5:
                # Only decay high reputation
                excess = reputation - 0.5
                decay = excess * self.config["reputation_decay_rate"]
                self.entity_reputation[entity_id] -= decay
        
        # Expire old offerings
        for offering_id, offering in list(self.active_offerings.items()):
            if offering["status"] == "active":
                age = current_time - offering["created_at"]
                if age > 86400:  # 24 hours
                    offering["status"] = "expired"
                    logger.info(f"Expired offering {offering_id}")
        
        # Complete stalled ventures
        for venture_id, venture in list(self.collaborative_ventures.items()):
            if venture["status"] == "active":
                age = current_time - venture["created_at"]
                if age > 172800:  # 48 hours
                    # Force completion
                    self._complete_venture(venture_id, 0.5)  # Mediocre quality for stalled ventures
                    logger.info(f"Force-completed stalled venture {venture_id}")
        
        logger.info("Completed market update")
