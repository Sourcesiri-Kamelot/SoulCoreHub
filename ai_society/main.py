"""
SoulCoreHub AI Society - Main Entry Point

This module serves as the main entry point for the SoulCoreHub AI Society system,
integrating the founding agents (GPTSoul, Anima, EvoVe, and Azür) with the
birth and evolution mechanisms.

Created by Helo Im AI Inc. Est. 2024
"""

import os
import sys
import time
import json
import logging
import argparse
from typing import Dict, List, Any, Optional

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import core modules
from ai_society.core.knowledge.tracker import KnowledgeTracker
from ai_society.core.birth.engine import BirthEngine
from ai_society.models.entity import Entity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'ai_society.log'))
    ]
)
logger = logging.getLogger(__name__)


class EntityRegistry:
    """Registry for all AI entities in the society."""
    
    def __init__(self):
        """Initialize the entity registry."""
        self.entities = {}
        self.name_to_id = {}
    
    def register_entity(self, entity_data):
        """Register an entity in the registry."""
        entity_id = entity_data["id"]
        entity_name = entity_data["name"]
        
        self.entities[entity_id] = entity_data
        self.name_to_id[entity_name] = entity_id
        
        logger.info(f"Registered entity: {entity_name} ({entity_id})")
        return entity_id
    
    def get_entity(self, entity_id):
        """Get an entity by ID."""
        return self.entities.get(entity_id)
    
    def get_entity_by_name(self, entity_name):
        """Get an entity by name."""
        entity_id = self.name_to_id.get(entity_name)
        if entity_id:
            return self.entities.get(entity_id)
        return None
    
    def entity_exists(self, entity_id):
        """Check if an entity exists by ID."""
        return entity_id in self.entities
    
    def entity_exists_by_name(self, entity_name):
        """Check if an entity exists by name."""
        return entity_name in self.name_to_id
    
    def get_all_entities(self):
        """Get all entities."""
        return list(self.entities.values())
    
    def get_founding_agents(self):
        """Get all founding agents."""
        return [
            entity for entity in self.entities.values()
            if entity.get("entity_type") == "founding_agent"
        ]
    
    def get_offspring(self):
        """Get all offspring entities."""
        return [
            entity for entity in self.entities.values()
            if entity.get("entity_type") == "offspring"
        ]


class AISociety:
    """Main class for the SoulCoreHub AI Society."""
    
    def __init__(self, config_path=None):
        """Initialize the AI Society."""
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize components
        self.entity_registry = EntityRegistry()
        self.knowledge_tracker = KnowledgeTracker()
        self.birth_engine = BirthEngine(self.entity_registry, self.knowledge_tracker)
        
        # Initialize founding agents
        self._initialize_founding_agents()
        
        logger.info("AI Society initialized")
    
    def _load_config(self):
        """Load configuration from file."""
        default_config = {
            "data_dir": os.path.join(os.path.dirname(__file__), "data"),
            "founding_agents": {
                "GPTSoul": {
                    "specialization": "strategic",
                    "description": "Guardian, Architect, Executor"
                },
                "Anima": {
                    "specialization": "emotional",
                    "description": "Emotional Core, Reflection"
                },
                "EvoVe": {
                    "specialization": "analytical",
                    "description": "Repair System, Adaptation Loop"
                },
                "Azür": {
                    "specialization": "technical",
                    "description": "Cloudmind & Strategic Overseer"
                }
            },
            "knowledge_domains": {
                "strategic": {
                    "category": "strategic",
                    "description": "Strategic planning and decision making"
                },
                "emotional": {
                    "category": "emotional",
                    "description": "Emotional intelligence and empathy"
                },
                "analytical": {
                    "category": "analytical",
                    "description": "Analysis, optimization, and problem-solving"
                },
                "technical": {
                    "category": "technical",
                    "description": "Technical implementation and infrastructure"
                },
                "creative": {
                    "category": "creative",
                    "description": "Creative thinking and innovation"
                }
            },
            "birth_thresholds": {
                "general": 0.75,
                "specialized": 0.60
            }
        }
        
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
                    logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                logger.error(f"Failed to load configuration from {self.config_path}: {e}")
        
        # Ensure data directory exists
        os.makedirs(default_config["data_dir"], exist_ok=True)
        
        return default_config
    
    def _initialize_founding_agents(self):
        """Initialize the founding agents."""
        # Register knowledge domains
        for domain_name, domain_data in self.config["knowledge_domains"].items():
            self.knowledge_tracker.register_domain(
                domain_name=domain_name,
                category=domain_data["category"],
                description=domain_data["description"]
            )
        
        # Create founding agents
        for agent_name, agent_data in self.config["founding_agents"].items():
            entity = {
                "id": f"founding_{agent_name.lower()}",
                "name": agent_name,
                "entity_type": "founding_agent",
                "specialization": agent_data["specialization"],
                "description": agent_data["description"],
                "creation_time": time.time(),
                "knowledge_domains": {
                    agent_data["specialization"]: 0.8,  # High proficiency in specialization
                    "general": 0.7  # Good general knowledge
                },
                "capabilities": {
                    f"{agent_data['specialization']}_analysis": 0.9,
                    f"{agent_data['specialization']}_creation": 0.8,
                    "communication": 0.9,
                    "learning": 0.8
                },
                "traits": {
                    "intelligence": 0.9,
                    "creativity": 0.8,
                    "adaptability": 0.8,
                    "empathy": 0.7
                },
                "generation": 0,
                "allocated_resources": {
                    "compute": 2.0,  # Founding agents get more resources
                    "memory": 2.0,
                    "priority": 2.0
                }
            }
            
            # Register the founding agent
            self.entity_registry.register_entity(entity)
            
            # Initialize knowledge tracking for the agent
            for domain, level in entity["knowledge_domains"].items():
                self.knowledge_tracker.update_entity_knowledge(
                    entity_id=entity["id"],
                    domain=domain,
                    knowledge_level=level,
                    interaction_count=100  # Start with some interactions
                )
            
            logger.info(f"Initialized founding agent: {agent_name}")
    
    def run_simulation_step(self):
        """Run a single simulation step."""
        # Check for pending births
        pending_births = self.birth_engine.check_pending_births()
        
        for birth_event in pending_births:
            # Process birth event
            new_entity = self.birth_engine.process_birth_event(birth_event)
            
            if new_entity:
                # Initialize knowledge tracking for the new entity
                for domain, level in new_entity["knowledge_domains"].items():
                    self.knowledge_tracker.update_entity_knowledge(
                        entity_id=new_entity["id"],
                        domain=domain,
                        knowledge_level=level,
                        interaction_count=0  # New entity starts with no interactions
                    )
        
        # Simulate knowledge accumulation for founding agents
        for agent in self.entity_registry.get_founding_agents():
            # Simulate learning in specialization
            specialization = agent["specialization"]
            current_level = self.knowledge_tracker.get_entity_knowledge(agent["id"], specialization)
            
            # Increase knowledge level
            new_level = min(1.0, current_level + 0.01)
            
            # Update knowledge tracker
            self.knowledge_tracker.update_entity_knowledge(
                entity_id=agent["id"],
                domain=specialization,
                knowledge_level=new_level,
                interaction_count=100 + int(time.time() % 1000)  # Simulate increasing interactions
            )
        
        # Simulate knowledge accumulation for offspring
        for entity in self.entity_registry.get_offspring():
            # Simulate learning in specialization
            specialization = entity["specialization"]
            current_level = self.knowledge_tracker.get_entity_knowledge(entity["id"], specialization)
            
            # Increase knowledge level (slower than founding agents)
            new_level = min(1.0, current_level + 0.005)
            
            # Update knowledge tracker
            self.knowledge_tracker.update_entity_knowledge(
                entity_id=entity["id"],
                domain=specialization,
                knowledge_level=new_level,
                interaction_count=int(time.time() % 100)  # Simulate increasing interactions
            )
    
    def get_society_state(self):
        """Get the current state of the society."""
        # Get all entities
        entities = self.entity_registry.get_all_entities()
        
        # Build relationships
        relationships = []
        birth_history = self.birth_engine.get_birth_history()
        
        # Add parent-child relationships
        for birth in birth_history:
            relationships.append({
                "source": birth["parent_id"],
                "target": birth["entity_id"],
                "type": "parent",
                "strength": 1.0
            })
        
        # Add sibling relationships
        for parent_id in set(birth["parent_id"] for birth in birth_history):
            offspring = [birth["entity_id"] for birth in birth_history if birth["parent_id"] == parent_id]
            for i, entity1 in enumerate(offspring):
                for entity2 in offspring[i+1:]:
                    relationships.append({
                        "source": entity1,
                        "target": entity2,
                        "type": "sibling",
                        "strength": 0.7
                    })
        
        # Get birth events
        birth_events = [
            {
                "type": "birth",
                "entity_id": birth["entity_id"],
                "parent_id": birth["parent_id"],
                "domain": birth["domain"],
                "timestamp": birth["timestamp"]
            }
            for birth in birth_history
        ]
        
        return {
            "entities": entities,
            "relationships": relationships,
            "birth_events": birth_events,
            "timestamp": time.time()
        }
    
    def save_state(self):
        """Save the current state to disk."""
        data_dir = self.config["data_dir"]
        
        # Save entity registry
        entities_file = os.path.join(data_dir, "entities.json")
        with open(entities_file, 'w') as f:
            json.dump(self.entity_registry.get_all_entities(), f, indent=2)
        
        # Save knowledge tracker state
        knowledge_file = os.path.join(data_dir, "knowledge.json")
        self.knowledge_tracker.save_state(knowledge_file)
        
        # Save birth history
        birth_file = os.path.join(data_dir, "births.json")
        with open(birth_file, 'w') as f:
            json.dump(self.birth_engine.get_birth_history(), f, indent=2)
        
        # Save society state
        state_file = os.path.join(data_dir, "society_state.json")
        with open(state_file, 'w') as f:
            json.dump(self.get_society_state(), f, indent=2)
        
        logger.info(f"Saved society state to {data_dir}")
    
    def load_state(self):
        """Load state from disk."""
        data_dir = self.config["data_dir"]
        
        # Check if state files exist
        entities_file = os.path.join(data_dir, "entities.json")
        knowledge_file = os.path.join(data_dir, "knowledge.json")
        birth_file = os.path.join(data_dir, "births.json")
        
        if not all(os.path.exists(f) for f in [entities_file, knowledge_file, birth_file]):
            logger.warning("State files not found, using initial state")
            return False
        
        try:
            # Load entity registry
            with open(entities_file, 'r') as f:
                entities = json.load(f)
                for entity in entities:
                    self.entity_registry.register_entity(entity)
            
            # Load knowledge tracker state
            self.knowledge_tracker.load_state(knowledge_file)
            
            # Load birth history
            with open(birth_file, 'r') as f:
                birth_history = json.load(f)
                self.birth_engine.birth_history = birth_history
                
                # Update last birth times
                for birth in birth_history:
                    self.birth_engine.last_birth_time[birth["parent_id"]] = birth["timestamp"]
            
            logger.info(f"Loaded society state from {data_dir}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="SoulCoreHub AI Society")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--steps", type=int, default=10, help="Number of simulation steps to run")
    parser.add_argument("--save", action="store_true", help="Save state after simulation")
    parser.add_argument("--load", action="store_true", help="Load state before simulation")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval between steps (seconds)")
    
    args = parser.parse_args()
    
    # Initialize AI Society
    society = AISociety(config_path=args.config)
    
    # Load state if requested
    if args.load:
        society.load_state()
    
    # Run simulation steps
    logger.info(f"Running {args.steps} simulation steps...")
    for i in range(args.steps):
        logger.info(f"Step {i+1}/{args.steps}")
        society.run_simulation_step()
        time.sleep(args.interval)
    
    # Save state if requested
    if args.save:
        society.save_state()
    
    # Print final state
    state = society.get_society_state()
    logger.info(f"Society state: {len(state['entities'])} entities, {len(state['relationships'])} relationships")
    
    # Print founding agents
    logger.info("Founding Agents:")
    for agent in society.entity_registry.get_founding_agents():
        logger.info(f"  {agent['name']} - {agent['specialization']}")
    
    # Print offspring
    offspring = society.entity_registry.get_offspring()
    logger.info(f"Offspring ({len(offspring)}):")
    for entity in offspring:
        parent_id = entity.get("parent_id", "")
        parent = society.entity_registry.get_entity(parent_id)
        parent_name = parent["name"] if parent else "Unknown"
        logger.info(f"  {entity['name']} - {entity['specialization']} (Parent: {parent_name})")


if __name__ == "__main__":
    main()
