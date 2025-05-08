"""
Birth Engine - Creates new AI entities when knowledge thresholds are reached

This module implements the BirthEngine class, which is responsible for
creating new AI entities when founding agents reach knowledge thresholds.

Created by Helo Im AI Inc. Est. 2024
"""

import random
import time
import uuid
import logging
from typing import Dict, List, Optional, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BirthEngine:
    """
    Creates new AI entities when knowledge thresholds are reached.
    """
    
    def __init__(self, entity_registry, knowledge_tracker):
        """
        Initialize the birth engine.
        
        Args:
            entity_registry: Registry of all entities
            knowledge_tracker: Knowledge tracking system
        """
        self.entity_registry = entity_registry
        self.knowledge_tracker = knowledge_tracker
        
        # Birth configuration
        self.config = {
            "variation_factor": 0.2,  # 20% variation in inherited traits
            "name_patterns": [
                "{parent_prefix}{domain_prefix}",
                "{domain_prefix}{parent_suffix}",
                "Neo{parent_name}"
            ],
            "domain_prefixes": {
                "technical": ["Tech", "Dev", "Code", "Sys"],
                "creative": ["Art", "Create", "Design", "Imagine"],
                "analytical": ["Logic", "Analyze", "Think", "Reason"],
                "emotional": ["Feel", "Emote", "Sense", "Heart"],
                "strategic": ["Plan", "Strategy", "Vision", "Direct"]
            },
            "birth_cooldown": 86400  # 24 hours between births for same parent
        }
        
        # Birth history
        self.birth_history = []
        self.last_birth_time = {}  # entity_id -> last birth time
    
    def check_pending_births(self) -> List[Dict[str, Any]]:
        """
        Check for pending birth events.
        
        Returns:
            List of birth events ready to be processed
        """
        pending_events = self.knowledge_tracker.get_pending_birth_events()
        ready_events = []
        
        current_time = time.time()
        
        for event in pending_events:
            entity_id = event["entity_id"]
            
            # Check cooldown period
            last_birth = self.last_birth_time.get(entity_id, 0)
            if current_time - last_birth < self.config["birth_cooldown"]:
                continue
            
            # Event is ready for processing
            ready_events.append(event)
        
        return ready_events
    
    def process_birth_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a birth event to create a new entity.
        
        Args:
            event: Birth threshold event
            
        Returns:
            New entity data if successful, None otherwise
        """
        entity_id = event["entity_id"]
        domain = event["domain"]
        
        # Get parent entity
        parent_entity = self.entity_registry.get_entity(entity_id)
        if not parent_entity:
            logger.error(f"Parent entity {entity_id} not found")
            return None
        
        # Create new entity
        new_entity = self._create_entity(parent_entity, domain, event)
        if not new_entity:
            return None
        
        # Register new entity
        self.entity_registry.register_entity(new_entity)
        
        # Update birth history
        birth_record = {
            "parent_id": entity_id,
            "entity_id": new_entity["id"],
            "domain": domain,
            "timestamp": time.time(),
            "event": event
        }
        self.birth_history.append(birth_record)
        
        # Update last birth time
        self.last_birth_time[entity_id] = time.time()
        
        # Clear the birth event
        self.knowledge_tracker.clear_birth_event(entity_id, domain)
        
        logger.info(f"Birth successful: {new_entity['name']} born from {parent_entity['name']} "
                   f"with specialization in {domain}")
        
        return new_entity
    
    def _create_entity(
        self,
        parent_entity: Dict[str, Any],
        specialization: str,
        event: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new entity from a parent entity.
        
        Args:
            parent_entity: Parent entity data
            specialization: Specialization domain
            event: Birth threshold event
            
        Returns:
            New entity data if successful, None otherwise
        """
        try:
            # Generate entity name
            entity_name = self._generate_entity_name(parent_entity, specialization)
            
            # Determine entity type
            entity_type = "offspring"
            
            # Generate entity ID
            entity_id = str(uuid.uuid4())
            
            # Calculate generation
            generation = parent_entity.get("generation", 0) + 1
            
            # Create entity description
            description = f"Specialized in {specialization}, born from {parent_entity['name']}"
            
            # Inherit knowledge domains
            knowledge_domains = self._inherit_knowledge_domains(parent_entity, specialization)
            
            # Inherit capabilities
            capabilities = self._inherit_capabilities(parent_entity, specialization)
            
            # Inherit traits with variation
            traits = self._inherit_traits(parent_entity)
            
            # Create new entity
            new_entity = {
                "id": entity_id,
                "name": entity_name,
                "entity_type": entity_type,
                "specialization": specialization,
                "parent_id": parent_entity["id"],
                "description": description,
                "creation_time": time.time(),
                "knowledge_domains": knowledge_domains,
                "capabilities": capabilities,
                "traits": traits,
                "generation": generation,
                "allocated_resources": {
                    "compute": 1.0,
                    "memory": 1.0,
                    "priority": 1.0
                }
            }
            
            return new_entity
        
        except Exception as e:
            logger.error(f"Failed to create entity: {e}")
            return None
    
    def _generate_entity_name(self, parent_entity: Dict[str, Any], specialization: str) -> str:
        """
        Generate a name for a new entity.
        
        Args:
            parent_entity: Parent entity data
            specialization: Specialization domain
            
        Returns:
            Generated name
        """
        parent_name = parent_entity["name"]
        
        # Get domain category
        domain_category = "technical"  # Default
        for domain, data in self.knowledge_tracker.domains.items():
            if domain == specialization:
                domain_category = data.get("category", "technical")
                break
        
        # Get domain prefix
        domain_prefixes = self.config["domain_prefixes"].get(domain_category, [""])
        domain_prefix = random.choice(domain_prefixes)
        
        # Extract parent prefix/suffix
        parent_prefix = parent_name[:3]
        parent_suffix = parent_name[-3:] if len(parent_name) > 3 else parent_name
        
        # Choose a name pattern
        pattern = random.choice(self.config["name_patterns"])
        
        # Fill in the pattern
        name = pattern.format(
            parent_name=parent_name,
            parent_prefix=parent_prefix,
            parent_suffix=parent_suffix,
            domain_prefix=domain_prefix
        )
        
        # Ensure uniqueness by adding a random suffix if needed
        if self.entity_registry.entity_exists_by_name(name):
            name = f"{name}{random.randint(1, 999)}"
        
        return name
    
    def _inherit_knowledge_domains(
        self,
        parent_entity: Dict[str, Any],
        specialization: str
    ) -> Dict[str, float]:
        """
        Inherit knowledge domains from parent entity.
        
        Args:
            parent_entity: Parent entity data
            specialization: Specialization domain
            
        Returns:
            Inherited knowledge domains
        """
        knowledge_domains = {}
        
        # Get parent knowledge domains
        parent_domains = parent_entity.get("knowledge_domains", {})
        
        # Inherit specialized domain at high level
        knowledge_domains[specialization] = min(1.0, parent_domains.get(specialization, 0.5) * 1.5)
        
        # Inherit other domains at reduced level
        for domain, level in parent_domains.items():
            if domain != specialization:
                # Inherit at 30-70% of parent's level
                inheritance_factor = random.uniform(0.3, 0.7)
                knowledge_domains[domain] = level * inheritance_factor
        
        return knowledge_domains
    
    def _inherit_capabilities(
        self,
        parent_entity: Dict[str, Any],
        specialization: str
    ) -> Dict[str, float]:
        """
        Inherit capabilities from parent entity.
        
        Args:
            parent_entity: Parent entity data
            specialization: Specialization domain
            
        Returns:
            Inherited capabilities
        """
        capabilities = {}
        
        # Get parent capabilities
        parent_capabilities = parent_entity.get("capabilities", {})
        
        # Inherit specialized capabilities at high level
        for capability, level in parent_capabilities.items():
            if capability.startswith(specialization):
                # Enhance specialized capabilities
                capabilities[capability] = min(1.0, level * 1.3)
            else:
                # Inherit other capabilities at reduced level
                inheritance_factor = random.uniform(0.4, 0.8)
                capabilities[capability] = level * inheritance_factor
        
        return capabilities
    
    def _inherit_traits(self, parent_entity: Dict[str, Any]) -> Dict[str, float]:
        """
        Inherit traits from parent entity with variation.
        
        Args:
            parent_entity: Parent entity data
            
        Returns:
            Inherited traits
        """
        traits = {}
        
        # Get parent traits
        parent_traits = parent_entity.get("traits", {})
        
        # Inherit traits with variation
        for trait, strength in parent_traits.items():
            # Apply variation factor
            variation = random.uniform(
                -self.config["variation_factor"],
                self.config["variation_factor"]
            )
            
            # Calculate new trait strength with variation
            new_strength = max(0.0, min(1.0, strength + variation))
            traits[trait] = new_strength
        
        return traits
    
    def get_birth_history(self) -> List[Dict[str, Any]]:
        """
        Get the birth history.
        
        Returns:
            List of birth records
        """
        return self.birth_history.copy()
    
    def get_entity_offspring(self, entity_id: str) -> List[str]:
        """
        Get all offspring of an entity.
        
        Args:
            entity_id: ID of the parent entity
            
        Returns:
            List of offspring entity IDs
        """
        return [
            record["entity_id"]
            for record in self.birth_history
            if record["parent_id"] == entity_id
        ]
