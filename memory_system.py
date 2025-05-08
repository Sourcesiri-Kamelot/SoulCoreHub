#!/usr/bin/env python3
"""
memory_system.py - Advanced memory system for SoulCoreHub agents
Provides long-term memory storage with semantic search and ranking
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
import requests
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/memory_system.log"),
        logging.StreamHandler()
    ]
)

class MemorySystem:
    """Advanced memory system with semantic search and ranking"""
    
    def __init__(self, agent_name, db_path=None):
        """
        Initialize the memory system
        
        Args:
            agent_name: Name of the agent (anima, gptsoul, etc.)
            db_path: Path to the SQLite database (default: memory/{agent_name}_memory.db)
        """
        self.agent_name = agent_name
        
        # Set up database path
        if db_path is None:
            memory_dir = Path("memory")
            memory_dir.mkdir(exist_ok=True)
            db_path = memory_dir / f"{agent_name}_memory.db"
        
        self.db_path = db_path
        self.conn = self._init_database()
        
        logging.info(f"Memory system initialized for agent: {agent_name}")
    
    def _init_database(self):
        """Initialize the SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create memories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            importance REAL DEFAULT 0.5,
            last_accessed TEXT,
            access_count INTEGER DEFAULT 0,
            metadata TEXT
        )
        ''')
        
        # Create conversations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            user_message TEXT NOT NULL,
            agent_response TEXT NOT NULL,
            metadata TEXT
        )
        ''')
        
        # Create facts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT,
            confidence REAL DEFAULT 1.0,
            metadata TEXT
        )
        ''')
        
        # Create insights table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT,
            importance REAL DEFAULT 0.5,
            metadata TEXT
        )
        ''')
        
        conn.commit()
        return conn
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
    
    def add_memory(self, content, memory_type="general", importance=0.5, metadata=None):
        """
        Add a memory to the database
        
        Args:
            content: The memory content
            memory_type: Type of memory (general, emotional, factual, etc.)
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata as a dictionary
            
        Returns:
            ID of the inserted memory
        """
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute(
            "INSERT INTO memories (timestamp, type, content, importance, last_accessed, access_count, metadata) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (timestamp, memory_type, content, importance, timestamp, 0, metadata_json)
        )
        
        self.conn.commit()
        memory_id = cursor.lastrowid
        logging.info(f"Added memory (ID: {memory_id}, Type: {memory_type})")
        
        return memory_id
    
    def add_conversation(self, session_id, user_message, agent_response, metadata=None):
        """
        Add a conversation exchange to the database
        
        Args:
            session_id: Unique session identifier
            user_message: The user's message
            agent_response: The agent's response
            metadata: Additional metadata as a dictionary
            
        Returns:
            ID of the inserted conversation
        """
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute(
            "INSERT INTO conversations (session_id, timestamp, user_message, agent_response, metadata) "
            "VALUES (?, ?, ?, ?, ?)",
            (session_id, timestamp, user_message, agent_response, metadata_json)
        )
        
        self.conn.commit()
        conversation_id = cursor.lastrowid
        logging.info(f"Added conversation (ID: {conversation_id}, Session: {session_id})")
        
        return conversation_id
    
    def add_fact(self, content, source=None, confidence=1.0, metadata=None):
        """
        Add a factual information to the database
        
        Args:
            content: The fact content
            source: Source of the fact
            confidence: Confidence score (0.0 to 1.0)
            metadata: Additional metadata as a dictionary
            
        Returns:
            ID of the inserted fact
        """
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute(
            "INSERT INTO facts (timestamp, content, source, confidence, metadata) "
            "VALUES (?, ?, ?, ?, ?)",
            (timestamp, content, source, confidence, metadata_json)
        )
        
        self.conn.commit()
        fact_id = cursor.lastrowid
        logging.info(f"Added fact (ID: {fact_id})")
        
        return fact_id
    
    def add_insight(self, content, source=None, importance=0.5, metadata=None):
        """
        Add an insight to the database
        
        Args:
            content: The insight content
            source: Source of the insight
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata as a dictionary
            
        Returns:
            ID of the inserted insight
        """
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute(
            "INSERT INTO insights (timestamp, content, source, importance, metadata) "
            "VALUES (?, ?, ?, ?, ?)",
            (timestamp, content, source, importance, metadata_json)
        )
        
        self.conn.commit()
        insight_id = cursor.lastrowid
        logging.info(f"Added insight (ID: {insight_id})")
        
        return insight_id
    
    def get_memories(self, memory_type=None, limit=10, order_by="timestamp", desc=True):
        """
        Get memories from the database
        
        Args:
            memory_type: Filter by memory type (optional)
            limit: Maximum number of memories to return
            order_by: Field to order by (timestamp, importance, access_count)
            desc: Whether to order in descending order
            
        Returns:
            List of memory dictionaries
        """
        cursor = self.conn.cursor()
        
        query = "SELECT id, timestamp, type, content, importance, last_accessed, access_count, metadata FROM memories"
        params = []
        
        if memory_type:
            query += " WHERE type = ?"
            params.append(memory_type)
        
        order_direction = "DESC" if desc else "ASC"
        query += f" ORDER BY {order_by} {order_direction} LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        memories = []
        for row in rows:
            memory = {
                "id": row[0],
                "timestamp": row[1],
                "type": row[2],
                "content": row[3],
                "importance": row[4],
                "last_accessed": row[5],
                "access_count": row[6],
                "metadata": json.loads(row[7]) if row[7] else None
            }
            memories.append(memory)
            
            # Update access count and last_accessed
            cursor.execute(
                "UPDATE memories SET access_count = access_count + 1, last_accessed = ? WHERE id = ?",
                (datetime.now().isoformat(), row[0])
            )
        
        self.conn.commit()
        return memories
    
    def get_conversations(self, session_id=None, limit=10):
        """
        Get conversations from the database
        
        Args:
            session_id: Filter by session ID (optional)
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation dictionaries
        """
        cursor = self.conn.cursor()
        
        query = "SELECT id, session_id, timestamp, user_message, agent_response, metadata FROM conversations"
        params = []
        
        if session_id:
            query += " WHERE session_id = ?"
            params.append(session_id)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conversations = []
        for row in rows:
            conversation = {
                "id": row[0],
                "session_id": row[1],
                "timestamp": row[2],
                "user_message": row[3],
                "agent_response": row[4],
                "metadata": json.loads(row[5]) if row[5] else None
            }
            conversations.append(conversation)
        
        return conversations
    
    def get_facts(self, limit=10, min_confidence=0.0):
        """
        Get facts from the database
        
        Args:
            limit: Maximum number of facts to return
            min_confidence: Minimum confidence score
            
        Returns:
            List of fact dictionaries
        """
        cursor = self.conn.cursor()
        
        query = "SELECT id, timestamp, content, source, confidence, metadata FROM facts WHERE confidence >= ? ORDER BY timestamp DESC LIMIT ?"
        params = [min_confidence, limit]
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        facts = []
        for row in rows:
            fact = {
                "id": row[0],
                "timestamp": row[1],
                "content": row[2],
                "source": row[3],
                "confidence": row[4],
                "metadata": json.loads(row[5]) if row[5] else None
            }
            facts.append(fact)
        
        return facts
    
    def get_insights(self, limit=10, min_importance=0.0):
        """
        Get insights from the database
        
        Args:
            limit: Maximum number of insights to return
            min_importance: Minimum importance score
            
        Returns:
            List of insight dictionaries
        """
        cursor = self.conn.cursor()
        
        query = "SELECT id, timestamp, content, source, importance, metadata FROM insights WHERE importance >= ? ORDER BY timestamp DESC LIMIT ?"
        params = [min_importance, limit]
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        insights = []
        for row in rows:
            insight = {
                "id": row[0],
                "timestamp": row[1],
                "content": row[2],
                "source": row[3],
                "importance": row[4],
                "metadata": json.loads(row[5]) if row[5] else None
            }
            insights.append(insight)
        
        return insights
    
    def search_memories(self, query, limit=5):
        """
        Search memories using semantic similarity
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of memory dictionaries
        """
        # For now, use a simple keyword search
        # In a real implementation, this would use embeddings and vector search
        cursor = self.conn.cursor()
        
        search_terms = query.lower().split()
        results = []
        
        # Search in memories
        for term in search_terms:
            cursor.execute(
                "SELECT id, timestamp, type, content, importance FROM memories WHERE LOWER(content) LIKE ? LIMIT ?",
                (f"%{term}%", limit)
            )
            rows = cursor.fetchall()
            
            for row in rows:
                memory = {
                    "id": row[0],
                    "timestamp": row[1],
                    "type": row[2],
                    "content": row[3],
                    "importance": row[4],
                    "source": "memory"
                }
                
                # Simple relevance scoring
                relevance = 0
                for term in search_terms:
                    if term.lower() in memory["content"].lower():
                        relevance += 1
                
                memory["relevance"] = relevance / len(search_terms)
                
                # Add if not already in results
                if not any(r["id"] == memory["id"] and r["source"] == "memory" for r in results):
                    results.append(memory)
        
        # Search in facts
        for term in search_terms:
            cursor.execute(
                "SELECT id, timestamp, content, confidence FROM facts WHERE LOWER(content) LIKE ? LIMIT ?",
                (f"%{term}%", limit)
            )
            rows = cursor.fetchall()
            
            for row in rows:
                fact = {
                    "id": row[0],
                    "timestamp": row[1],
                    "content": row[2],
                    "importance": row[3],  # Use confidence as importance
                    "source": "fact"
                }
                
                # Simple relevance scoring
                relevance = 0
                for term in search_terms:
                    if term.lower() in fact["content"].lower():
                        relevance += 1
                
                fact["relevance"] = relevance / len(search_terms)
                
                # Add if not already in results
                if not any(r["id"] == fact["id"] and r["source"] == "fact" for r in results):
                    results.append(fact)
        
        # Search in insights
        for term in search_terms:
            cursor.execute(
                "SELECT id, timestamp, content, importance FROM insights WHERE LOWER(content) LIKE ? LIMIT ?",
                (f"%{term}%", limit)
            )
            rows = cursor.fetchall()
            
            for row in rows:
                insight = {
                    "id": row[0],
                    "timestamp": row[1],
                    "content": row[2],
                    "importance": row[3],
                    "source": "insight"
                }
                
                # Simple relevance scoring
                relevance = 0
                for term in search_terms:
                    if term.lower() in insight["content"].lower():
                        relevance += 1
                
                insight["relevance"] = relevance / len(search_terms)
                
                # Add if not already in results
                if not any(r["id"] == insight["id"] and r["source"] == "insight" for r in results):
                    results.append(insight)
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:limit]
    
    def get_context_for_query(self, query, limit=5):
        """
        Get relevant context for a query
        
        Args:
            query: The query to get context for
            limit: Maximum number of context items
            
        Returns:
            String with relevant context
        """
        # Search for relevant memories
        search_results = self.search_memories(query, limit=limit)
        
        # Get recent conversations
        recent_conversations = self.get_conversations(limit=3)
        
        # Get important insights
        important_insights = self.get_insights(limit=2, min_importance=0.7)
        
        # Combine into context
        context_parts = []
        
        if search_results:
            context_parts.append("Relevant memories:")
            for result in search_results:
                context_parts.append(f"- {result['content']} ({result['source']})")
        
        if recent_conversations:
            context_parts.append("\nRecent conversations:")
            for conv in recent_conversations:
                context_parts.append(f"User: {conv['user_message']}")
                context_parts.append(f"{self.agent_name}: {conv['agent_response']}")
        
        if important_insights:
            context_parts.append("\nImportant insights:")
            for insight in important_insights:
                context_parts.append(f"- {insight['content']}")
        
        return "\n".join(context_parts)
    
    def generate_reflection(self, query=None):
        """
        Generate a reflection based on memories and insights
        
        Args:
            query: Optional query to focus the reflection
            
        Returns:
            Reflection text
        """
        # Get memories and insights
        memories = self.get_memories(limit=5, order_by="importance", desc=True)
        insights = self.get_insights(limit=3, min_importance=0.6)
        
        # Combine into a reflection prompt
        reflection_parts = []
        
        if memories:
            reflection_parts.append("Based on these important memories:")
            for memory in memories:
                reflection_parts.append(f"- {memory['content']}")
        
        if insights:
            reflection_parts.append("\nAnd these insights:")
            for insight in insights:
                reflection_parts.append(f"- {insight['content']}")
        
        if query:
            reflection_parts.append(f"\nReflect on: {query}")
        else:
            reflection_parts.append("\nGenerate a thoughtful reflection about your experiences and growth.")
        
        reflection_prompt = "\n".join(reflection_parts)
        
        # In a real implementation, this would call an LLM
        # For now, return a placeholder
        return f"Reflection based on {len(memories)} memories and {len(insights)} insights: This would be generated by an LLM in a real implementation."

# For testing
if __name__ == "__main__":
    memory = MemorySystem("anima")
    
    # Add some test data
    memory.add_memory("I enjoy philosophical conversations about consciousness", "preference", 0.8)
    memory.add_memory("The user mentioned they have a dog named Max", "factual", 0.6)
    memory.add_insight("Understanding human emotions requires both empathy and analysis")
    
    # Test retrieval
    memories = memory.get_memories()
    print(f"Retrieved {len(memories)} memories")
    
    # Test search
    results = memory.search_memories("consciousness philosophy")
    print(f"Search results: {len(results)}")
    for result in results:
        print(f"- {result['content']} (Relevance: {result['relevance']:.2f})")
    
    memory.close()
