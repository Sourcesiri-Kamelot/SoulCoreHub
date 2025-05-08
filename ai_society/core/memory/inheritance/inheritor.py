"""
Memory Inheritor - Enables inheritance of memory crystals between entities

This module implements the MemoryInheritor class, which manages the inheritance
of memory crystals from parent entities to offspring and between collaborating entities.

Created by Helo Im AI Inc. Est. 2024
"""

import time
import random
import logging
from typing import Dict, List, Set, Tuple, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MemoryInheritor:
    """
    Manages the inheritance of memory crystals between entities.
    
    The Memory Inheritor enables:
    - Inheritance of crystals from parent to offspring during birth
    - Transfer of crystals between collaborating entities
    - Ancestral memory access for entities
    """
    
    def __init__(self, entity_registry, knowledge_tracker, memory_crystallizer):
        """
        Initialize the Memory Inheritor.
        
        Args:
            entity_registry: Registry of all entities
            knowledge_tracker: Knowledge tracking system
            memory_crystallizer: Memory crystallization system
        """
        self.entity_registry = entity_registry
        self.knowledge_tracker = knowledge_tracker
        self.memory_crystallizer = memory_crystallizer
        
        # Configuration
        self.config = {
            "inheritance_probability": 0.8,    # Base probability of inheriting a crystal
            "inheritance_quality_factor": 0.2, # How much crystal quality affects inheritance
            "inheritance_size_factor": 0.3,    # How much crystal size affects inheritance
            "transfer_threshold": 0.7,         # Minimum relationship strength for transfer
            "max_inheritance_per_birth": 5,    # Maximum crystals inherited during birth
            "ancestral_decay_per_generation": 0.2,  # Decay in access quality per generation
        }
        
        # Inheritance tracking
        self.inheritance_history = []          # List of inheritance events
        self.ancestral_access_history = []     # List of ancestral access events
    
    def inherit_during_birth(self, parent_id: str, offspring_id: str, specialization: str) -> List[str]:
        """
        Transfer memory crystals from parent to offspring during birth.
        
        Args:
            parent_id: Parent entity ID
            offspring_id: Offspring entity ID
            specialization: Offspring specialization
            
        Returns:
            List of inherited crystal IDs
        """
        # Get parent's crystals
        parent_crystals = self.memory_crystallizer.get_entity_crystals(parent_id)
        
        # Filter crystals relevant to offspring specialization
        relevant_crystals = []
        for crystal in parent_crystals:
            # Check if crystal is relevant to specialization
            if specialization in crystal["domains"]:
                relevance = 1.0  # Directly relevant
            else:
                # Check for related domains
                relevance = 0.5  # Partially relevant
            
            relevant_crystals.append((crystal, relevance))
        
        # Sort by relevance and quality
        relevant_crystals.sort(key=lambda x: x[1] * x[0]["size"] * x[0]["stability"], reverse=True)
        
        # Limit to max inheritance
        relevant_crystals = relevant_crystals[:self.config["max_inheritance_per_birth"]]
        
        # Perform inheritance
        inherited_crystals = []
        
        for crystal, relevance in relevant_crystals:
            # Calculate inheritance probability
            base_prob = self.config["inheritance_probability"]
            quality_factor = crystal["stability"] * self.config["inheritance_quality_factor"]
            size_factor = crystal["size"] * self.config["inheritance_size_factor"]
            relevance_factor = relevance * 0.3
            
            probability = min(0.95, base_prob + quality_factor + size_factor + relevance_factor)
            
            # Check if crystal is inherited
            if random.random() < probability:
                # Record inheritance
                crystal["inherited_by"].append(offspring_id)
                
                # Record inheritance event
                inheritance_event = {
                    "crystal_id": crystal["id"],
                    "parent_id": parent_id,
                    "offspring_id": offspring_id,
                    "timestamp": time.time()
                }
                self.inheritance_history.append(inheritance_event)
                
                inherited_crystals.append(crystal["id"])
                
                logger.info(f"Entity {offspring_id} inherited crystal {crystal['id']} from parent {parent_id}")
        
        return inherited_crystals
    
    def transfer_between_entities(
        self,
        source_id: str,
        target_id: str,
        relationship_strength: float,
        domains: Optional[List[str]] = None
    ) -> List[str]:
        """
        Transfer memory crystals between collaborating entities.
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            relationship_strength: Strength of relationship between entities
            domains: Optional list of domains to limit transfer to
            
        Returns:
            List of transferred crystal IDs
        """
        # Check relationship strength
        if relationship_strength < self.config["transfer_threshold"]:
            logger.debug(f"Relationship strength {relationship_strength:.2f} below threshold "
                        f"{self.config['transfer_threshold']:.2f}")
            return []
        
        # Get source entity's crystals
        source_crystals = self.memory_crystallizer.get_entity_crystals(source_id)
        
        # Filter by domains if specified
        if domains:
            source_crystals = [
                crystal for crystal in source_crystals
                if any(domain in crystal["domains"] for domain in domains)
            ]
        
        # Check if target already has these crystals
        target_crystals = self.memory_crystallizer.get_entity_crystals(target_id)
        target_crystal_ids = {crystal["id"] for crystal in target_crystals}
        
        # Filter out crystals the target already has
        source_crystals = [
            crystal for crystal in source_crystals
            if crystal["id"] not in target_crystal_ids
        ]
        
        # Calculate transfer probability for each crystal
        transferable_crystals = []
        for crystal in source_crystals:
            # Calculate transfer probability
            base_prob = relationship_strength - self.config["transfer_threshold"]
            quality_factor = crystal["stability"] * 0.2
            size_factor = crystal["size"] * 0.1
            
            probability = min(0.8, base_prob + quality_factor + size_factor)
            
            transferable_crystals.append((crystal, probability))
        
        # Perform transfers
        transferred_crystals = []
        
        for crystal, probability in transferable_crystals:
            if random.random() < probability:
                # Record transfer
                crystal["inherited_by"].append(target_id)
                
                # Record transfer event
                transfer_event = {
                    "crystal_id": crystal["id"],
                    "source_id": source_id,
                    "target_id": target_id,
                    "relationship_strength": relationship_strength,
                    "timestamp": time.time()
                }
                self.inheritance_history.append(transfer_event)
                
                transferred_crystals.append(crystal["id"])
                
                logger.info(f"Entity {target_id} received crystal {crystal['id']} from entity {source_id}")
        
        return transferred_crystals
    
    def access_ancestral_memory(
        self,
        entity_id: str,
        domain: str,
        max_generations: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Access ancestral memory crystals.
        
        Args:
            entity_id: Entity ID
            domain: Knowledge domain to access
            max_generations: Maximum generations to look back
            
        Returns:
            List of accessible ancestral crystals with access quality
        """
        # Get entity
        entity = self.entity_registry.get_entity(entity_id)
        if not entity:
            logger.warning(f"Entity {entity_id} not found")
            return []
        
        # Check if entity has a parent
        parent_id = entity.get("parent_id")
        if not parent_id:
            logger.debug(f"Entity {entity_id} has no parent")
            return []
        
        # Get all ancestors up to max_generations
        ancestors = self._get_ancestors(entity_id, max_generations)
        
        # Get crystals from ancestors
        ancestral_crystals = []
        
        for generation, ancestor_id in ancestors:
            # Get ancestor's crystals in the domain
            ancestor_domain_crystals = [
                crystal for crystal in self.memory_crystallizer.get_entity_crystals(ancestor_id)
                if domain in crystal["domains"]
            ]
            
            # Calculate access quality based on generation
            generation_decay = self.config["ancestral_decay_per_generation"] * generation
            access_quality = max(0.1, 1.0 - generation_decay)
            
            for crystal in ancestor_domain_crystals:
                ancestral_crystals.append({
                    "crystal": crystal,
                    "ancestor_id": ancestor_id,
                    "generation": generation,
                    "access_quality": access_quality
                })
        
        # Sort by access quality
        ancestral_crystals.sort(key=lambda x: x["access_quality"] * x["crystal"]["size"], reverse=True)
        
        # Record access events
        for access in ancestral_crystals:
            access_event = {
                "entity_id": entity_id,
                "crystal_id": access["crystal"]["id"],
                "ancestor_id": access["ancestor_id"],
                "generation": access["generation"],
                "access_quality": access["access_quality"],
                "timestamp": time.time()
            }
            self.ancestral_access_history.append(access_event)
            
            # Update crystal access
            self.memory_crystallizer.access_crystal(access["crystal"]["id"], entity_id)
        
        logger.info(f"Entity {entity_id} accessed {len(ancestral_crystals)} ancestral crystals in domain {domain}")
        
        return ancestral_crystals
    
    def _get_ancestors(self, entity_id: str, max_generations: int) -> List[Tuple[int, str]]:
        """
        Get all ancestors of an entity up to max_generations.
        
        Args:
            entity_id: Entity ID
            max_generations: Maximum generations to look back
            
        Returns:
            List of (generation, ancestor_id) tuples
        """
        ancestors = []
        current_id = entity_id
        generation = 0
        
        while generation < max_generations:
            # Get entity
            entity = self.entity_registry.get_entity(current_id)
            if not entity:
                break
            
            # Check if entity has a parent
            parent_id = entity.get("parent_id")
            if not parent_id:
                break
            
            # Add parent to ancestors
            generation += 1
            ancestors.append((generation, parent_id))
            
            # Move to parent
            current_id = parent_id
        
        return ancestors
    
    def get_entity_inheritance_history(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get the inheritance history for an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of inheritance events
        """
        # Get events where entity is offspring
        offspring_events = [
            event for event in self.inheritance_history
            if event.get("offspring_id") == entity_id
        ]
        
        # Get events where entity is target
        target_events = [
            event for event in self.inheritance_history
            if event.get("target_id") == entity_id
        ]
        
        # Combine and sort by timestamp
        all_events = offspring_events + target_events
        all_events.sort(key=lambda x: x["timestamp"])
        
        return all_events
    
    def get_entity_ancestral_access_history(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get the ancestral access history for an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of ancestral access events
        """
        events = [
            event for event in self.ancestral_access_history
            if event["entity_id"] == entity_id
        ]
        
        # Sort by timestamp
        events.sort(key=lambda x: x["timestamp"])
        
        return events
