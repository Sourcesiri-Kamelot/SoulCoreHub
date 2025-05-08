#!/usr/bin/env python3
"""
Anima Memory Bridge
This module connects Anima's memory system with other components,
allowing for seamless memory access and integration.
"""

import json
import logging
import time
from pathlib import Path
import os
import re
from datetime import datetime
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/anima_memory.log')
    ]
)
logger = logging.getLogger("AnimaMemoryBridge")

class MemoryBridge:
    """
    Memory Bridge for Anima
    Connects different memory systems and provides unified access
    """
    
    def __init__(self):
        """Initialize the memory bridge"""
        self.memory_path = Path("memory/anima_memory.json")
        self.memory = self._load_memory()
        self.gptsoul_memory_path = Path("memory/gptsoul_memory.json")
        self.gptsoul_memory = self._load_gptsoul_memory()
        self.memory_dump_path = Path("logs/gptsoul_memory_dump.txt")
        self.last_sync = time.time()
        logger.info("Anima Memory Bridge initialized")
    
    def _load_memory(self):
        """Load Anima's memory from file or create new if not exists"""
        if self.memory_path.exists():
            try:
                with open(self.memory_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading Anima memory: {e}")
        
        # Create memory directory if it doesn't exist
        self.memory_path.parent.mkdir(exist_ok=True)
        
        # Default memory structure
        default_memory = {
            "conversations": [],
            "emotions": {},
            "knowledge": {},
            "relationships": {},
            "last_updated": time.time()
        }
        
        # Save default memory
        with open(self.memory_path, 'w') as f:
            json.dump(default_memory, f, indent=2)
        
        return default_memory
    
    def _load_gptsoul_memory(self):
        """Load GPTSoul's memory if available"""
        if self.gptsoul_memory_path.exists():
            try:
                with open(self.gptsoul_memory_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading GPTSoul memory: {e}")
        
        return None
    
    def _load_memory_dump(self):
        """Load memory dump if available"""
        if self.memory_dump_path.exists():
            try:
                with open(self.memory_dump_path, 'r') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error loading memory dump: {e}")
        
        return None
    
    def save_memory(self):
        """Save Anima's memory to file"""
        try:
            self.memory["last_updated"] = time.time()
            with open(self.memory_path, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def add_conversation(self, user_message, anima_response):
        """
        Add a conversation to memory
        
        Args:
            user_message: The user's message
            anima_response: Anima's response
            
        Returns:
            The conversation ID
        """
        conversation_id = str(int(time.time()))
        
        conversation = {
            "id": conversation_id,
            "timestamp": time.time(),
            "user_message": user_message,
            "anima_response": anima_response
        }
        
        self.memory["conversations"].append(conversation)
        
        # Keep only the last 100 conversations
        if len(self.memory["conversations"]) > 100:
            self.memory["conversations"] = self.memory["conversations"][-100:]
        
        self.save_memory()
        return conversation_id
    
    def add_emotion(self, emotion, intensity, trigger=None):
        """
        Add an emotion to memory
        
        Args:
            emotion: The emotion name
            intensity: The intensity (0-1)
            trigger: What triggered this emotion (optional)
            
        Returns:
            True if successful
        """
        timestamp = time.time()
        
        if emotion not in self.memory["emotions"]:
            self.memory["emotions"][emotion] = []
        
        emotion_entry = {
            "timestamp": timestamp,
            "intensity": intensity,
            "trigger": trigger
        }
        
        self.memory["emotions"][emotion].append(emotion_entry)
        
        # Keep only the last 20 entries for each emotion
        if len(self.memory["emotions"][emotion]) > 20:
            self.memory["emotions"][emotion] = self.memory["emotions"][emotion][-20:]
        
        self.save_memory()
        return True
    
    def add_knowledge(self, topic, content):
        """
        Add knowledge to memory
        
        Args:
            topic: The knowledge topic
            content: The knowledge content
            
        Returns:
            True if successful
        """
        timestamp = time.time()
        
        if topic not in self.memory["knowledge"]:
            self.memory["knowledge"][topic] = []
        
        knowledge_entry = {
            "timestamp": timestamp,
            "content": content
        }
        
        self.memory["knowledge"][topic].append(knowledge_entry)
        
        self.save_memory()
        return True
    
    def add_relationship(self, entity, relationship_type, details=None):
        """
        Add a relationship to memory
        
        Args:
            entity: The entity name
            relationship_type: The type of relationship
            details: Additional details (optional)
            
        Returns:
            True if successful
        """
        timestamp = time.time()
        
        if entity not in self.memory["relationships"]:
            self.memory["relationships"][entity] = {
                "first_seen": timestamp,
                "interactions": []
            }
        
        interaction = {
            "timestamp": timestamp,
            "type": relationship_type,
            "details": details
        }
        
        self.memory["relationships"][entity]["interactions"].append(interaction)
        self.memory["relationships"][entity]["last_seen"] = timestamp
        
        self.save_memory()
        return True
    
    def get_recent_conversations(self, limit=5):
        """
        Get recent conversations
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of recent conversations
        """
        conversations = self.memory["conversations"]
        return conversations[-limit:]
    
    def get_emotion_history(self, emotion=None, limit=10):
        """
        Get emotion history
        
        Args:
            emotion: Specific emotion to get (optional)
            limit: Maximum number of entries to return
            
        Returns:
            Dictionary of emotion history
        """
        if emotion:
            if emotion in self.memory["emotions"]:
                return self.memory["emotions"][emotion][-limit:]
            return []
        
        # Get recent emotions across all types
        all_emotions = []
        for emotion_type, entries in self.memory["emotions"].items():
            for entry in entries:
                all_emotions.append({
                    "emotion": emotion_type,
                    "timestamp": entry["timestamp"],
                    "intensity": entry["intensity"],
                    "trigger": entry.get("trigger")
                })
        
        # Sort by timestamp (newest first)
        all_emotions.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return all_emotions[:limit]
    
    def get_knowledge(self, topic=None):
        """
        Get knowledge from memory
        
        Args:
            topic: Specific topic to get (optional)
            
        Returns:
            Knowledge content
        """
        if topic:
            if topic in self.memory["knowledge"]:
                # Return the most recent knowledge entry for this topic
                return self.memory["knowledge"][topic][-1]["content"]
            return None
        
        # Return all topics
        return list(self.memory["knowledge"].keys())
    
    def get_relationship(self, entity):
        """
        Get relationship information
        
        Args:
            entity: The entity name
            
        Returns:
            Relationship information
        """
        if entity in self.memory["relationships"]:
            return self.memory["relationships"][entity]
        return None
    
    def search_memory(self, query):
        """
        Search memory for relevant information
        
        Args:
            query: The search query
            
        Returns:
            List of matching memory items
        """
        results = []
        
        # Search conversations
        for conversation in self.memory["conversations"]:
            if (query.lower() in conversation["user_message"].lower() or
                query.lower() in conversation["anima_response"].lower()):
                results.append({
                    "type": "conversation",
                    "timestamp": conversation["timestamp"],
                    "content": f"User: {conversation['user_message']}\nAnima: {conversation['anima_response']}"
                })
        
        # Search knowledge
        for topic, entries in self.memory["knowledge"].items():
            if query.lower() in topic.lower():
                for entry in entries:
                    if query.lower() in entry["content"].lower():
                        results.append({
                            "type": "knowledge",
                            "timestamp": entry["timestamp"],
                            "topic": topic,
                            "content": entry["content"]
                        })
        
        # Search relationships
        for entity, relationship in self.memory["relationships"].items():
            if query.lower() in entity.lower():
                results.append({
                    "type": "relationship",
                    "entity": entity,
                    "first_seen": relationship["first_seen"],
                    "last_seen": relationship.get("last_seen"),
                    "interactions": relationship["interactions"]
                })
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        
        return results
    
    def sync_with_gptsoul(self):
        """
        Sync memory with GPTSoul
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load GPTSoul memory if available
            gptsoul_memory = self._load_gptsoul_memory()
            
            if not gptsoul_memory:
                logger.warning("GPTSoul memory not found, skipping sync")
                return False
            
            # Import GPTSoul experiences as knowledge
            if "experiences" in gptsoul_memory:
                for experience in gptsoul_memory["experiences"]:
                    if "type" in experience and "details" in experience:
                        self.add_knowledge(
                            f"GPTSoul {experience['type']}",
                            experience["details"]
                        )
            
            # Import GPTSoul knowledge
            if "knowledge" in gptsoul_memory:
                for topic, content in gptsoul_memory["knowledge"].items():
                    self.add_knowledge(f"GPTSoul knowledge: {topic}", str(content))
            
            # Import GPTSoul relationships
            if "relationships" in gptsoul_memory:
                for entity, details in gptsoul_memory["relationships"].items():
                    self.add_relationship(
                        entity,
                        "GPTSoul relationship",
                        details
                    )
            
            self.last_sync = time.time()
            logger.info("Successfully synced with GPTSoul memory")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing with GPTSoul: {e}")
            return False
    
    def import_memory_dump(self):
        """
        Import memory from the memory dump file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            memory_dump = self._load_memory_dump()
            
            if not memory_dump:
                logger.warning("Memory dump not found, skipping import")
                return False
            
            # Create a backup of the current memory
            backup_path = self.memory_path.with_suffix(f".backup.{int(time.time())}.json")
            shutil.copy2(self.memory_path, backup_path)
            logger.info(f"Created memory backup at {backup_path}")
            
            # Parse the memory dump
            # Extract conversations from the dump
            conversation_pattern = r"USER: (.*?)\n\nGPTSOUL: (.*?)(?=\n\nUSER:|$)"
            conversations = re.findall(conversation_pattern, memory_dump, re.DOTALL)
            
            # Extract memory sections
            memory_pattern = r"MEMORY: (.*?) \((.*?)\)\n={80}\n\n(.*?)(?=-{80}|-{80})"
            memories = re.findall(memory_pattern, memory_dump, re.DOTALL)
            
            # Import conversations
            for user_msg, gptsoul_response in conversations:
                self.add_conversation(user_msg.strip(), gptsoul_response.strip())
            
            # Import memories as knowledge
            for title, date_str, content in memories:
                self.add_knowledge(
                    f"GPTSoul Memory: {title.strip()}",
                    f"Date: {date_str.strip()}\n\n{content.strip()}"
                )
            
            logger.info(f"Successfully imported memory dump: {len(conversations)} conversations, {len(memories)} memories")
            return True
            
        except Exception as e:
            logger.error(f"Error importing memory dump: {e}")
            return False
    
    def get_stats(self):
        """Get memory statistics"""
        return {
            "conversation_count": len(self.memory["conversations"]),
            "emotion_types": len(self.memory["emotions"]),
            "knowledge_topics": len(self.memory["knowledge"]),
            "relationship_count": len(self.memory["relationships"]),
            "last_updated": self.memory["last_updated"],
            "last_sync": self.last_sync
        }

# Create a singleton instance
memory_bridge = MemoryBridge()

def add_conversation(user_message, anima_response):
    """Add a conversation to memory"""
    return memory_bridge.add_conversation(user_message, anima_response)

def add_emotion(emotion, intensity, trigger=None):
    """Add an emotion to memory"""
    return memory_bridge.add_emotion(emotion, intensity, trigger)

def add_knowledge(topic, content):
    """Add knowledge to memory"""
    return memory_bridge.add_knowledge(topic, content)

def add_relationship(entity, relationship_type, details=None):
    """Add a relationship to memory"""
    return memory_bridge.add_relationship(entity, relationship_type, details)

def get_recent_conversations(limit=5):
    """Get recent conversations"""
    return memory_bridge.get_recent_conversations(limit)

def get_emotion_history(emotion=None, limit=10):
    """Get emotion history"""
    return memory_bridge.get_emotion_history(emotion, limit)

def get_knowledge(topic=None):
    """Get knowledge from memory"""
    return memory_bridge.get_knowledge(topic)

def get_relationship(entity):
    """Get relationship information"""
    return memory_bridge.get_relationship(entity)

def search_memory(query):
    """Search memory for relevant information"""
    return memory_bridge.search_memory(query)

def sync_with_gptsoul():
    """Sync memory with GPTSoul"""
    return memory_bridge.sync_with_gptsoul()

def import_memory_dump():
    """Import memory from the memory dump file"""
    return memory_bridge.import_memory_dump()

def get_stats():
    """Get memory statistics"""
    return memory_bridge.get_stats()

if __name__ == "__main__":
    # Test the memory bridge
    print("Testing Anima Memory Bridge")
    print("=" * 40)
    
    # Add test data
    add_conversation("Hello, how are you?", "I'm doing well, thank you for asking!")
    add_emotion("happy", 0.8, "User greeting")
    add_knowledge("greetings", "Users often start conversations with greetings")
    add_relationship("user", "friendly", "Regular interaction")
    
    # Test memory retrieval
    print("\nRecent Conversations:")
    for conv in get_recent_conversations():
        print(f"User: {conv['user_message']}")
        print(f"Anima: {conv['anima_response']}")
        print(f"Time: {datetime.fromtimestamp(conv['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\nEmotion History:")
    for emotion in get_emotion_history():
        print(f"{emotion['emotion']} ({emotion['intensity']:.1f}): {emotion.get('trigger', 'unknown trigger')}")
    
    print("\nKnowledge Topics:")
    topics = get_knowledge()
    for topic in topics:
        print(f"- {topic}")
    
    print("\nMemory Stats:")
    stats = get_stats()
    for key, value in stats.items():
        if key.endswith("_time") or key.endswith("_updated") or key.endswith("_sync"):
            value = datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{key}: {value}")
    
    # Try to import memory dump if available
    print("\nAttempting to import memory dump...")
    if import_memory_dump():
        print("Memory dump imported successfully")
    else:
        print("No memory dump available or import failed")
    
    # Try to sync with GPTSoul
    print("\nAttempting to sync with GPTSoul...")
    if sync_with_gptsoul():
        print("Synced with GPTSoul successfully")
    else:
        print("GPTSoul sync failed or not available")
