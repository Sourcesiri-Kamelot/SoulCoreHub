"""
Memory Recoverer - Recovers dormant or forgotten knowledge

This module implements the MemoryRecoverer class, which identifies and recovers
valuable knowledge that has become dormant or forgotten within the AI Society.

Created by Helo Im AI Inc. Est. 2024
"""

import time
import random
import logging
import numpy as np
from typing import Dict, List, Set, Tuple, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MemoryRecoverer:
    """
    Identifies and recovers valuable dormant or forgotten knowledge.
    
    The Memory Recoverer:
    - Identifies dormant knowledge crystals
    - Recovers forgotten knowledge through pattern analysis
    - Connects related knowledge across different domains
    - Revitalizes valuable but unused knowledge
    """
    
    def __init__(self, entity_registry, knowledge_tracker, memory_crystallizer):
        """
        Initialize the Memory Recoverer.
        
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
            "dormancy_threshold": 604800,     # 7 days in seconds
            "recovery_threshold": 0.6,        # Minimum quality for recovery
            "connection_threshold": 0.7,      # Minimum similarity for connections
            "max_recoveries_per_run": 5,      # Maximum recoveries per run
            "recovery_boost": 0.3,            # Size/stability boost for recovered crystals
            "novelty_threshold": 0.6,         # Minimum novelty for recovery
        }
        
        # Recovery tracking
        self.recovery_history = []            # List of recovery events
        self.dormant_crystals = {}            # crystal_id -> dormancy data
        self.forgotten_patterns = []          # List of forgotten knowledge patterns
    
    def identify_dormant_crystals(self) -> List[Dict[str, Any]]:
        """
        Identify dormant knowledge crystals.
        
        Returns:
            List of dormant crystals with dormancy data
        """
        current_time = time.time()
        dormant_crystals = []
        
        for crystal_id, crystal in self.memory_crystallizer.crystals.items():
            # Check if crystal has not been accessed recently
            time_since_access = current_time - crystal["last_accessed"]
            
            if time_since_access > self.config["dormancy_threshold"]:
                # Calculate dormancy level
                dormancy_level = min(1.0, time_since_access / (self.config["dormancy_threshold"] * 3))
                
                # Calculate recovery value based on crystal quality and size
                recovery_value = crystal["size"] * crystal["stability"] * (1.0 - dormancy_level * 0.3)
                
                # Only consider valuable crystals
                if recovery_value >= self.config["recovery_threshold"]:
                    dormancy_data = {
                        "crystal_id": crystal_id,
                        "dormancy_level": dormancy_level,
                        "recovery_value": recovery_value,
                        "time_since_access": time_since_access
                    }
                    
                    dormant_crystals.append((crystal, dormancy_data))
                    
                    # Update dormant crystals registry
                    self.dormant_crystals[crystal_id] = dormancy_data
        
        # Sort by recovery value
        dormant_crystals.sort(key=lambda x: x[1]["recovery_value"], reverse=True)
        
        return [data for _, data in dormant_crystals]
    
    def recover_dormant_crystal(self, crystal_id: str) -> Optional[Dict[str, Any]]:
        """
        Recover a dormant crystal.
        
        Args:
            crystal_id: Crystal ID
            
        Returns:
            Recovery event data if successful, None otherwise
        """
        # Get the crystal
        crystal = self.memory_crystallizer.crystals.get(crystal_id)
        if not crystal:
            logger.warning(f"Crystal {crystal_id} not found")
            return None
        
        # Check if crystal is dormant
        dormancy_data = self.dormant_crystals.get(crystal_id)
        if not dormancy_data:
            logger.warning(f"Crystal {crystal_id} is not dormant")
            return None
        
        # Boost crystal size and stability
        original_size = crystal["size"]
        original_stability = crystal["stability"]
        
        crystal["size"] = min(1.0, crystal["size"] + self.config["recovery_boost"])
        crystal["stability"] = min(1.0, crystal["stability"] + self.config["recovery_boost"] * 0.5)
        
        # Update access time
        crystal["last_accessed"] = time.time()
        crystal["access_count"] += 1
        
        # Remove from dormant crystals
        if crystal_id in self.dormant_crystals:
            del self.dormant_crystals[crystal_id]
        
        # Record recovery event
        recovery_event = {
            "crystal_id": crystal_id,
            "domains": crystal["domains"],
            "dormancy_level": dormancy_data["dormancy_level"],
            "recovery_value": dormancy_data["recovery_value"],
            "size_before": original_size,
            "size_after": crystal["size"],
            "stability_before": original_stability,
            "stability_after": crystal["stability"],
            "timestamp": time.time()
        }
        
        self.recovery_history.append(recovery_event)
        
        logger.info(f"Recovered dormant crystal {crystal_id} with recovery value {dormancy_data['recovery_value']:.2f}")
        
        return recovery_event
    
    def identify_forgotten_patterns(self) -> List[Dict[str, Any]]:
        """
        Identify forgotten knowledge patterns.
        
        Returns:
            List of forgotten pattern data
        """
        # This is a simplified implementation
        # In a real system, this would involve sophisticated pattern analysis
        
        forgotten_patterns = []
        
        # Get all domains
        all_domains = set()
        for crystal in self.memory_crystallizer.crystals.values():
            all_domains.update(crystal["domains"])
        
        # Check each domain for forgotten patterns
        for domain in all_domains:
            # Get domain entities
            domain_entities = self.knowledge_tracker.get_domain_entities(domain)
            
            # Skip domains with few entities
            if len(domain_entities) < 3:
                continue
            
            # Get domain crystals
            domain_crystals = self.memory_crystallizer.get_domain_crystals(domain)
            
            # Skip domains with many crystals
            if len(domain_crystals) >= 5:
                continue
            
            # Check if domain has high knowledge but few crystals
            total_knowledge = sum(domain_entities.values())
            avg_knowledge = total_knowledge / len(domain_entities) if domain_entities else 0
            
            if avg_knowledge > 0.7 and len(domain_crystals) < 3:
                # This domain likely has forgotten patterns
                pattern = {
                    "domain": domain,
                    "avg_knowledge": avg_knowledge,
                    "entity_count": len(domain_entities),
                    "crystal_count": len(domain_crystals),
                    "recovery_potential": avg_knowledge * (1.0 - len(domain_crystals) / 5),
                    "identified_at": time.time()
                }
                
                forgotten_patterns.append(pattern)
        
        # Sort by recovery potential
        forgotten_patterns.sort(key=lambda x: x["recovery_potential"], reverse=True)
        
        # Update forgotten patterns registry
        self.forgotten_patterns = forgotten_patterns
        
        return forgotten_patterns
    
    def recover_forgotten_pattern(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Recover a forgotten pattern in a domain.
        
        Args:
            domain: Knowledge domain
            
        Returns:
            Recovery event data if successful, None otherwise
        """
        # Find the pattern
        pattern = None
        for p in self.forgotten_patterns:
            if p["domain"] == domain:
                pattern = p
                break
        
        if not pattern:
            logger.warning(f"No forgotten pattern found for domain {domain}")
            return None
        
        # Get domain entities
        domain_entities = self.knowledge_tracker.get_domain_entities(domain)
        
        # Get top entities in the domain
        top_entities = sorted(domain_entities.items(), key=lambda x: x[1], reverse=True)[:3]
        
        if not top_entities:
            logger.warning(f"No entities found for domain {domain}")
            return None
        
        # Create a synthetic interaction pattern
        entity_ids = [entity_id for entity_id, _ in top_entities]
        
        # Create synthetic interactions
        interactions = []
        for i in range(5):  # Simulate 5 interactions
            interaction = {
                "entity_id1": entity_ids[0],
                "entity_id2": entity_ids[1] if len(entity_ids) > 1 else entity_ids[0],
                "type": "knowledge_sharing",
                "domains": [domain],
                "content": f"Recovered pattern in {domain}",
                "timestamp": time.time() - (86400 * i)  # Spread over past days
            }
            interactions.append(interaction)
        
        # Extract pattern
        pattern_data = self._extract_pattern_from_interactions(interactions, domain)
        
        # Create a new crystal from the pattern
        crystal_id = self._create_crystal_from_pattern(pattern_data, entity_ids)
        
        if not crystal_id:
            logger.warning(f"Failed to create crystal from pattern in domain {domain}")
            return None
        
        # Record recovery event
        recovery_event = {
            "pattern_domain": domain,
            "recovery_potential": pattern["recovery_potential"],
            "entity_count": len(entity_ids),
            "crystal_id": crystal_id,
            "timestamp": time.time()
        }
        
        self.recovery_history.append(recovery_event)
        
        logger.info(f"Recovered forgotten pattern in domain {domain} with potential {pattern['recovery_potential']:.2f}")
        
        return recovery_event
    
    def _extract_pattern_from_interactions(
        self,
        interactions: List[Dict[str, Any]],
        domain: str
    ) -> Dict[str, Any]:
        """
        Extract a pattern from interactions.
        
        Args:
            interactions: List of interactions
            domain: Knowledge domain
            
        Returns:
            Pattern data
        """
        # In a real implementation, this would involve sophisticated pattern analysis
        # Here we'll create a simplified pattern
        
        # Get unique entities
        entities = set()
        for interaction in interactions:
            entities.add(interaction["entity_id1"])
            entities.add(interaction["entity_id2"])
        
        # Calculate pattern quality based on entity knowledge
        quality = 0.0
        for entity_id in entities:
            knowledge_level = self.knowledge_tracker.get_entity_knowledge(entity_id, domain)
            quality += knowledge_level
        
        quality /= len(entities) if entities else 1.0
        
        # Create pattern
        pattern = {
            "domain": domain,
            "entities": list(entities),
            "quality": quality,
            "novelty": random.uniform(0.6, 0.9),  # Simplified novelty calculation
            "extracted_at": time.time()
        }
        
        return pattern
    
    def _create_crystal_from_pattern(
        self,
        pattern: Dict[str, Any],
        entity_ids: List[str]
    ) -> Optional[str]:
        """
        Create a new crystal from a recovered pattern.
        
        Args:
            pattern: Pattern data
            entity_ids: List of contributing entity IDs
            
        Returns:
            Crystal ID if successful, None otherwise
        """
        # Check pattern quality and novelty
        if pattern["quality"] < self.config["recovery_threshold"] or pattern["novelty"] < self.config["novelty_threshold"]:
            return None
        
        # Create crystal directly in the crystallizer's registry
        crystal_id = str(uuid.uuid4())
        
        crystal = {
            "id": crystal_id,
            "type": "recovered",
            "domains": [pattern["domain"]],
            "contributors": entity_ids,
            "size": pattern["quality"] * 0.8,
            "stability": pattern["quality"] * 0.7,
            "created_at": time.time(),
            "last_accessed": time.time(),
            "access_count": 1,
            "inherited_by": [],
            "recovery_source": "forgotten_pattern"
        }
        
        # Add to registry
        self.memory_crystallizer.crystals[crystal_id] = crystal
        
        # Initialize access tracking
        self.memory_crystallizer.crystal_access[crystal_id] = {}
        
        return crystal_id
    
    def find_cross_domain_connections(self) -> List[Dict[str, Any]]:
        """
        Find connections between knowledge in different domains.
        
        Returns:
            List of cross-domain connections
        """
        connections = []
        
        # Get all crystals
        all_crystals = list(self.memory_crystallizer.crystals.values())
        
        # Check each pair of crystals from different domains
        for i, crystal1 in enumerate(all_crystals):
            for crystal2 in all_crystals[i+1:]:
                # Check if crystals are from different domains
                domains1 = set(crystal1["domains"])
                domains2 = set(crystal2["domains"])
                
                # Skip if domains overlap
                if domains1 & domains2:
                    continue
                
                # Calculate similarity based on contributors
                contributors1 = set(crystal1["contributors"])
                contributors2 = set(crystal2["contributors"])
                
                contributor_overlap = len(contributors1 & contributors2)
                contributor_similarity = contributor_overlap / max(1, len(contributors1) + len(contributors2) - contributor_overlap)
                
                # Skip if similarity is too low
                if contributor_similarity < self.config["connection_threshold"]:
                    continue
                
                # Calculate connection strength
                connection_strength = contributor_similarity * 0.7 + (crystal1["size"] + crystal2["size"]) / 2 * 0.3
                
                # Create connection
                connection = {
                    "crystal1_id": crystal1["id"],
                    "crystal2_id": crystal2["id"],
                    "domains1": crystal1["domains"],
                    "domains2": crystal2["domains"],
                    "contributor_similarity": contributor_similarity,
                    "connection_strength": connection_strength,
                    "identified_at": time.time()
                }
                
                connections.append(connection)
        
        # Sort by connection strength
        connections.sort(key=lambda x: x["connection_strength"], reverse=True)
        
        return connections
    
    def create_bridge_crystal(self, crystal_id1: str, crystal_id2: str) -> Optional[str]:
        """
        Create a bridge crystal connecting knowledge from different domains.
        
        Args:
            crystal_id1: First crystal ID
            crystal_id2: Second crystal ID
            
        Returns:
            Bridge crystal ID if successful, None otherwise
        """
        # Get the crystals
        crystal1 = self.memory_crystallizer.crystals.get(crystal_id1)
        crystal2 = self.memory_crystallizer.crystals.get(crystal_id2)
        
        if not crystal1 or not crystal2:
            logger.warning(f"One or both crystals not found: {crystal_id1}, {crystal_id2}")
            return None
        
        # Check if domains are different
        domains1 = set(crystal1["domains"])
        domains2 = set(crystal2["domains"])
        
        if domains1 & domains2:
            logger.warning(f"Crystals share domains: {domains1 & domains2}")
            return None
        
        # Calculate contributor similarity
        contributors1 = set(crystal1["contributors"])
        contributors2 = set(crystal2["contributors"])
        
        contributor_overlap = len(contributors1 & contributors2)
        contributor_similarity = contributor_overlap / max(1, len(contributors1) + len(contributors2) - contributor_overlap)
        
        if contributor_similarity < self.config["connection_threshold"]:
            logger.warning(f"Contributor similarity too low: {contributor_similarity:.2f}")
            return None
        
        # Create bridge crystal
        crystal_id = str(uuid.uuid4())
        
        # Combine domains and contributors
        combined_domains = list(domains1 | domains2)
        combined_contributors = list(contributors1 | contributors2)
        
        # Calculate bridge quality
        bridge_quality = contributor_similarity * 0.6 + (crystal1["stability"] + crystal2["stability"]) / 2 * 0.4
        
        crystal = {
            "id": crystal_id,
            "type": "bridge",
            "domains": combined_domains,
            "contributors": combined_contributors,
            "size": (crystal1["size"] + crystal2["size"]) / 2 * 0.8,  # Slightly smaller than average
            "stability": bridge_quality * 0.9,  # Slightly less stable
            "created_at": time.time(),
            "last_accessed": time.time(),
            "access_count": 1,
            "inherited_by": [],
            "bridge_source": [crystal_id1, crystal_id2],
            "connection_strength": contributor_similarity
        }
        
        # Add to registry
        self.memory_crystallizer.crystals[crystal_id] = crystal
        
        # Initialize access tracking
        self.memory_crystallizer.crystal_access[crystal_id] = {}
        
        # Record recovery event
        recovery_event = {
            "type": "bridge_creation",
            "crystal_id": crystal_id,
            "source_crystals": [crystal_id1, crystal_id2],
            "domains": combined_domains,
            "connection_strength": contributor_similarity,
            "timestamp": time.time()
        }
        
        self.recovery_history.append(recovery_event)
        
        logger.info(f"Created bridge crystal {crystal_id} connecting domains {domains1} and {domains2}")
        
        return crystal_id
    
    def run_recovery_cycle(self) -> Dict[str, Any]:
        """
        Run a complete recovery cycle.
        
        This includes:
        - Identifying dormant crystals
        - Recovering high-value dormant crystals
        - Identifying forgotten patterns
        - Recovering high-potential patterns
        - Finding cross-domain connections
        - Creating bridge crystals
        
        Returns:
            Summary of recovery actions
        """
        recovery_summary = {
            "dormant_identified": 0,
            "dormant_recovered": 0,
            "patterns_identified": 0,
            "patterns_recovered": 0,
            "connections_identified": 0,
            "bridges_created": 0,
            "timestamp": time.time()
        }
        
        # Identify dormant crystals
        dormant_crystals = self.identify_dormant_crystals()
        recovery_summary["dormant_identified"] = len(dormant_crystals)
        
        # Recover high-value dormant crystals
        recovered_count = 0
        for dormancy_data in sorted(dormant_crystals, key=lambda x: x["recovery_value"], reverse=True):
            if recovered_count >= self.config["max_recoveries_per_run"]:
                break
                
            if self.recover_dormant_crystal(dormancy_data["crystal_id"]):
                recovered_count += 1
        
        recovery_summary["dormant_recovered"] = recovered_count
        
        # Identify forgotten patterns
        forgotten_patterns = self.identify_forgotten_patterns()
        recovery_summary["patterns_identified"] = len(forgotten_patterns)
        
        # Recover high-potential patterns
        recovered_count = 0
        for pattern in sorted(forgotten_patterns, key=lambda x: x["recovery_potential"], reverse=True):
            if recovered_count >= self.config["max_recoveries_per_run"]:
                break
                
            if self.recover_forgotten_pattern(pattern["domain"]):
                recovered_count += 1
        
        recovery_summary["patterns_recovered"] = recovered_count
        
        # Find cross-domain connections
        connections = self.find_cross_domain_connections()
        recovery_summary["connections_identified"] = len(connections)
        
        # Create bridge crystals
        bridge_count = 0
        for connection in connections[:self.config["max_recoveries_per_run"]]:
            if self.create_bridge_crystal(connection["crystal1_id"], connection["crystal2_id"]):
                bridge_count += 1
        
        recovery_summary["bridges_created"] = bridge_count
        
        logger.info(f"Completed recovery cycle: {recovery_summary}")
        
        return recovery_summary
