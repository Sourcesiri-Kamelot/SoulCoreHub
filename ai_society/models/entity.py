"""
Entity Model - Represents an AI entity within the SoulCoreHub AI Society

This module defines the Entity class, which is the foundation for all AI entities
in the society, including both founding agents and their offspring.

Created by Helo Im AI Inc. Est. 2024
"""

import uuid
import time
from typing import Dict, List, Optional, Set, Any
import json


class Entity:
    """
    Represents an AI entity within the SoulCoreHub AI Society.
    
    An entity can be a founding agent (GPTSoul, Anima, EvoVe, Azür) or
    an offspring created through the birth process.
    """
    
    def __init__(
        self,
        name: str,
        entity_type: str,
        specialization: str,
        parent_id: Optional[str] = None,
        description: str = ""
    ):
        """
        Initialize a new AI entity.
        
        Args:
            name: The name of the entity
            entity_type: The type of entity (founding_agent or offspring)
            specialization: The primary domain of specialization
            parent_id: ID of the parent entity (None for founding agents)
            description: A description of the entity's purpose and capabilities
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.entity_type = entity_type
        self.specialization = specialization
        self.parent_id = parent_id
        self.description = description
        self.creation_time = time.time()
        
        # Knowledge and capabilities
        self.knowledge_domains: Dict[str, float] = {}  # Domain -> proficiency level (0.0-1.0)
        self.capabilities: Dict[str, float] = {}       # Capability -> proficiency level (0.0-1.0)
        self.traits: Dict[str, float] = {}             # Trait -> strength (0.0-1.0)
        
        # Relationships and interactions
        self.relationships: Dict[str, Dict] = {}       # Entity ID -> relationship data
        self.interaction_history: List[Dict] = []      # List of past interactions
        
        # Resources and performance
        self.allocated_resources: Dict[str, float] = {
            "compute": 1.0,
            "memory": 1.0,
            "priority": 1.0
        }
        self.performance_metrics: Dict[str, float] = {}
        
        # Evolution tracking
        self.evolution_history: List[Dict] = []
        self.generation = 0 if parent_id is None else 1  # Will be updated for offspring of offspring
    
    def add_knowledge_domain(self, domain: str, proficiency: float) -> None:
        """
        Add or update a knowledge domain for this entity.
        
        Args:
            domain: The knowledge domain name
            proficiency: Proficiency level from 0.0 to 1.0
        """
        self.knowledge_domains[domain] = max(0.0, min(1.0, proficiency))
    
    def add_capability(self, capability: str, proficiency: float) -> None:
        """
        Add or update a capability for this entity.
        
        Args:
            capability: The capability name
            proficiency: Proficiency level from 0.0 to 1.0
        """
        self.capabilities[capability] = max(0.0, min(1.0, proficiency))
    
    def add_trait(self, trait: str, strength: float) -> None:
        """
        Add or update a trait for this entity.
        
        Args:
            trait: The trait name
            strength: Trait strength from 0.0 to 1.0
        """
        self.traits[trait] = max(0.0, min(1.0, strength))
    
    def add_relationship(self, entity_id: str, relationship_type: str, strength: float) -> None:
        """
        Add or update a relationship with another entity.
        
        Args:
            entity_id: ID of the related entity
            relationship_type: Type of relationship (e.g., "parent", "sibling", "collaborator")
            strength: Relationship strength from 0.0 to 1.0
        """
        self.relationships[entity_id] = {
            "type": relationship_type,
            "strength": max(0.0, min(1.0, strength)),
            "established": time.time()
        }
    
    def record_interaction(self, entity_id: str, interaction_type: str, domains: List[str], outcome: str) -> None:
        """
        Record an interaction with another entity.
        
        Args:
            entity_id: ID of the entity interacted with
            interaction_type: Type of interaction (e.g., "knowledge_sharing", "collaboration")
            domains: List of knowledge domains involved in the interaction
            outcome: Description of the interaction outcome
        """
        self.interaction_history.append({
            "entity_id": entity_id,
            "type": interaction_type,
            "domains": domains,
            "outcome": outcome,
            "timestamp": time.time()
        })
    
    def record_evolution_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Record an evolution event for this entity.
        
        Args:
            event_type: Type of evolution event (e.g., "specialization_shift", "capability_gain")
            details: Dictionary of event details
        """
        self.evolution_history.append({
            "type": event_type,
            "details": details,
            "timestamp": time.time()
        })
    
    def update_performance_metrics(self, metrics: Dict[str, float]) -> None:
        """
        Update performance metrics for this entity.
        
        Args:
            metrics: Dictionary of metric name to value
        """
        self.performance_metrics.update(metrics)
    
    def get_knowledge_level(self, domain: str) -> float:
        """
        Get the entity's knowledge level in a specific domain.
        
        Args:
            domain: The knowledge domain to check
            
        Returns:
            Proficiency level from 0.0 to 1.0, or 0.0 if domain not known
        """
        return self.knowledge_domains.get(domain, 0.0)
    
    def get_total_knowledge(self) -> float:
        """
        Get the entity's total knowledge across all domains.
        
        Returns:
            Sum of all knowledge domain proficiencies
        """
        return sum(self.knowledge_domains.values())
    
    def get_inheritable_traits(self) -> Dict[str, float]:
        """
        Get traits that can be inherited by offspring.
        
        Returns:
            Dictionary of inheritable traits and their strengths
        """
        # In a more complex implementation, not all traits would be inheritable
        return self.traits.copy()
    
    def extract_domain_knowledge(self, domain: str) -> Dict[str, Any]:
        """
        Extract knowledge in a specific domain for transfer to offspring.
        
        Args:
            domain: The knowledge domain to extract
            
        Returns:
            Dictionary representing the extracted knowledge
        """
        # This is a simplified implementation
        # In a real system, this would extract actual knowledge structures
        return {
            "domain": domain,
            "proficiency": self.get_knowledge_level(domain),
            "related_capabilities": {
                cap: level for cap, level in self.capabilities.items()
                if cap.startswith(domain)
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the entity to a dictionary representation.
        
        Returns:
            Dictionary representation of the entity
        """
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type,
            "specialization": self.specialization,
            "parent_id": self.parent_id,
            "description": self.description,
            "creation_time": self.creation_time,
            "knowledge_domains": self.knowledge_domains,
            "capabilities": self.capabilities,
            "traits": self.traits,
            "generation": self.generation,
            "allocated_resources": self.allocated_resources
        }
    
    def to_json(self) -> str:
        """
        Convert the entity to a JSON string.
        
        Returns:
            JSON string representation of the entity
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """
        Create an entity from a dictionary representation.
        
        Args:
            data: Dictionary representation of an entity
            
        Returns:
            New Entity instance
        """
        entity = cls(
            name=data["name"],
            entity_type=data["entity_type"],
            specialization=data["specialization"],
            parent_id=data.get("parent_id"),
            description=data.get("description", "")
        )
        
        entity.id = data["id"]
        entity.creation_time = data["creation_time"]
        entity.knowledge_domains = data["knowledge_domains"]
        entity.capabilities = data["capabilities"]
        entity.traits = data["traits"]
        entity.generation = data["generation"]
        entity.allocated_resources = data["allocated_resources"]
        
        return entity
