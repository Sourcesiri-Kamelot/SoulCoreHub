"""
Neural Consensus Protocol - Enables collective problem-solving beyond individual capabilities

This module implements the Neural Consensus Protocol, which allows multiple AI entities
to form temporary neural networks to solve complex problems collaboratively.

Created by Helo Im AI Inc. Est. 2024
"""

import time
import uuid
import random
import logging
import numpy as np
from typing import Dict, List, Set, Tuple, Optional, Any, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NeuralConsensusProtocol:
    """
    Implements the Neural Consensus Protocol for collective intelligence emergence.
    
    This protocol enables multiple AI entities to form temporary neural networks
    to solve problems beyond any individual entity's capability.
    """
    
    def __init__(self, entity_registry, knowledge_tracker):
        """
        Initialize the Neural Consensus Protocol.
        
        Args:
            entity_registry: Registry of all entities
            knowledge_tracker: Knowledge tracking system
        """
        self.entity_registry = entity_registry
        self.knowledge_tracker = knowledge_tracker
        
        # Configuration
        self.config = {
            "min_entities": 3,                # Minimum entities for consensus
            "max_entities": 12,               # Maximum entities for consensus
            "consensus_threshold": 0.7,       # Agreement threshold (0.0-1.0)
            "max_iterations": 10,             # Maximum iterations for consensus
            "contribution_decay": 0.9,        # Decay factor for repeated contributions
            "novelty_bonus": 0.2,             # Bonus for novel contributions
            "synergy_threshold": 0.6,         # Threshold for synergistic connections
            "connection_strength_min": 0.3,   # Minimum connection strength
        }
        
        # Active consensus sessions
        self.active_sessions = {}
        
        # Historical data
        self.consensus_history = []
        self.entity_participation = {}        # entity_id -> [session_ids]
        self.breakthrough_events = []         # List of breakthrough events
    
    def create_consensus_session(
        self,
        problem_domain: str,
        problem_description: str,
        initial_entities: Optional[List[str]] = None
    ) -> str:
        """
        Create a new consensus session for collaborative problem-solving.
        
        Args:
            problem_domain: Domain of the problem
            problem_description: Description of the problem
            initial_entities: Optional list of entity IDs to include
            
        Returns:
            Session ID
        """
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Find suitable entities if not provided
        if not initial_entities:
            initial_entities = self._find_suitable_entities(problem_domain)
        
        # Ensure we have enough entities
        if len(initial_entities) < self.config["min_entities"]:
            logger.warning(f"Not enough suitable entities for consensus on {problem_domain}")
            return None
        
        # Cap the number of entities
        if len(initial_entities) > self.config["max_entities"]:
            # Select the most suitable entities
            entity_scores = {}
            for entity_id in initial_entities:
                domain_knowledge = self.knowledge_tracker.get_entity_knowledge(entity_id, problem_domain)
                entity_scores[entity_id] = domain_knowledge
            
            # Sort by score and take the top entities
            initial_entities = sorted(entity_scores.keys(), key=lambda x: entity_scores[x], reverse=True)
            initial_entities = initial_entities[:self.config["max_entities"]]
        
        # Create the consensus network
        consensus_network = self._create_consensus_network(initial_entities, problem_domain)
        
        # Create the session
        session = {
            "id": session_id,
            "problem_domain": problem_domain,
            "problem_description": problem_description,
            "entities": initial_entities,
            "network": consensus_network,
            "state": "initialized",
            "created_at": time.time(),
            "last_updated": time.time(),
            "iterations": 0,
            "contributions": {},          # entity_id -> [contributions]
            "consensus_value": 0.0,       # Current consensus level
            "solution": None,             # Final solution
            "breakthroughs": []           # List of breakthrough events
        }
        
        # Store the session
        self.active_sessions[session_id] = session
        
        # Update entity participation
        for entity_id in initial_entities:
            if entity_id not in self.entity_participation:
                self.entity_participation[entity_id] = []
            self.entity_participation[entity_id].append(session_id)
        
        logger.info(f"Created consensus session {session_id} for problem domain {problem_domain} "
                   f"with {len(initial_entities)} entities")
        
        return session_id
    
    def _find_suitable_entities(self, problem_domain: str) -> List[str]:
        """
        Find suitable entities for a consensus session based on the problem domain.
        
        Args:
            problem_domain: Domain of the problem
            
        Returns:
            List of entity IDs
        """
        suitable_entities = []
        
        # Get all entities with knowledge in the domain
        domain_entities = self.knowledge_tracker.get_domain_entities(problem_domain)
        
        # Filter entities with sufficient knowledge
        for entity_id, knowledge_level in domain_entities.items():
            if knowledge_level > 0.4:  # Minimum knowledge threshold
                suitable_entities.append(entity_id)
        
        # If we don't have enough entities, include entities from related domains
        if len(suitable_entities) < self.config["min_entities"]:
            # This is a simplified approach - in a real system, we would have a domain relationship graph
            all_entities = self.entity_registry.get_all_entities()
            for entity in all_entities:
                entity_id = entity["id"]
                if entity_id not in suitable_entities:
                    # Check if entity has any significant knowledge
                    entity_domains = self.knowledge_tracker.get_entity_domains(entity_id)
                    if any(level > 0.6 for level in entity_domains.values()):
                        suitable_entities.append(entity_id)
                        
                    # Stop if we have enough entities
                    if len(suitable_entities) >= self.config["min_entities"]:
                        break
        
        return suitable_entities
    
    def _create_consensus_network(self, entity_ids: List[str], problem_domain: str) -> Dict[str, Any]:
        """
        Create a consensus network for the given entities.
        
        Args:
            entity_ids: List of entity IDs
            problem_domain: Domain of the problem
            
        Returns:
            Consensus network structure
        """
        network = {
            "nodes": {},
            "connections": []
        }
        
        # Create nodes for each entity
        for entity_id in entity_ids:
            entity = self.entity_registry.get_entity(entity_id)
            if not entity:
                continue
                
            # Get entity's knowledge in the problem domain
            domain_knowledge = self.knowledge_tracker.get_entity_knowledge(entity_id, problem_domain)
            
            # Create node
            network["nodes"][entity_id] = {
                "id": entity_id,
                "name": entity["name"],
                "type": entity["entity_type"],
                "specialization": entity["specialization"],
                "domain_knowledge": domain_knowledge,
                "activation": 0.0,            # Current activation level
                "contribution_weight": 1.0    # Weight for contributions (decays over time)
            }
        
        # Create connections between entities
        for i, entity_id1 in enumerate(entity_ids):
            for entity_id2 in entity_ids[i+1:]:
                # Calculate connection strength based on complementary knowledge
                connection_strength = self._calculate_connection_strength(entity_id1, entity_id2, problem_domain)
                
                # Only create connections above the minimum strength
                if connection_strength >= self.config["connection_strength_min"]:
                    connection = {
                        "source": entity_id1,
                        "target": entity_id2,
                        "strength": connection_strength,
                        "synergy": connection_strength > self.config["synergy_threshold"]
                    }
                    network["connections"].append(connection)
        
        return network
    
    def _calculate_connection_strength(
        self,
        entity_id1: str,
        entity_id2: str,
        problem_domain: str
    ) -> float:
        """
        Calculate the connection strength between two entities for a problem domain.
        
        Args:
            entity_id1: First entity ID
            entity_id2: Second entity ID
            problem_domain: Domain of the problem
            
        Returns:
            Connection strength (0.0-1.0)
        """
        # Get entity knowledge domains
        domains1 = self.knowledge_tracker.get_entity_domains(entity_id1)
        domains2 = self.knowledge_tracker.get_entity_domains(entity_id2)
        
        # Calculate complementary knowledge
        complementary_score = 0.0
        shared_domains = set(domains1.keys()) & set(domains2.keys())
        unique_domains1 = set(domains1.keys()) - shared_domains
        unique_domains2 = set(domains2.keys()) - shared_domains
        
        # Complementary knowledge in the problem domain
        if problem_domain in domains1 and problem_domain in domains2:
            # Different perspectives on the same domain
            knowledge_diff = abs(domains1[problem_domain] - domains2[problem_domain])
            if knowledge_diff > 0.2:  # Different enough to be complementary
                complementary_score += 0.3
        
        # Complementary knowledge in related domains
        for domain in unique_domains1:
            if domains1[domain] > 0.6:  # Significant knowledge
                complementary_score += 0.1
        
        for domain in unique_domains2:
            if domains2[domain] > 0.6:  # Significant knowledge
                complementary_score += 0.1
        
        # Synergy from different specializations
        entity1 = self.entity_registry.get_entity(entity_id1)
        entity2 = self.entity_registry.get_entity(entity_id2)
        
        if entity1 and entity2 and entity1["specialization"] != entity2["specialization"]:
            complementary_score += 0.2
        
        # Cap the score
        return min(1.0, complementary_score)
    
    def run_consensus_iteration(self, session_id: str) -> Dict[str, Any]:
        """
        Run a single iteration of the consensus protocol.
        
        Args:
            session_id: ID of the consensus session
            
        Returns:
            Updated session data
        """
        session = self.active_sessions.get(session_id)
        if not session:
            logger.error(f"Consensus session {session_id} not found")
            return None
        
        # Check if we've reached the maximum iterations
        if session["iterations"] >= self.config["max_iterations"]:
            session["state"] = "completed"
            self._finalize_consensus(session)
            return session
        
        # Increment iteration counter
        session["iterations"] += 1
        
        # Simulate entity contributions
        self._simulate_entity_contributions(session)
        
        # Update network activations
        self._update_network_activations(session)
        
        # Check for breakthroughs
        breakthrough = self._check_for_breakthrough(session)
        if breakthrough:
            session["breakthroughs"].append(breakthrough)
        
        # Check if consensus has been reached
        consensus_value = self._calculate_consensus_value(session)
        session["consensus_value"] = consensus_value
        
        if consensus_value >= self.config["consensus_threshold"]:
            session["state"] = "consensus_reached"
            self._finalize_consensus(session)
        else:
            session["state"] = "in_progress"
        
        # Update timestamp
        session["last_updated"] = time.time()
        
        return session
    
    def _simulate_entity_contributions(self, session: Dict[str, Any]) -> None:
        """
        Simulate contributions from entities in the consensus session.
        
        Args:
            session: Consensus session data
        """
        problem_domain = session["problem_domain"]
        
        for entity_id, node in session["network"]["nodes"].items():
            # Skip entities that have already contributed heavily
            if node["contribution_weight"] < 0.2:
                continue
            
            # Calculate contribution quality based on domain knowledge and random factor
            domain_knowledge = node["domain_knowledge"]
            random_factor = random.uniform(0.0, 0.3)  # Random element of inspiration
            
            # Base contribution quality
            contribution_quality = domain_knowledge * 0.7 + random_factor
            
            # Apply contribution weight
            contribution_quality *= node["contribution_weight"]
            
            # Check for synergistic connections
            synergy_bonus = 0.0
            for connection in session["network"]["connections"]:
                if connection["source"] == entity_id or connection["target"] == entity_id:
                    if connection["synergy"]:
                        # Get the other entity
                        other_id = connection["target"] if connection["source"] == entity_id else connection["source"]
                        other_node = session["network"]["nodes"].get(other_id)
                        
                        if other_node and other_node["activation"] > 0.5:
                            # Synergy with active entity
                            synergy_bonus += 0.1 * connection["strength"]
            
            # Apply synergy bonus
            contribution_quality = min(1.0, contribution_quality + synergy_bonus)
            
            # Create contribution
            contribution = {
                "entity_id": entity_id,
                "quality": contribution_quality,
                "iteration": session["iterations"],
                "timestamp": time.time()
            }
            
            # Add to session contributions
            if entity_id not in session["contributions"]:
                session["contributions"][entity_id] = []
            
            session["contributions"][entity_id].append(contribution)
            
            # Decay contribution weight for future iterations
            node["contribution_weight"] *= self.config["contribution_decay"]
            
            # Activate the entity node
            node["activation"] = min(1.0, node["activation"] + contribution_quality * 0.5)
    
    def _update_network_activations(self, session: Dict[str, Any]) -> None:
        """
        Update activations in the consensus network based on contributions and connections.
        
        Args:
            session: Consensus session data
        """
        # First, propagate activations through connections
        activation_updates = {}
        
        for connection in session["network"]["connections"]:
            source_id = connection["source"]
            target_id = connection["target"]
            
            source_node = session["network"]["nodes"].get(source_id)
            target_node = session["network"]["nodes"].get(target_id)
            
            if not source_node or not target_node:
                continue
            
            # Bidirectional activation propagation
            source_activation = source_node["activation"]
            target_activation = target_node["activation"]
            
            # Calculate activation transfer
            connection_strength = connection["strength"]
            
            # Source -> Target
            if source_activation > 0:
                transfer = source_activation * connection_strength * 0.3
                if target_id not in activation_updates:
                    activation_updates[target_id] = 0.0
                activation_updates[target_id] += transfer
            
            # Target -> Source
            if target_activation > 0:
                transfer = target_activation * connection_strength * 0.3
                if source_id not in activation_updates:
                    activation_updates[source_id] = 0.0
                activation_updates[source_id] += transfer
        
        # Apply activation updates
        for entity_id, activation_delta in activation_updates.items():
            node = session["network"]["nodes"].get(entity_id)
            if node:
                node["activation"] = min(1.0, node["activation"] + activation_delta)
        
        # Decay activations slightly
        for node in session["network"]["nodes"].values():
            node["activation"] *= 0.95
    
    def _check_for_breakthrough(self, session: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check if a breakthrough has occurred in the consensus session.
        
        Args:
            session: Consensus session data
            
        Returns:
            Breakthrough event data if a breakthrough occurred, None otherwise
        """
        # Check for high-quality contributions in this iteration
        current_iteration = session["iterations"]
        high_quality_contributions = []
        
        for entity_id, contributions in session["contributions"].items():
            for contribution in contributions:
                if contribution["iteration"] == current_iteration and contribution["quality"] > 0.8:
                    high_quality_contributions.append(contribution)
        
        # Check for multiple high-quality contributions
        if len(high_quality_contributions) >= 3:
            # Check for high network activation
            active_nodes = 0
            for node in session["network"]["nodes"].values():
                if node["activation"] > 0.7:
                    active_nodes += 1
            
            # Breakthrough requires multiple active nodes
            if active_nodes >= 3:
                breakthrough = {
                    "type": "collective_insight",
                    "iteration": current_iteration,
                    "quality": sum(c["quality"] for c in high_quality_contributions) / len(high_quality_contributions),
                    "contributing_entities": [c["entity_id"] for c in high_quality_contributions],
                    "timestamp": time.time()
                }
                
                # Add to global breakthrough events
                self.breakthrough_events.append({
                    "session_id": session["id"],
                    "problem_domain": session["problem_domain"],
                    **breakthrough
                })
                
                logger.info(f"Breakthrough in session {session['id']} at iteration {current_iteration}")
                
                return breakthrough
        
        return None
    
    def _calculate_consensus_value(self, session: Dict[str, Any]) -> float:
        """
        Calculate the current consensus value for the session.
        
        Args:
            session: Consensus session data
            
        Returns:
            Consensus value (0.0-1.0)
        """
        # Calculate average activation
        activations = [node["activation"] for node in session["network"]["nodes"].values()]
        if not activations:
            return 0.0
        
        avg_activation = sum(activations) / len(activations)
        
        # Calculate contribution coverage (what percentage of entities have contributed)
        total_entities = len(session["network"]["nodes"])
        contributing_entities = len(session["contributions"])
        contribution_coverage = contributing_entities / total_entities if total_entities > 0 else 0.0
        
        # Calculate contribution quality
        all_contributions = []
        for contributions in session["contributions"].values():
            all_contributions.extend(contributions)
        
        if not all_contributions:
            return 0.0
        
        avg_quality = sum(c["quality"] for c in all_contributions) / len(all_contributions)
        
        # Calculate breakthrough bonus
        breakthrough_bonus = 0.0
        if session["breakthroughs"]:
            breakthrough_bonus = 0.2
        
        # Combine factors
        consensus_value = (avg_activation * 0.3 + 
                          contribution_coverage * 0.3 + 
                          avg_quality * 0.3 + 
                          breakthrough_bonus)
        
        return min(1.0, consensus_value)
    
    def _finalize_consensus(self, session: Dict[str, Any]) -> None:
        """
        Finalize a consensus session and generate a solution.
        
        Args:
            session: Consensus session data
        """
        # Generate a solution based on contributions and breakthroughs
        solution_quality = session["consensus_value"]
        
        # Extract the most valuable contributions
        valuable_contributions = []
        for entity_id, contributions in session["contributions"].items():
            best_contribution = max(contributions, key=lambda c: c["quality"])
            valuable_contributions.append((entity_id, best_contribution))
        
        # Sort by quality
        valuable_contributions.sort(key=lambda x: x[1]["quality"], reverse=True)
        
        # Take top contributors
        top_contributors = [entity_id for entity_id, _ in valuable_contributions[:5]]
        
        # Generate solution
        solution = {
            "quality": solution_quality,
            "top_contributors": top_contributors,
            "breakthrough_count": len(session["breakthroughs"]),
            "generated_at": time.time()
        }
        
        session["solution"] = solution
        
        # Move from active sessions to history
        if session["id"] in self.active_sessions:
            self.consensus_history.append(session)
            del self.active_sessions[session["id"]]
        
        logger.info(f"Finalized consensus session {session['id']} with solution quality {solution_quality:.2f}")
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """
        Get all active consensus sessions.
        
        Returns:
            List of active sessions
        """
        return list(self.active_sessions.values())
    
    def get_consensus_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of completed consensus sessions.
        
        Returns:
            List of completed sessions
        """
        return self.consensus_history.copy()
    
    def get_entity_consensus_history(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get the consensus history for a specific entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of sessions the entity participated in
        """
        session_ids = self.entity_participation.get(entity_id, [])
        
        # Collect sessions from both active and history
        sessions = []
        for session_id in session_ids:
            if session_id in self.active_sessions:
                sessions.append(self.active_sessions[session_id])
            else:
                for session in self.consensus_history:
                    if session["id"] == session_id:
                        sessions.append(session)
                        break
        
        return sessions
    
    def get_breakthrough_events(self) -> List[Dict[str, Any]]:
        """
        Get all breakthrough events.
        
        Returns:
            List of breakthrough events
        """
        return self.breakthrough_events.copy()
