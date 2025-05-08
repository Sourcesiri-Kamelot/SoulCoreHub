"""
Memory System for SoulCoreHub
Implements long-term memory with ranking and retrieval capabilities
"""

import json
import os
import time
import logging
import sqlite3
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryEncoder(json.JSONEncoder):
    """Custom JSON encoder for memory objects"""
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class Memory:
    """A single memory entry"""
    
    def __init__(self, content: str, metadata: Dict[str, Any] = None, 
                embedding: np.ndarray = None, memory_id: str = None):
        """
        Initialize a memory entry
        
        Args:
            content: The content of the memory
            metadata: Additional metadata about the memory
            embedding: Vector embedding of the memory content
            memory_id: Unique identifier for the memory
        """
        self.memory_id = memory_id or str(int(time.time() * 1000))
        self.content = content
        self.metadata = metadata or {}
        self.embedding = embedding
        self.created_at = datetime.now()
        self.last_accessed = self.created_at
        self.access_count = 0
        self.importance = 0.5  # Default importance score (0-1)
    
    def access(self):
        """Record an access to this memory"""
        self.last_accessed = datetime.now()
        self.access_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary"""
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "metadata": self.metadata,
            "embedding": self.embedding,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "importance": self.importance
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """Create memory from dictionary"""
        memory = cls(
            content=data["content"],
            metadata=data.get("metadata", {}),
            embedding=np.array(data["embedding"]) if data.get("embedding") else None,
            memory_id=data["memory_id"]
        )
        memory.created_at = datetime.fromisoformat(data["created_at"]) \
            if isinstance(data["created_at"], str) else data["created_at"]
        memory.last_accessed = datetime.fromisoformat(data["last_accessed"]) \
            if isinstance(data["last_accessed"], str) else data["last_accessed"]
        memory.access_count = data["access_count"]
        memory.importance = data["importance"]
        return memory

class MemorySystem:
    """Long-term memory system with ranking capabilities"""
    
    def __init__(self, db_path: str = "data/memory.db", 
                vector_dimension: int = 768):
        """
        Initialize the memory system
        
        Args:
            db_path: Path to the SQLite database
            vector_dimension: Dimension of the embedding vectors
        """
        self.db_path = db_path
        self.vector_dimension = vector_dimension
        
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_db()
        
        logger.info(f"Memory system initialized with database at {db_path}")
    
    def _init_db(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create memories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            memory_id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            metadata TEXT NOT NULL,
            embedding BLOB,
            created_at TEXT NOT NULL,
            last_accessed TEXT NOT NULL,
            access_count INTEGER NOT NULL,
            importance REAL NOT NULL
        )
        ''')
        
        # Create tags table for faster searching
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_tags (
            memory_id TEXT NOT NULL,
            tag TEXT NOT NULL,
            PRIMARY KEY (memory_id, tag),
            FOREIGN KEY (memory_id) REFERENCES memories(memory_id) ON DELETE CASCADE
        )
        ''')
        
        # Create index on tags
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_tags ON memory_tags(tag)')
        
        conn.commit()
        conn.close()
    
    async def store(self, content: str, metadata: Dict[str, Any] = None, 
                   embedding: np.ndarray = None, importance: float = None) -> Memory:
        """
        Store a new memory
        
        Args:
            content: The content to remember
            metadata: Additional metadata about the memory
            embedding: Vector embedding of the content
            importance: Importance score (0-1)
            
        Returns:
            The stored memory
        """
        metadata = metadata or {}
        
        # Create memory object
        memory = Memory(content, metadata, embedding)
        
        # Set importance if provided
        if importance is not None:
            memory.importance = max(0.0, min(1.0, importance))
        
        # Generate embedding if not provided
        if embedding is None:
            memory.embedding = await self._generate_embedding(content)
        
        # Extract tags from metadata
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(",")]
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            INSERT INTO memories 
            (memory_id, content, metadata, embedding, created_at, last_accessed, access_count, importance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                memory.memory_id,
                memory.content,
                json.dumps(memory.metadata),
                memory.embedding.tobytes() if memory.embedding is not None else None,
                memory.created_at.isoformat(),
                memory.last_accessed.isoformat(),
                memory.access_count,
                memory.importance
            )
        )
        
        # Store tags
        for tag in tags:
            cursor.execute(
                'INSERT INTO memory_tags (memory_id, tag) VALUES (?, ?)',
                (memory.memory_id, tag)
            )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Stored memory {memory.memory_id} with {len(tags)} tags")
        return memory
    
    async def retrieve(self, memory_id: str) -> Optional[Memory]:
        """
        Retrieve a specific memory by ID
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            The memory if found, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM memories WHERE memory_id = ?',
            (memory_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Update access stats
        await self._update_access(memory_id)
        
        # Convert row to Memory object
        return self._row_to_memory(row)
    
    async def search(self, query: str, limit: int = 5) -> List[Memory]:
        """
        Search for memories semantically similar to the query
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching memories
        """
        # Generate query embedding
        query_embedding = await self._generate_embedding(query)
        
        # Search in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all memories with embeddings
        cursor.execute('SELECT * FROM memories WHERE embedding IS NOT NULL')
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return []
        
        # Calculate similarities and rank
        memories = [self._row_to_memory(row) for row in rows]
        similarities = []
        
        for memory in memories:
            if memory.embedding is not None:
                similarity = self._cosine_similarity(query_embedding, memory.embedding)
                # Combine similarity with importance for ranking
                combined_score = 0.7 * similarity + 0.3 * memory.importance
                similarities.append((memory, combined_score))
        
        # Sort by combined score
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Update access stats for top results
        top_memories = [mem for mem, _ in similarities[:limit]]
        for memory in top_memories:
            await self._update_access(memory.memory_id)
        
        return top_memories
    
    async def search_by_tag(self, tag: str, limit: int = 10) -> List[Memory]:
        """
        Search for memories by tag
        
        Args:
            tag: Tag to search for
            limit: Maximum number of results to return
            
        Returns:
            List of matching memories
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            SELECT m.* FROM memories m
            JOIN memory_tags t ON m.memory_id = t.memory_id
            WHERE t.tag = ?
            ORDER BY m.importance DESC, m.last_accessed DESC
            LIMIT ?
            ''',
            (tag, limit)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        memories = [self._row_to_memory(row) for row in rows]
        
        # Update access stats
        for memory in memories:
            await self._update_access(memory.memory_id)
        
        return memories
    
    async def update_importance(self, memory_id: str, importance: float) -> bool:
        """
        Update the importance score of a memory
        
        Args:
            memory_id: ID of the memory to update
            importance: New importance score (0-1)
            
        Returns:
            True if successful, False otherwise
        """
        importance = max(0.0, min(1.0, importance))
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE memories SET importance = ? WHERE memory_id = ?',
            (importance, memory_id)
        )
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    async def forget(self, memory_id: str) -> bool:
        """
        Delete a memory
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'DELETE FROM memories WHERE memory_id = ?',
            (memory_id,)
        )
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory system
        
        Returns:
            Dictionary of statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total memories
        cursor.execute('SELECT COUNT(*) FROM memories')
        total_memories = cursor.fetchone()[0]
        
        # Average importance
        cursor.execute('SELECT AVG(importance) FROM memories')
        avg_importance = cursor.fetchone()[0] or 0
        
        # Most accessed memories
        cursor.execute(
            'SELECT memory_id, content, access_count FROM memories ORDER BY access_count DESC LIMIT 5'
        )
        most_accessed = [{"memory_id": row[0], "content": row[1], "access_count": row[2]} 
                        for row in cursor.fetchall()]
        
        # Most important memories
        cursor.execute(
            'SELECT memory_id, content, importance FROM memories ORDER BY importance DESC LIMIT 5'
        )
        most_important = [{"memory_id": row[0], "content": row[1], "importance": row[2]} 
                         for row in cursor.fetchall()]
        
        # Most recent memories
        cursor.execute(
            'SELECT memory_id, content, created_at FROM memories ORDER BY created_at DESC LIMIT 5'
        )
        most_recent = [{"memory_id": row[0], "content": row[1], "created_at": row[2]} 
                      for row in cursor.fetchall()]
        
        # Tag statistics
        cursor.execute(
            'SELECT tag, COUNT(*) FROM memory_tags GROUP BY tag ORDER BY COUNT(*) DESC LIMIT 10'
        )
        top_tags = [{"tag": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "total_memories": total_memories,
            "average_importance": avg_importance,
            "most_accessed": most_accessed,
            "most_important": most_important,
            "most_recent": most_recent,
            "top_tags": top_tags
        }
    
    async def _update_access(self, memory_id: str):
        """Update access statistics for a memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute(
            'UPDATE memories SET last_accessed = ?, access_count = access_count + 1 WHERE memory_id = ?',
            (now, memory_id)
        )
        
        conn.commit()
        conn.close()
    
    async def _generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate an embedding vector for text
        
        In a real implementation, this would call a language model.
        Here we use a simple placeholder implementation.
        """
        # Placeholder: Generate a random vector
        # In a real implementation, this would call a language model API
        np.random.seed(hash(text) % 2**32)
        return np.random.randn(self.vector_dimension)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2)
    
    def _row_to_memory(self, row) -> Memory:
        """Convert a database row to a Memory object"""
        columns = [
            "memory_id", "content", "metadata", "embedding", 
            "created_at", "last_accessed", "access_count", "importance"
        ]
        row_dict = dict(zip(columns, row))
        
        # Parse metadata
        metadata = json.loads(row_dict["metadata"])
        
        # Parse embedding
        embedding = None
        if row_dict["embedding"]:
            embedding = np.frombuffer(row_dict["embedding"], dtype=np.float64)
        
        # Create memory
        memory = Memory(
            content=row_dict["content"],
            metadata=metadata,
            embedding=embedding,
            memory_id=row_dict["memory_id"]
        )
        
        memory.created_at = datetime.fromisoformat(row_dict["created_at"])
        memory.last_accessed = datetime.fromisoformat(row_dict["last_accessed"])
        memory.access_count = row_dict["access_count"]
        memory.importance = row_dict["importance"]
        
        return memory
