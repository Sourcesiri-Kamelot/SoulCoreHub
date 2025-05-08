"""
Knowledge Tracker - Monitors knowledge accumulation in AI entities

This module implements the KnowledgeTracker class, which is responsible for
monitoring knowledge accumulation in AI entities and detecting when knowledge
thresholds are reached.

Created by Helo Im AI Inc. Est. 2024
"""

from typing import Dict, List, Set, Tuple, Optional, Any
import time
import json
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KnowledgeTracker:
    """
    Tracks knowledge accumulation in AI entities and detects birth thresholds.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the knowledge tracker.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        # Default configuration
        self.config = {
            "general_threshold": 0.75,  # 75% knowledge saturation triggers birth
            "specialized_threshold": 0.60,  # 60% for specialized domains
            "minimum_interactions": 50,  # Minimum interactions before birth is possible
            "knowledge_decay_rate": 0.01,  # Knowledge decay rate per day (unused knowledge)
            "domain_weights": {
                "technical": 1.0,
                "creative": 1.0,
                "analytical": 1.0,
                "emotional": 1.0,
                "strategic": 1.0
            }
        }
        
        # Load configuration if provided
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                    logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.error(f"Failed to load configuration from {config_path}: {e}")
        
        # Knowledge domain registry
        self.domains: Dict[str, Dict[str, Any]] = {}
        
        # Birth threshold events
        self.threshold_events: List[Dict[str, Any]] = []
    
    def register_domain(self, domain_name: str, category: str, description: str) -> None:
        """
        Register a knowledge domain for tracking.
        
        Args:
            domain_name: Name of the knowledge domain
            category: Category of the domain (technical, creative, etc.)
            description: Description of the domain
        """
        if domain_name in self.domains:
            logger.warning(f"Domain {domain_name} already registered, updating")
        
        self.domains[domain_name] = {
            "name": domain_name,
            "category": category,
            "description": description,
            "registered_at": time.time(),
            "entities": {}  # Will store entity_id -> knowledge level
        }
        
        logger.info(f"Registered domain: {domain_name} ({category})")
    
    def update_entity_knowledge(
        self,
        entity_id: str,
        domain: str,
        knowledge_level: float,
        interaction_count: int
    ) -> None:
        """
        Update an entity's knowledge level in a specific domain.
        
        Args:
            entity_id: ID of the entity
            domain: Knowledge domain
            knowledge_level: New knowledge level (0.0-1.0)
            interaction_count: Current interaction count for the entity
        """
        # Ensure domain exists
        if domain not in self.domains:
            logger.warning(f"Domain {domain} not registered, registering with default values")
            self.register_domain(domain, "unknown", f"Auto-registered domain: {domain}")
        
        # Update knowledge level
        self.domains[domain]["entities"][entity_id] = {
            "level": max(0.0, min(1.0, knowledge_level)),  # Clamp to 0.0-1.0
            "updated_at": time.time(),
            "interaction_count": interaction_count
        }
        
        # Check if birth threshold is reached
        self._check_birth_threshold(entity_id, domain, knowledge_level, interaction_count)
    
    def get_entity_knowledge(self, entity_id: str, domain: str) -> float:
        """
        Get an entity's knowledge level in a specific domain.
        
        Args:
            entity_id: ID of the entity
            domain: Knowledge domain
            
        Returns:
            Knowledge level (0.0-1.0), or 0.0 if not found
        """
        if domain not in self.domains:
            return 0.0
        
        entity_data = self.domains[domain]["entities"].get(entity_id)
        if not entity_data:
            return 0.0
        
        return entity_data["level"]
    
    def get_entity_domains(self, entity_id: str) -> Dict[str, float]:
        """
        Get all knowledge domains and levels for an entity.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Dictionary of domain -> knowledge level
        """
        result = {}
        for domain_name, domain_data in self.domains.items():
            entity_data = domain_data["entities"].get(entity_id)
            if entity_data:
                result[domain_name] = entity_data["level"]
        
        return result
    
    def get_domain_entities(self, domain: str) -> Dict[str, float]:
        """
        Get all entities and their knowledge levels for a domain.
        
        Args:
            domain: Knowledge domain
            
        Returns:
            Dictionary of entity_id -> knowledge level
        """
        if domain not in self.domains:
            return {}
        
        return {
            entity_id: data["level"]
            for entity_id, data in self.domains[domain]["entities"].items()
        }
    
    def get_entity_primary_domain(self, entity_id: str) -> Tuple[str, float]:
        """
        Get the primary knowledge domain for an entity.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Tuple of (domain_name, knowledge_level), or ("", 0.0) if none found
        """
        domains = self.get_entity_domains(entity_id)
        if not domains:
            return ("", 0.0)
        
        primary_domain = max(domains.items(), key=lambda x: x[1])
        return primary_domain
    
    def _check_birth_threshold(
        self,
        entity_id: str,
        domain: str,
        knowledge_level: float,
        interaction_count: int
    ) -> bool:
        """
        Check if a birth threshold has been reached.
        
        Args:
            entity_id: ID of the entity
            domain: Knowledge domain
            knowledge_level: Current knowledge level
            interaction_count: Current interaction count
            
        Returns:
            True if threshold reached, False otherwise
        """
        # Check minimum interactions
        if interaction_count < self.config["minimum_interactions"]:
            return False
        
        # Get threshold for this domain
        threshold = self.config["specialized_threshold"]
        if domain == "general":
            threshold = self.config["general_threshold"]
        
        # Check if threshold is reached
        if knowledge_level >= threshold:
            # Record threshold event
            event = {
                "entity_id": entity_id,
                "domain": domain,
                "knowledge_level": knowledge_level,
                "threshold": threshold,
                "interaction_count": interaction_count,
                "timestamp": time.time()
            }
            self.threshold_events.append(event)
            
            logger.info(f"Birth threshold reached: Entity {entity_id} in domain {domain} "
                       f"with knowledge level {knowledge_level:.2f}")
            
            return True
        
        return False
    
    def get_pending_birth_events(self) -> List[Dict[str, Any]]:
        """
        Get all pending birth threshold events.
        
        Returns:
            List of birth threshold events
        """
        return self.threshold_events.copy()
    
    def clear_birth_event(self, entity_id: str, domain: str) -> None:
        """
        Clear a birth threshold event after it has been processed.
        
        Args:
            entity_id: ID of the entity
            domain: Knowledge domain
        """
        self.threshold_events = [
            event for event in self.threshold_events
            if not (event["entity_id"] == entity_id and event["domain"] == domain)
        ]
    
    def analyze_knowledge_distribution(self, entity_id: str) -> Dict[str, Any]:
        """
        Analyze the knowledge distribution for an entity.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Analysis results
        """
        domains = self.get_entity_domains(entity_id)
        if not domains:
            return {
                "entity_id": entity_id,
                "total_domains": 0,
                "total_knowledge": 0.0,
                "average_level": 0.0,
                "primary_domain": "",
                "primary_level": 0.0,
                "distribution": {}
            }
        
        total_knowledge = sum(domains.values())
        average_level = total_knowledge / len(domains) if domains else 0.0
        primary_domain, primary_level = self.get_entity_primary_domain(entity_id)
        
        # Calculate distribution by category
        category_distribution = {}
        for domain, level in domains.items():
            if domain in self.domains:
                category = self.domains[domain]["category"]
                if category not in category_distribution:
                    category_distribution[category] = 0.0
                category_distribution[category] += level
        
        return {
            "entity_id": entity_id,
            "total_domains": len(domains),
            "total_knowledge": total_knowledge,
            "average_level": average_level,
            "primary_domain": primary_domain,
            "primary_level": primary_level,
            "distribution": domains,
            "category_distribution": category_distribution
        }
    
    def save_state(self, file_path: str) -> None:
        """
        Save the current state to a file.
        
        Args:
            file_path: Path to save the state
        """
        state = {
            "config": self.config,
            "domains": self.domains,
            "threshold_events": self.threshold_events
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"Saved state to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save state to {file_path}: {e}")
    
    def load_state(self, file_path: str) -> bool:
        """
        Load state from a file.
        
        Args:
            file_path: Path to load the state from
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"State file not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'r') as f:
                state = json.load(f)
            
            self.config = state["config"]
            self.domains = state["domains"]
            self.threshold_events = state["threshold_events"]
            
            logger.info(f"Loaded state from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load state from {file_path}: {e}")
            return False
