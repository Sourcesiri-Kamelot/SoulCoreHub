"""
Memory components for AirTrain agents.

This module provides memory systems for agents, including short-term,
long-term, and shared memory implementations.
"""

from typing import Dict, List, Any, Optional
import json
import os
import uuid
from datetime import datetime
from pathlib import Path


class BaseMemory:
    """Base class for all memory types."""
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize a memory instance.
        
        Args:
            name: Optional name for the memory instance
        """
        self.name = name or self.__class__.__name__
        self.messages = []
    
    def add(self, message: Dict[str, Any]):
        """
        Add a message to memory.
        
        Args:
            message: Message dictionary to add to memory
        
        Returns:
            self for method chaining
        """
        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
            
        self.messages.append(message)
        return self
    
    def clear(self):
        """
        Clear all messages from memory.
        
        Returns:
            self for method chaining
        """
        self.messages = []
        return self
    
    def get_messages(self, limit: Optional[int] = None):
        """
        Get messages with optional limit.
        
        Args:
            limit: Maximum number of messages to return (from most recent)
            
        Returns:
            List of message dictionaries
        """
        if limit is None or limit <= 0:
            return self.messages
        return self.messages[-limit:]
    
    def to_dict(self):
        """
        Convert memory to a dictionary for serialization.
        
        Returns:
            Dictionary representation of memory
        """
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "messages": self.messages
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create a memory instance from a dictionary.
        
        Args:
            data: Dictionary representation of memory
            
        Returns:
            Memory instance
        """
        instance = cls(name=data.get("name"))
        instance.messages = data.get("messages", [])
        return instance


class ShortTermMemory(BaseMemory):
    """Short-term memory with automatic summarization capability."""
    
    def __init__(self, name: Optional[str] = None, max_messages: int = 10):
        """
        Initialize short-term memory.
        
        Args:
            name: Optional name for the memory instance
            max_messages: Maximum number of messages to keep before summarizing
        """
        super().__init__(name)
        self.max_messages = max_messages
        self.summaries = []
    
    def add(self, message: Dict[str, Any]):
        """
        Add message and manage memory size.
        
        If the number of messages exceeds max_messages, the oldest
        messages will be summarized and removed.
        
        Args:
            message: Message dictionary to add to memory
            
        Returns:
            self for method chaining
        """
        super().add(message)
        if len(self.messages) > self.max_messages:
            self.summarize_oldest()
        return self
    
    def summarize_oldest(self, count: int = 1):
        """
        Summarize the oldest messages in memory.
        
        Args:
            count: Number of oldest messages to summarize
            
        Returns:
            self for method chaining
        """
        if count <= 0 or count >= len(self.messages):
            return self
            
        # Get the oldest messages
        oldest = self.messages[:count]
        
        # Create a summary (simple concatenation for now - would use LLM in real impl)
        contents = [m.get("content", "") for m in oldest if "content" in m]
        summary_content = "\n".join(contents)
        summary = {
            "role": "system",
            "content": f"Summary of previous messages: {summary_content[:100]}...",
            "timestamp": datetime.now().isoformat(),
            "type": "summary",
            "original_count": count
        }
        
        # Add to summaries and remove oldest messages
        self.summaries.append(summary)
        self.messages = self.messages[count:]
        
        # Insert the summary at the beginning of messages
        self.messages.insert(0, summary)
        
        return self
    
    def to_dict(self):
        """
        Convert memory to a dictionary for serialization.
        
        Returns:
            Dictionary representation of memory
        """
        data = super().to_dict()
        data.update({
            "max_messages": self.max_messages,
            "summaries": self.summaries
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create a short-term memory instance from a dictionary.
        
        Args:
            data: Dictionary representation of memory
            
        Returns:
            ShortTermMemory instance
        """
        instance = cls(
            name=data.get("name"),
            max_messages=data.get("max_messages", 10)
        )
        instance.messages = data.get("messages", [])
        instance.summaries = data.get("summaries", [])
        return instance


class LongTermMemory(BaseMemory):
    """Long-term persistent memory with advanced retrieval capabilities."""
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize long-term memory.
        
        Args:
            name: Optional name for the memory instance
        """
        super().__init__(name)
        self.summaries = []
        self.keywords = {}
        self.embeddings = {}
        self.uuid = str(uuid.uuid4())
    
    def add(self, message: Dict[str, Any]):
        """
        Add message and update indices.
        
        Args:
            message: Message dictionary to add to memory
            
        Returns:
            self for method chaining
        """
        super().add(message)
        self._extract_keywords(message)
        # Embeddings would be created here in a real implementation
        return self
    
    def _extract_keywords(self, message: Dict[str, Any]):
        """
        Extract keywords from message for later retrieval.
        
        Args:
            message: Message to extract keywords from
        """
        if "content" not in message:
            return
            
        # Simple keyword extraction (would use NLP in real implementation)
        content = message.get("content", "").lower()
        words = content.split()
        
        for word in words:
            # Remove punctuation
            word = word.strip('.,!?():;-"\'')
            if len(word) < 3:
                continue
                
            if word not in self.keywords:
                self.keywords[word] = []
            
            # Store the index of the message
            self.keywords[word].append(len(self.messages) - 1)
    
    def search_by_keyword(self, keyword: str, limit: int = 5):
        """
        Search conversations by keyword.
        
        Args:
            keyword: Keyword to search for
            limit: Maximum number of results to return
            
        Returns:
            List of matching messages
        """
        keyword = keyword.lower()
        
        if keyword not in self.keywords:
            return []
            
        # Get message indices for this keyword
        indices = self.keywords[keyword][-limit:]
        
        # Return the messages
        return [self.messages[i] for i in indices if i < len(self.messages)]
    
    def search_by_semantic(self, query: str, limit: int = 5):
        """
        Search conversations by semantic similarity.
        
        This is a placeholder. In a real implementation, this would create
        an embedding for the query and find similar messages.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of semantically similar messages
        """
        # Placeholder - would use embeddings in real implementation
        return self.search_by_keyword(query, limit)
    
    def get_standard_storage_path(self, agent_name: str = None):
        """
        Get the standard path for storing memory data.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Path object for storing memory data
        """
        home_dir = str(Path.home())
        trmx_dir = os.path.join(home_dir, ".trmx", "agents")
        
        agent_part = agent_name or "default_agent"
        memory_part = self.name or "default_memory"
        
        # Use UUID to create a unique filename
        filename = f"{self.uuid}.json"
        
        # Create the complete path
        storage_path = os.path.join(trmx_dir, agent_part, memory_part)
        
        return os.path.join(storage_path, filename)
    
    def persist(self, storage_path: Optional[str] = None, agent_name: Optional[str] = None):
        """
        Save long-term memory to disk.
        
        Args:
            storage_path: Path to save memory data (if None, use standard path)
            agent_name: Name of the agent for standard path
            
        Returns:
            self for method chaining
        """
        if storage_path is None:
            storage_path = self.get_standard_storage_path(agent_name)
        
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        
        with open(storage_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
            
        return self
    
    def load(self, storage_path: Optional[str] = None, agent_name: Optional[str] = None):
        """
        Load long-term memory from disk.
        
        Args:
            storage_path: Path to load memory data from (if None, use standard path)
            agent_name: Name of the agent for standard path
            
        Returns:
            self for method chaining
        """
        if storage_path is None:
            storage_path = self.get_standard_storage_path(agent_name)
            
        if not os.path.exists(storage_path):
            return self
            
        with open(storage_path, "r") as f:
            data = json.load(f)
            
        self.name = data.get("name", self.name)
        self.messages = data.get("messages", [])
        self.summaries = data.get("summaries", [])
        self.keywords = data.get("keywords", {})
        if "uuid" in data:
            self.uuid = data["uuid"]
        
        return self
    
    def to_dict(self):
        """
        Convert memory to a dictionary for serialization.
        
        Returns:
            Dictionary representation of memory
        """
        data = super().to_dict()
        data.update({
            "summaries": self.summaries,
            "keywords": self.keywords,
            "uuid": self.uuid
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create a long-term memory instance from a dictionary.
        
        Args:
            data: Dictionary representation of memory
            
        Returns:
            LongTermMemory instance
        """
        instance = cls(name=data.get("name"))
        instance.messages = data.get("messages", [])
        instance.summaries = data.get("summaries", [])
        instance.keywords = data.get("keywords", {})
        instance.uuid = data.get("uuid", str(uuid.uuid4()))
        return instance


class SharedMemory(BaseMemory):
    """Memory that can be shared across multiple agents."""
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize shared memory.
        
        Args:
            name: Optional name for the memory instance
        """
        super().__init__(name)
        
    def to_dict(self):
        """
        Convert memory to a dictionary for serialization.
        
        Returns:
            Dictionary representation of memory
        """
        data = super().to_dict()
        data["shared"] = True
        return data


class AgentMemoryManager:
    """Manages multiple memory instances for an agent."""
    
    def __init__(self):
        """Initialize memory manager."""
        self.long_term_memory = LongTermMemory("primary_ltm")
        self.short_term_memories = {}
        self.shared_memories = {}
    
    def create_short_term_memory(
        self, name: str = "default", max_messages: int = 10
    ) -> ShortTermMemory:
        """
        Create a new short-term memory instance.
        
        Args:
            name: Name for the memory instance
            max_messages: Maximum number of messages before summarization
            
        Returns:
            The created ShortTermMemory instance
        """
        self.short_term_memories[name] = ShortTermMemory(name, max_messages)
        return self.short_term_memories[name]
    
    def get_short_term_memory(self, name: str = "default") -> ShortTermMemory:
        """
        Get or create a short-term memory by name.
        
        Args:
            name: Name of the short-term memory
            
        Returns:
            The requested ShortTermMemory instance
        """
        if name not in self.short_term_memories:
            return self.create_short_term_memory(name)
        return self.short_term_memories[name]
    
    def reset_short_term_memory(self, name: str = "default"):
        """
        Reset a specific short-term memory.
        
        Args:
            name: Name of the short-term memory to reset
            
        Returns:
            self for method chaining
        """
        if name in self.short_term_memories:
            self.short_term_memories[name].clear()
        return self
    
    def add_shared_memory(self, shared_memory: SharedMemory):
        """
        Add a reference to a shared memory.
        
        Args:
            shared_memory: SharedMemory instance to add
            
        Returns:
            self for method chaining
        """
        self.shared_memories[shared_memory.name] = shared_memory
        return self
    
    def add_to_all(self, message: Dict[str, Any]):
        """
        Add message to all memories.
        
        Args:
            message: Message to add to all memories
            
        Returns:
            self for method chaining
        """
        self.long_term_memory.add(message)
        for stm in self.short_term_memories.values():
            stm.add(message)
        return self
    
    def add_to_memory(self, memory_name: str, message: Dict[str, Any]):
        """
        Add message to a specific memory.
        
        Args:
            memory_name: Name of the memory to add to
            message: Message to add
            
        Returns:
            self for method chaining
        """
        # Add to long-term memory if specified
        if memory_name == "long_term":
            self.long_term_memory.add(message)
            return self
            
        # Try short-term memories
        if memory_name in self.short_term_memories:
            self.short_term_memories[memory_name].add(message)
            return self
            
        # Try shared memories
        if memory_name in self.shared_memories:
            self.shared_memories[memory_name].add(message)
            
        return self
    
    def get_context(
        self, stm_name: str = "default", include_shared: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get context from memories for agent processing.
        
        Args:
            stm_name: Name of the short-term memory to use
            include_shared: Whether to include shared memories
            
        Returns:
            Combined context from the specified memories
        """
        context = []
        
        # Add short-term memory context
        stm = self.get_short_term_memory(stm_name)
        context.extend(stm.get_messages())
        
        # Add shared memories if requested
        if include_shared:
            for shared_mem in self.shared_memories.values():
                context.extend(shared_mem.get_messages())
        
        # Would add relevant long-term memory here based on query/context
        
        return context
    
    def persist(self, storage_dir: str = None, agent_name: str = None):
        """
        Save all memories to disk.
        
        Args:
            storage_dir: Directory to save memory data, if None use standard path
            agent_name: Name of the agent for standard paths
            
        Returns:
            self for method chaining
        """
        if storage_dir is None and agent_name is None:
            raise ValueError("Either storage_dir or agent_name must be provided")
        
        # Save long-term memory
        if storage_dir:
            os.makedirs(storage_dir, exist_ok=True)
            self.long_term_memory.persist(os.path.join(storage_dir, "long_term.json"))
        else:
            self.long_term_memory.persist(agent_name=agent_name)
        
        # Save short-term memories
        if storage_dir:
            stm_dir = os.path.join(storage_dir, "short_term")
            os.makedirs(stm_dir, exist_ok=True)
            
            for name, memory in self.short_term_memories.items():
                memory_path = os.path.join(stm_dir, f"{name}.json")
                with open(memory_path, "w") as f:
                    json.dump(memory.to_dict(), f, indent=2)
        else:
            # Use standard paths for each memory
            home_dir = str(Path.home())
            stm_dir = os.path.join(home_dir, ".trmx", "agents", agent_name, "short_term")
            os.makedirs(stm_dir, exist_ok=True)
            
            for name, memory in self.short_term_memories.items():
                memory_path = os.path.join(stm_dir, f"{name}.json")
                with open(memory_path, "w") as f:
                    json.dump(memory.to_dict(), f, indent=2)
                
        return self
    
    def load(self, storage_dir: str = None, agent_name: str = None):
        """
        Load all memories from disk.
        
        Args:
            storage_dir: Directory to load memory data from
            agent_name: Name of the agent for standard paths
            
        Returns:
            self for method chaining
        """
        if storage_dir is None and agent_name is None:
            raise ValueError("Either storage_dir or agent_name must be provided")
        
        # Load long-term memory
        if storage_dir:
            ltm_path = os.path.join(storage_dir, "long_term.json")
            if os.path.exists(ltm_path):
                self.long_term_memory.load(ltm_path)
        else:
            self.long_term_memory.load(agent_name=agent_name)
            
        # Load short-term memories
        if storage_dir:
            stm_dir = os.path.join(storage_dir, "short_term")
            if os.path.exists(stm_dir):
                for filename in os.listdir(stm_dir):
                    if not filename.endswith(".json"):
                        continue
                        
                    memory_path = os.path.join(stm_dir, filename)
                    with open(memory_path, "r") as f:
                        data = json.load(f)
                        
                    name = data.get("name", filename[:-5])  # Remove .json
                    memory = ShortTermMemory.from_dict(data)
                    self.short_term_memories[name] = memory
        else:
            # Use standard paths
            home_dir = str(Path.home())
            stm_dir = os.path.join(home_dir, ".trmx", "agents", agent_name, "short_term")
            if os.path.exists(stm_dir):
                for filename in os.listdir(stm_dir):
                    if not filename.endswith(".json"):
                        continue
                        
                    memory_path = os.path.join(stm_dir, filename)
                    with open(memory_path, "r") as f:
                        data = json.load(f)
                        
                    name = data.get("name", filename[:-5])  # Remove .json
                    memory = ShortTermMemory.from_dict(data)
                    self.short_term_memories[name] = memory
                
        return self 