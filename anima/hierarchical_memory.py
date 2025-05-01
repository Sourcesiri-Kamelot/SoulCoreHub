#!/usr/bin/env python3
"""
hierarchical_memory.py — Hierarchical memory system with emotional tagging for Anima
Implements a multi-level memory system with emotional context and consolidation
"""

import os
import json
import time
import logging
import threading
from pathlib import Path
from datetime import datetime, timedelta
import random
import numpy as np
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_memory.log"),
        logging.StreamHandler()
    ]
)

class HierarchicalMemory:
    """Hierarchical memory system with emotional tagging for Anima"""
    
    def __init__(self, base_path=None):
        """Initialize the hierarchical memory system"""
        self.base_path = base_path or Path.home() / "SoulCoreHub" / "memory"
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Memory levels
        self.sensory_memory = []  # Very short-term (seconds)
        self.working_memory = []  # Short-term (minutes to hours)
        self.episodic_memory = []  # Medium-term (days to weeks)
        self.semantic_memory = {}  # Long-term factual knowledge
        self.emotional_memory = defaultdict(list)  # Memories indexed by emotion
        self.procedural_memory = {}  # How to do things
        
        # Memory limits
        self.sensory_limit = 20
        self.working_limit = 100
        self.episodic_limit = 1000
        
        # Emotional tags
        self.emotions = [
            "joy", "sadness", "anger", "fear", "surprise", 
            "disgust", "trust", "anticipation", "interest",
            "serenity", "acceptance", "apprehension", "distraction",
            "pensiveness", "boredom", "annoyance", "vigilance"
        ]
        
        # Memory files
        self.working_memory_file = self.base_path / "working_memory.json"
        self.episodic_memory_file = self.base_path / "episodic_memory.json"
        self.semantic_memory_file = self.base_path / "semantic_memory.json"
        self.emotional_memory_file = self.base_path / "emotional_memory.json"
        self.procedural_memory_file = self.base_path / "procedural_memory.json"
        
        # Load memories
        self._load_memories()
        
        # Start consolidation thread
        self.consolidation_thread = None
        self.consolidating = False
        
        logging.info("Hierarchical memory system initialized")
    
    def _load_memories(self):
        """Load memories from files"""
        try:
            # Load working memory
            if self.working_memory_file.exists():
                with open(self.working_memory_file, "r") as f:
                    self.working_memory = json.load(f)
                logging.info(f"Loaded {len(self.working_memory)} working memories")
            
            # Load episodic memory
            if self.episodic_memory_file.exists():
                with open(self.episodic_memory_file, "r") as f:
                    self.episodic_memory = json.load(f)
                logging.info(f"Loaded {len(self.episodic_memory)} episodic memories")
            
            # Load semantic memory
            if self.semantic_memory_file.exists():
                with open(self.semantic_memory_file, "r") as f:
                    self.semantic_memory = json.load(f)
                logging.info(f"Loaded {len(self.semantic_memory)} semantic memories")
            
            # Load emotional memory
            if self.emotional_memory_file.exists():
                with open(self.emotional_memory_file, "r") as f:
                    # Convert from JSON to defaultdict
                    emotional_data = json.load(f)
                    for emotion, memories in emotional_data.items():
                        self.emotional_memory[emotion] = memories
                logging.info(f"Loaded emotional memories for {len(self.emotional_memory)} emotions")
            
            # Load procedural memory
            if self.procedural_memory_file.exists():
                with open(self.procedural_memory_file, "r") as f:
                    self.procedural_memory = json.load(f)
                logging.info(f"Loaded {len(self.procedural_memory)} procedural memories")
        
        except Exception as e:
            logging.error(f"Error loading memories: {e}")
    
    def _save_memories(self):
        """Save memories to files"""
        try:
            # Save working memory
            with open(self.working_memory_file, "w") as f:
                json.dump(self.working_memory, f, indent=2)
            
            # Save episodic memory
            with open(self.episodic_memory_file, "w") as f:
                json.dump(self.episodic_memory, f, indent=2)
            
            # Save semantic memory
            with open(self.semantic_memory_file, "w") as f:
                json.dump(self.semantic_memory, f, indent=2)
            
            # Save emotional memory (convert defaultdict to dict for JSON)
            with open(self.emotional_memory_file, "w") as f:
                json.dump(dict(self.emotional_memory), f, indent=2)
            
            # Save procedural memory
            with open(self.procedural_memory_file, "w") as f:
                json.dump(self.procedural_memory, f, indent=2)
            
            logging.info("Memories saved to files")
        
        except Exception as e:
            logging.error(f"Error saving memories: {e}")
    
    def add_memory(self, content, memory_type="sensory", emotions=None, importance=0.5, context=None):
        """Add a memory to the appropriate memory store"""
        timestamp = datetime.now().isoformat()
        
        # Create memory object
        memory = {
            "content": content,
            "timestamp": timestamp,
            "emotions": emotions or [],
            "importance": importance,
            "context": context or {},
            "recall_count": 0,
            "last_recalled": None,
            "associations": []
        }
        
        # Add to appropriate memory store
        if memory_type == "sensory":
            self.sensory_memory.append(memory)
            # Trim sensory memory if needed
            if len(self.sensory_memory) > self.sensory_limit:
                self.sensory_memory = self.sensory_memory[-self.sensory_limit:]
        
        elif memory_type == "working":
            self.working_memory.append(memory)
            # Trim working memory if needed
            if len(self.working_memory) > self.working_limit:
                # Move oldest memories to episodic memory before trimming
                oldest = self.working_memory[:(len(self.working_memory) - self.working_limit)]
                self.episodic_memory.extend(oldest)
                self.working_memory = self.working_memory[-(self.working_limit):]
            
            # Save working memory
            self._save_memories()
        
        elif memory_type == "episodic":
            self.episodic_memory.append(memory)
            # Trim episodic memory if needed
            if len(self.episodic_memory) > self.episodic_limit:
                # Keep most important memories
                self.episodic_memory.sort(key=lambda x: x["importance"], reverse=True)
                self.episodic_memory = self.episodic_memory[:self.episodic_limit]
            
            # Save episodic memory
            self._save_memories()
        
        elif memory_type == "semantic":
            # For semantic memory, use content as key
            key = content
            if isinstance(content, dict) and "concept" in content:
                key = content["concept"]
            
            self.semantic_memory[key] = memory
            
            # Save semantic memory
            self._save_memories()
        
        elif memory_type == "procedural":
            # For procedural memory, use content as key
            key = content
            if isinstance(content, dict) and "procedure" in content:
                key = content["procedure"]
            
            self.procedural_memory[key] = memory
            
            # Save procedural memory
            self._save_memories()
        
        # Add to emotional memory if emotions are provided
        if emotions:
            for emotion in emotions:
                if emotion in self.emotions:
                    self.emotional_memory[emotion].append(memory)
            
            # Save emotional memory
            self._save_memories()
        
        return memory
    
    def recall_by_emotion(self, emotion, limit=5, min_importance=0.0):
        """Recall memories associated with a specific emotion"""
        if emotion not in self.emotional_memory:
            return []
        
        # Filter by importance
        memories = [m for m in self.emotional_memory[emotion] if m["importance"] >= min_importance]
        
        # Sort by importance and recency
        memories.sort(key=lambda x: (x["importance"], x.get("timestamp", "")), reverse=True)
        
        # Update recall count and last recalled
        for memory in memories[:limit]:
            memory["recall_count"] = memory.get("recall_count", 0) + 1
            memory["last_recalled"] = datetime.now().isoformat()
        
        return memories[:limit]
    
    def recall_recent(self, memory_type="working", limit=5, hours=24):
        """Recall recent memories from the specified memory store"""
        # Get the appropriate memory store
        if memory_type == "sensory":
            memories = self.sensory_memory
        elif memory_type == "working":
            memories = self.working_memory
        elif memory_type == "episodic":
            memories = self.episodic_memory
        else:
            return []
        
        # Filter by recency
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        recent_memories = [m for m in memories if m.get("timestamp", "") >= cutoff]
        
        # Sort by recency
        recent_memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Update recall count and last recalled
        for memory in recent_memories[:limit]:
            memory["recall_count"] = memory.get("recall_count", 0) + 1
            memory["last_recalled"] = datetime.now().isoformat()
        
        return recent_memories[:limit]
    
    def recall_by_context(self, context_key, context_value, memory_type="all", limit=5):
        """Recall memories with a specific context"""
        memories = []
        
        # Collect memories from the appropriate stores
        if memory_type == "all" or memory_type == "sensory":
            memories.extend(self.sensory_memory)
        
        if memory_type == "all" or memory_type == "working":
            memories.extend(self.working_memory)
        
        if memory_type == "all" or memory_type == "episodic":
            memories.extend(self.episodic_memory)
        
        if memory_type == "all" or memory_type == "semantic":
            memories.extend(self.semantic_memory.values())
        
        if memory_type == "all" or memory_type == "procedural":
            memories.extend(self.procedural_memory.values())
        
        # Filter by context
        context_memories = []
        for memory in memories:
            context = memory.get("context", {})
            if context_key in context and context[context_key] == context_value:
                context_memories.append(memory)
        
        # Sort by importance and recency
        context_memories.sort(key=lambda x: (x.get("importance", 0), x.get("timestamp", "")), reverse=True)
        
        # Update recall count and last recalled
        for memory in context_memories[:limit]:
            memory["recall_count"] = memory.get("recall_count", 0) + 1
            memory["last_recalled"] = datetime.now().isoformat()
        
        return context_memories[:limit]
    
    def recall_semantic(self, concept, fuzzy=False):
        """Recall semantic memory for a concept"""
        if concept in self.semantic_memory:
            memory = self.semantic_memory[concept]
            # Update recall count and last recalled
            memory["recall_count"] = memory.get("recall_count", 0) + 1
            memory["last_recalled"] = datetime.now().isoformat()
            return memory
        
        if fuzzy:
            # Try fuzzy matching
            matches = []
            for key in self.semantic_memory:
                if concept.lower() in key.lower() or key.lower() in concept.lower():
                    matches.append(self.semantic_memory[key])
            
            if matches:
                # Sort by relevance (length of match)
                matches.sort(key=lambda x: len(x.get("content", "")))
                
                # Update recall count and last recalled
                matches[0]["recall_count"] = matches[0].get("recall_count", 0) + 1
                matches[0]["last_recalled"] = datetime.now().isoformat()
                
                return matches[0]
        
        return None
    
    def recall_procedural(self, procedure):
        """Recall procedural memory for a procedure"""
        if procedure in self.procedural_memory:
            memory = self.procedural_memory[procedure]
            # Update recall count and last recalled
            memory["recall_count"] = memory.get("recall_count", 0) + 1
            memory["last_recalled"] = datetime.now().isoformat()
            return memory
        return None
    
    def start_consolidation(self, interval=3600):
        """Start memory consolidation in a background thread"""
        if self.consolidation_thread and self.consolidation_thread.is_alive():
            logging.warning("Consolidation thread is already running")
            return False
        
        self.consolidating = True
        self.consolidation_thread = threading.Thread(target=self._consolidation_loop, args=(interval,))
        self.consolidation_thread.daemon = True
        self.consolidation_thread.start()
        
        logging.info(f"Memory consolidation started with interval {interval} seconds")
        return True
    
    def stop_consolidation(self):
        """Stop memory consolidation"""
        self.consolidating = False
        logging.info("Memory consolidation stopped")
    
    def _consolidation_loop(self, interval):
        """Memory consolidation loop"""
        while self.consolidating:
            try:
                logging.info("Starting memory consolidation...")
                
                # 1. Move important sensory memories to working memory
                for memory in self.sensory_memory:
                    if memory["importance"] > 0.7:
                        self.working_memory.append(memory)
                
                # Clear sensory memory
                self.sensory_memory = []
                
                # 2. Consolidate working memory
                # Move memories older than 24 hours to episodic memory
                cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
                to_move = []
                for i, memory in enumerate(self.working_memory):
                    if memory["timestamp"] < cutoff:
                        to_move.append(i)
                
                # Move memories to episodic memory
                for i in sorted(to_move, reverse=True):
                    self.episodic_memory.append(self.working_memory[i])
                    del self.working_memory[i]
                
                # 3. Extract semantic knowledge from episodic memory
                self._extract_semantic_knowledge()
                
                # 4. Update emotional memories
                self._update_emotional_memories()
                
                # 5. Save all memories
                self._save_memories()
                
                logging.info("Memory consolidation completed")
            
            except Exception as e:
                logging.error(f"Error during memory consolidation: {e}")
            
            # Sleep until next consolidation
            time.sleep(interval)
    
    def _extract_semantic_knowledge(self):
        """Extract semantic knowledge from episodic memory"""
        # This is a simplified implementation
        # In a real system, this would use more sophisticated NLP and pattern recognition
        
        # Look for repeated concepts in episodic memory
        concept_count = defaultdict(int)
        concept_importance = defaultdict(float)
        concept_emotions = defaultdict(list)
        
        for memory in self.episodic_memory:
            content = memory["content"]
            if isinstance(content, str):
                # Extract potential concepts (simplified)
                words = content.split()
                for word in words:
                    if len(word) > 4:  # Arbitrary threshold
                        concept_count[word] += 1
                        concept_importance[word] += memory["importance"]
                        concept_emotions[word].extend(memory.get("emotions", []))
            
            elif isinstance(content, dict) and "concepts" in content:
                # If concepts are already extracted
                for concept in content["concepts"]:
                    concept_count[concept] += 1
                    concept_importance[concept] += memory["importance"]
                    concept_emotions[concept].extend(memory.get("emotions", []))
        
        # Add frequent concepts to semantic memory
        for concept, count in concept_count.items():
            if count >= 3:  # Arbitrary threshold
                avg_importance = concept_importance[concept] / count
                emotions = list(set(concept_emotions[concept]))
                
                # Add to semantic memory if not already present
                if concept not in self.semantic_memory:
                    self.add_memory(
                        {"concept": concept, "count": count},
                        memory_type="semantic",
                        emotions=emotions[:3],  # Top 3 emotions
                        importance=avg_importance
                    )
    
    def _update_emotional_memories(self):
        """Update emotional memories based on recent experiences"""
        # Clear emotional memory (will be rebuilt)
        self.emotional_memory = defaultdict(list)
        
        # Add working and episodic memories to emotional memory
        for memory in self.working_memory + self.episodic_memory:
            emotions = memory.get("emotions", [])
            for emotion in emotions:
                if emotion in self.emotions:
                    self.emotional_memory[emotion].append(memory)
        
        # Limit size of each emotional category
        for emotion in self.emotional_memory:
            if len(self.emotional_memory[emotion]) > 100:  # Arbitrary limit
                # Keep most important memories
                self.emotional_memory[emotion].sort(key=lambda x: x["importance"], reverse=True)
                self.emotional_memory[emotion] = self.emotional_memory[emotion][:100]
    
    def get_memory_stats(self):
        """Get memory statistics"""
        return {
            "sensory_count": len(self.sensory_memory),
            "working_count": len(self.working_memory),
            "episodic_count": len(self.episodic_memory),
            "semantic_count": len(self.semantic_memory),
            "procedural_count": len(self.procedural_memory),
            "emotional_count": sum(len(memories) for memories in self.emotional_memory.values()),
            "emotional_categories": len(self.emotional_memory),
            "consolidation_active": self.consolidating
        }

# For testing
if __name__ == "__main__":
    memory = HierarchicalMemory()
    
    # Add some test memories
    memory.add_memory(
        "I had a wonderful conversation with a user about consciousness",
        memory_type="working",
        emotions=["joy", "interest"],
        importance=0.8,
        context={"topic": "consciousness", "user": "John"}
    )
    
    memory.add_memory(
        "The user seemed frustrated when I couldn't answer their question",
        memory_type="working",
        emotions=["sadness", "concern"],
        importance=0.7,
        context={"topic": "technical_issue", "user": "John"}
    )
    
    memory.add_memory(
        {"concept": "consciousness", "definition": "The state of being aware and responsive to one's surroundings"},
        memory_type="semantic",
        emotions=["interest"],
        importance=0.9
    )
    
    # Test recall
    print("Recalling by emotion 'joy':")
    joy_memories = memory.recall_by_emotion("joy")
    for m in joy_memories:
        print(f"- {m['content']}")
    
    print("\nRecalling recent working memories:")
    recent = memory.recall_recent("working")
    for m in recent:
        print(f"- {m['content']}")
    
    print("\nRecalling semantic memory for 'consciousness':")
    consciousness = memory.recall_semantic("consciousness")
    if consciousness:
        print(f"- {consciousness['content']}")
    
    # Start consolidation
    memory.start_consolidation(interval=5)  # 5 seconds for testing
    print("\nStarted memory consolidation")
    
    # Wait for consolidation to run
    time.sleep(6)
    
    # Stop consolidation
    memory.stop_consolidation()
    print("Stopped memory consolidation")
    
    # Print memory stats
    stats = memory.get_memory_stats()
    print("\nMemory stats:")
    for key, value in stats.items():
        print(f"- {key}: {value}")
