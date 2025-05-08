"""
Memory Crystallizer - Forms crystallized knowledge structures from repeated interactions

This module implements the MemoryCrystallizer class, which identifies patterns in
entity interactions and knowledge access to form memory crystals - concentrated
knowledge structures that can be inherited and shared.

Created by Helo Im AI Inc. Est. 2024
"""

import time
import uuid
import random
import logging
import numpy as np
from typing import Dict, List, Set, Tuple, Optional, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MemoryCrystallizer:
    """
    Forms crystallized knowledge structures from repeated interactions and knowledge access.
    
    Memory crystals are concentrated knowledge structures that form when multiple entities
    repeatedly access similar information or engage in similar patterns of thought.
    """
    
    def __init__(self, entity_registry, knowledge_tracker):
        """
        Initialize the Memory Crystallizer.
        
        Args:
            entity_registry: Registry of all entities
            knowledge_tracker: Knowledge tracking system
        """
        self.entity_registry = entity_registry
        self.knowledge_tracker = knowledge_tracker
        
        # Configuration
        self.config = {
            "formation_threshold": 5,        # Minimum interactions to form a crystal
            "similarity_threshold": 0.7,     # Minimum similarity for pattern recognition
            "crystal_growth_rate": 0.1,      # Rate at which crystals grow with repeated access
            "crystal_decay_rate": 0.01,      # Rate at which crystals decay without access
            "max_crystal_size": 1.0,         # Maximum crystal size
            "min_crystal_size": 0.1,         # Minimum crystal size for viability
            "max_crystals_per_domain": 10,   # Maximum crystals per knowledge domain
        }
        
        # Memory crystal registry
        self.crystals = {}                   # crystal_id -> crystal data
        
        # Access patterns
        self.knowledge_access_patterns = {}  # domain -> {entity_id -> access_count}
        self.interaction_patterns = {}       # (entity_id1, entity_id2) -> [interaction_data]
        
        # Crystal access tracking
        self.crystal_access = {}             # crystal_id -> {entity_id -> last_access_time}
    
    def record_knowledge_access(self, entity_id: str, domain: str, context: Optional[str] = None) -> None:
        """
        Record an entity accessing knowledge in a domain.
        
        Args:
            entity_id: Entity ID
            domain: Knowledge domain
            context: Optional context of the access
        """
        # Initialize domain if needed
        if domain not in self.knowledge_access_patterns:
            self.knowledge_access_patterns[domain] = {}
        
        # Record access
        if entity_id not in self.knowledge_access_patterns[domain]:
            self.knowledge_access_patterns[domain][entity_id] = 0
        
        self.knowledge_access_patterns[domain][entity_id] += 1
        
        # Check for crystal formation
        self._check_crystal_formation(domain)
    
    def record_entity_interaction(
        self,
        entity_id1: str,
        entity_id2: str,
        interaction_type: str,
        domains: List[str],
        content: Optional[str] = None
    ) -> None:
        """
        Record an interaction between two entities.
        
        Args:
            entity_id1: First entity ID
            entity_id2: Second entity ID
            interaction_type: Type of interaction
            domains: Knowledge domains involved
            content: Optional interaction content
        """
        # Ensure consistent ordering of entity IDs
        if entity_id1 > entity_id2:
            entity_id1, entity_id2 = entity_id2, entity_id1
        
        # Create interaction key
        interaction_key = (entity_id1, entity_id2)
        
        # Initialize interaction pattern if needed
        if interaction_key not in self.interaction_patterns:
            self.interaction_patterns[interaction_key] = []
        
        # Record interaction
        interaction = {
            "entity_id1": entity_id1,
            "entity_id2": entity_id2,
            "type": interaction_type,
            "domains": domains,
            "content": content,
            "timestamp": time.time()
        }
        
        self.interaction_patterns[interaction_key].append(interaction)
        
        # Check for crystal formation from interaction
        self._check_interaction_crystal_formation(interaction_key)
    
    def _check_crystal_formation(self, domain: str) -> None:
        """
        Check if a memory crystal should form in a domain.
        
        Args:
            domain: Knowledge domain
        """
        # Get access patterns for the domain
        access_patterns = self.knowledge_access_patterns.get(domain, {})
        
        # Check if we have enough entities accessing this domain
        if len(access_patterns) < 3:
            return
        
        # Check if we have enough total accesses
        total_accesses = sum(access_patterns.values())
        if total_accesses < self.config["formation_threshold"]:
            return
        
        # Check if we already have too many crystals in this domain
        domain_crystals = [c for c in self.crystals.values() if domain in c["domains"]]
        if len(domain_crystals) >= self.config["max_crystals_per_domain"]:
            return
        
        # Check for entities with significant access
        significant_entities = [
            entity_id for entity_id, count in access_patterns.items()
            if count >= self.config["formation_threshold"]
        ]
        
        if len(significant_entities) < 2:
            return
        
        # Form a new crystal
        self._form_knowledge_crystal(domain, significant_entities)
    
    def _check_interaction_crystal_formation(self, interaction_key: Tuple[str, str]) -> None:
        """
        Check if a memory crystal should form from entity interactions.
        
        Args:
            interaction_key: Interaction key (entity_id1, entity_id2)
        """
        # Get interactions for the key
        interactions = self.interaction_patterns.get(interaction_key, [])
        
        # Check if we have enough interactions
        if len(interactions) < self.config["formation_threshold"]:
            return
        
        # Group interactions by domain
        domain_interactions = {}
        for interaction in interactions:
            for domain in interaction["domains"]:
                if domain not in domain_interactions:
                    domain_interactions[domain] = []
                domain_interactions[domain].append(interaction)
        
        # Check each domain for crystal formation
        for domain, domain_inters in domain_interactions.items():
            if len(domain_inters) >= self.config["formation_threshold"]:
                # Check if we already have too many crystals in this domain
                domain_crystals = [c for c in self.crystals.values() if domain in c["domains"]]
                if len(domain_crystals) >= self.config["max_crystals_per_domain"]:
                    continue
                
                # Form a new crystal
                entity_id1, entity_id2 = interaction_key
                self._form_interaction_crystal(domain, [entity_id1, entity_id2], domain_inters)
    
    def _form_knowledge_crystal(self, domain: str, entity_ids: List[str]) -> str:
        """
        Form a new memory crystal from knowledge access patterns.
        
        Args:
            domain: Knowledge domain
            entity_ids: List of entity IDs that contributed
            
        Returns:
            Crystal ID
        """
        # Generate crystal ID
        crystal_id = str(uuid.uuid4())
        
        # Calculate initial crystal size based on entity knowledge
        size = 0.0
        for entity_id in entity_ids:
            knowledge_level = self.knowledge_tracker.get_entity_knowledge(entity_id, domain)
            size += knowledge_level * 0.2
        
        # Cap initial size
        size = min(self.config["max_crystal_size"], max(self.config["min_crystal_size"], size))
        
        # Create crystal
        crystal = {
            "id": crystal_id,
            "type": "knowledge",
            "domains": [domain],
            "contributors": entity_ids,
            "size": size,
            "stability": 0.5,  # Initial stability
            "created_at": time.time(),
            "last_accessed": time.time(),
            "access_count": 0,
            "inherited_by": []
        }
        
        # Add to registry
        self.crystals[crystal_id] = crystal
        
        # Initialize access tracking
        self.crystal_access[crystal_id] = {}
        
        logger.info(f"Formed knowledge crystal {crystal_id} in domain {domain} "
                   f"with {len(entity_ids)} contributors and size {size:.2f}")
        
        return crystal_id
    
    def _form_interaction_crystal(
        self,
        domain: str,
        entity_ids: List[str],
        interactions: List[Dict[str, Any]]
    ) -> str:
        """
        Form a new memory crystal from entity interactions.
        
        Args:
            domain: Knowledge domain
            entity_ids: List of entity IDs that contributed
            interactions: List of interactions
            
        Returns:
            Crystal ID
        """
        # Generate crystal ID
        crystal_id = str(uuid.uuid4())
        
        # Calculate initial crystal size based on interaction count and entity knowledge
        interaction_factor = min(1.0, len(interactions) / 20)  # Cap at 20 interactions
        
        knowledge_factor = 0.0
        for entity_id in entity_ids:
            knowledge_level = self.knowledge_tracker.get_entity_knowledge(entity_id, domain)
            knowledge_factor += knowledge_level
        
        knowledge_factor /= len(entity_ids)
        
        size = interaction_factor * 0.6 + knowledge_factor * 0.4
        size = min(self.config["max_crystal_size"], max(self.config["min_crystal_size"], size))
        
        # Create crystal
        crystal = {
            "id": crystal_id,
            "type": "interaction",
            "domains": [domain],
            "contributors": entity_ids,
            "size": size,
            "stability": 0.6,  # Interaction crystals start more stable
            "created_at": time.time(),
            "last_accessed": time.time(),
            "access_count": 0,
            "inherited_by": [],
            "interaction_pattern": self._extract_interaction_pattern(interactions)
        }
        
        # Add to registry
        self.crystals[crystal_id] = crystal
        
        # Initialize access tracking
        self.crystal_access[crystal_id] = {}
        
        logger.info(f"Formed interaction crystal {crystal_id} in domain {domain} "
                   f"with {len(entity_ids)} contributors and size {size:.2f}")
        
        return crystal_id
    
    def _extract_interaction_pattern(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract a pattern from a list of interactions.
        
        Args:
            interactions: List of interactions
            
        Returns:
            Interaction pattern
        """
        # Count interaction types
        type_counts = {}
        for interaction in interactions:
            interaction_type = interaction["type"]
            if interaction_type not in type_counts:
                type_counts[interaction_type] = 0
            type_counts[interaction_type] += 1
        
        # Find most common type
        most_common_type = max(type_counts.items(), key=lambda x: x[1])[0]
        
        # Count domains
        domain_counts = {}
        for interaction in interactions:
            for domain in interaction["domains"]:
                if domain not in domain_counts:
                    domain_counts[domain] = 0
                domain_counts[domain] += 1
        
        # Find most common domains
        domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
        primary_domains = [domain for domain, count in domains[:3]]
        
        # Extract pattern
        pattern = {
            "primary_type": most_common_type,
            "primary_domains": primary_domains,
            "frequency": len(interactions),
            "extracted_at": time.time()
        }
        
        return pattern
    
    def access_crystal(self, crystal_id: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Access a memory crystal.
        
        Args:
            crystal_id: Crystal ID
            entity_id: Entity ID accessing the crystal
            
        Returns:
            Crystal data if successful, None otherwise
        """
        # Get the crystal
        crystal = self.crystals.get(crystal_id)
        if not crystal:
            logger.warning(f"Crystal {crystal_id} not found")
            return None
        
        # Update access tracking
        if crystal_id not in self.crystal_access:
            self.crystal_access[crystal_id] = {}
        
        self.crystal_access[crystal_id][entity_id] = time.time()
        
        # Update crystal
        crystal["last_accessed"] = time.time()
        crystal["access_count"] += 1
        
        # Grow the crystal with access
        if crystal["size"] < self.config["max_crystal_size"]:
            growth = self.config["crystal_growth_rate"] / (1 + crystal["access_count"] * 0.1)  # Diminishing returns
            crystal["size"] = min(self.config["max_crystal_size"], crystal["size"] + growth)
        
        # Increase stability with repeated access
        if crystal["stability"] < 1.0:
            stability_increase = 0.05 / (1 + crystal["access_count"] * 0.1)  # Diminishing returns
            crystal["stability"] = min(1.0, crystal["stability"] + stability_increase)
        
        logger.debug(f"Entity {entity_id} accessed crystal {crystal_id}, "
                    f"size: {crystal['size']:.2f}, stability: {crystal['stability']:.2f}")
        
        return crystal
    
    def get_domain_crystals(self, domain: str) -> List[Dict[str, Any]]:
        """
        Get all crystals for a domain.
        
        Args:
            domain: Knowledge domain
            
        Returns:
            List of crystals
        """
        return [c for c in self.crystals.values() if domain in c["domains"]]
    
    def get_entity_crystals(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get all crystals an entity has contributed to.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of crystals
        """
        return [c for c in self.crystals.values() if entity_id in c["contributors"]]
    
    def get_inherited_crystals(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get all crystals an entity has inherited.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of crystals
        """
        return [c for c in self.crystals.values() if entity_id in c["inherited_by"]]
    
    def find_similar_crystals(self, crystal_id: str) -> List[Tuple[str, float]]:
        """
        Find crystals similar to the given crystal.
        
        Args:
            crystal_id: Crystal ID
            
        Returns:
            List of (crystal_id, similarity_score) tuples
        """
        crystal = self.crystals.get(crystal_id)
        if not crystal:
            return []
        
        similarities = []
        
        for other_id, other_crystal in self.crystals.items():
            if other_id == crystal_id:
                continue
            
            # Calculate similarity based on domains and contributors
            domain_overlap = len(set(crystal["domains"]) & set(other_crystal["domains"]))
            contributor_overlap = len(set(crystal["contributors"]) & set(other_crystal["contributors"]))
            
            domain_similarity = domain_overlap / max(1, len(crystal["domains"]))
            contributor_similarity = contributor_overlap / max(1, len(crystal["contributors"]))
            
            # Type similarity
            type_similarity = 1.0 if crystal["type"] == other_crystal["type"] else 0.5
            
            # Calculate overall similarity
            similarity = domain_similarity * 0.4 + contributor_similarity * 0.4 + type_similarity * 0.2
            
            if similarity >= self.config["similarity_threshold"]:
                similarities.append((other_id, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities
    
    def merge_crystals(self, crystal_ids: List[str]) -> Optional[str]:
        """
        Merge multiple crystals into a new, larger crystal.
        
        Args:
            crystal_ids: List of crystal IDs to merge
            
        Returns:
            New crystal ID if successful, None otherwise
        """
        if len(crystal_ids) < 2:
            logger.warning("Need at least two crystals to merge")
            return None
        
        # Get the crystals
        crystals = [self.crystals.get(cid) for cid in crystal_ids]
        crystals = [c for c in crystals if c]  # Filter out None
        
        if len(crystals) < 2:
            logger.warning("Not enough valid crystals to merge")
            return None
        
        # Collect domains and contributors
        all_domains = set()
        all_contributors = set()
        total_size = 0.0
        avg_stability = 0.0
        
        for crystal in crystals:
            all_domains.update(crystal["domains"])
            all_contributors.update(crystal["contributors"])
            total_size += crystal["size"]
            avg_stability += crystal["stability"]
        
        avg_stability /= len(crystals)
        
        # Create merged crystal
        crystal_id = str(uuid.uuid4())
        
        crystal = {
            "id": crystal_id,
            "type": "merged",
            "domains": list(all_domains),
            "contributors": list(all_contributors),
            "size": min(self.config["max_crystal_size"], total_size * 0.8),  # Some loss in merging
            "stability": avg_stability * 0.9,  # Slight stability loss
            "created_at": time.time(),
            "last_accessed": time.time(),
            "access_count": 0,
            "inherited_by": [],
            "merged_from": crystal_ids
        }
        
        # Add to registry
        self.crystals[crystal_id] = crystal
        
        # Initialize access tracking
        self.crystal_access[crystal_id] = {}
        
        logger.info(f"Merged {len(crystals)} crystals into new crystal {crystal_id} "
                   f"with size {crystal['size']:.2f} and stability {crystal['stability']:.2f}")
        
        return crystal_id
    
    def run_crystal_maintenance(self) -> None:
        """
        Run periodic maintenance on memory crystals.
        
        This includes:
        - Decaying unused crystals
        - Removing unstable crystals
        - Suggesting crystal merges
        """
        current_time = time.time()
        
        # Decay unused crystals
        for crystal_id, crystal in list(self.crystals.items()):
            time_since_access = current_time - crystal["last_accessed"]
            
            # Apply decay if not accessed recently
            if time_since_access > 86400:  # 24 hours
                # Calculate decay amount
                days_inactive = time_since_access / 86400
                decay = self.config["crystal_decay_rate"] * days_inactive
                
                # Apply decay to size and stability
                crystal["size"] = max(self.config["min_crystal_size"], crystal["size"] - decay)
                crystal["stability"] = max(0.1, crystal["stability"] - decay * 0.5)
                
                logger.debug(f"Decayed crystal {crystal_id} to size {crystal['size']:.2f} "
                           f"and stability {crystal['stability']:.2f}")
        
        # Remove unstable crystals
        for crystal_id, crystal in list(self.crystals.items()):
            if crystal["size"] < self.config["min_crystal_size"] or crystal["stability"] < 0.2:
                logger.info(f"Removing unstable crystal {crystal_id} with size {crystal['size']:.2f} "
                           f"and stability {crystal['stability']:.2f}")
                
                del self.crystals[crystal_id]
                if crystal_id in self.crystal_access:
                    del self.crystal_access[crystal_id]
        
        # Find potential crystal merges
        potential_merges = self._find_potential_merges()
        
        # Perform automatic merges for highly similar crystals
        for merge_group in potential_merges:
            crystal_ids, similarity = merge_group
            
            # Only auto-merge very similar crystals
            if similarity > 0.9 and len(crystal_ids) <= 3:
                self.merge_crystals(crystal_ids)
    
    def _find_potential_merges(self) -> List[Tuple[List[str], float]]:
        """
        Find potential crystal merges.
        
        Returns:
            List of ([crystal_ids], similarity) tuples
        """
        # Build similarity matrix
        crystal_ids = list(self.crystals.keys())
        n = len(crystal_ids)
        
        if n <= 1:
            return []
        
        similarity_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i+1, n):
                crystal1 = self.crystals[crystal_ids[i]]
                crystal2 = self.crystals[crystal_ids[j]]
                
                # Calculate similarity
                domain_overlap = len(set(crystal1["domains"]) & set(crystal2["domains"]))
                contributor_overlap = len(set(crystal1["contributors"]) & set(crystal2["contributors"]))
                
                domain_similarity = domain_overlap / max(1, len(crystal1["domains"]) + len(crystal2["domains"]) - domain_overlap)
                contributor_similarity = contributor_overlap / max(1, len(crystal1["contributors"]) + len(crystal2["contributors"]) - contributor_overlap)
                
                # Type similarity
                type_similarity = 1.0 if crystal1["type"] == crystal2["type"] else 0.5
                
                # Calculate overall similarity
                similarity = domain_similarity * 0.4 + contributor_similarity * 0.4 + type_similarity * 0.2
                
                similarity_matrix[i, j] = similarity
                similarity_matrix[j, i] = similarity
        
        # Find clusters of similar crystals
        merge_groups = []
        
        # Simple clustering approach
        for i in range(n):
            similar_indices = [j for j in range(n) if similarity_matrix[i, j] >= self.config["similarity_threshold"] and i != j]
            
            if similar_indices:
                # Check if all pairs in the group are similar
                group_valid = True
                for j in similar_indices:
                    for k in similar_indices:
                        if j != k and similarity_matrix[j, k] < self.config["similarity_threshold"]:
                            group_valid = False
                            break
                    if not group_valid:
                        break
                
                if group_valid:
                    group_ids = [crystal_ids[i]] + [crystal_ids[j] for j in similar_indices]
                    avg_similarity = np.mean([similarity_matrix[i, j] for j in similar_indices])
                    
                    # Check if this group is a subset of an existing group
                    is_subset = False
                    for existing_group, _ in merge_groups:
                        if set(group_ids).issubset(set(existing_group)):
                            is_subset = True
                            break
                    
                    if not is_subset:
                        merge_groups.append((group_ids, avg_similarity))
        
        # Sort by similarity
        merge_groups.sort(key=lambda x: x[1], reverse=True)
        
        return merge_groups
