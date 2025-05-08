#!/usr/bin/env python3
"""
Neural Routing System for SoulCoreHub
Combines RAG with MCP server selection for optimal query processing
"""

import os
import json
import logging
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import faiss
import pickle
from mcp_client_bridge import MCPClientBridge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("neural_routing.log"), logging.StreamHandler()]
)
logger = logging.getLogger("neural_routing")

class NeuralRouter:
    """Neural Router for combining RAG with MCP server selection"""
    
    def __init__(self, rag_vector_db_path="rag_vector_db", 
                 routing_feedback_path="routing_feedback.json",
                 mcp_ports=range(8701, 8708)):
        """Initialize the Neural Router"""
        self.rag_vector_db_path = rag_vector_db_path
        self.routing_feedback_path = routing_feedback_path
        self.mcp_ports = list(mcp_ports)
        self.mcp_client = MCPClientBridge()
        self.vectorizer = TfidfVectorizer()
        
        # Initialize or load the vector database
        self._initialize_vector_db()
        
        # Initialize or load routing feedback
        self._initialize_routing_feedback()
        
        # MCP server descriptions for relevance scoring
        self.mcp_descriptions = {
            8701: "General knowledge and factual information processing",
            8702: "Code generation and software development assistance",
            8703: "Data analysis and visualization",
            8704: "Natural language understanding and text processing",
            8705: "Image and multimedia content processing",
            8706: "Emotional intelligence and sentiment analysis",
            8707: "Strategic planning and decision making"
        }
        
        # Initialize server weights (will be updated from feedback)
        self.server_weights = {port: 1.0 for port in self.mcp_ports}
        self._update_server_weights_from_feedback()
        
        logger.info("Neural Router initialized")
    
    def _initialize_vector_db(self):
        """Initialize or load the vector database"""
        os.makedirs(self.rag_vector_db_path, exist_ok=True)
        
        self.index_path = os.path.join(self.rag_vector_db_path, "faiss_index.bin")
        self.chunks_path = os.path.join(self.rag_vector_db_path, "chunks.pkl")
        self.vectorizer_path = os.path.join(self.rag_vector_db_path, "vectorizer.pkl")
        
        # Check if vector database exists
        if os.path.exists(self.index_path) and os.path.exists(self.chunks_path) and os.path.exists(self.vectorizer_path):
            # Load existing database
            self.index = faiss.read_index(self.index_path)
            
            with open(self.chunks_path, 'rb') as f:
                self.chunks = pickle.load(f)
                
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
                
            logger.info(f"Loaded existing vector database with {len(self.chunks)} chunks")
        else:
            # Create empty database with placeholder data
            logger.warning("No existing vector database found, creating a new one")
            self.chunks = ["This is a placeholder chunk for the RAG system"]
            
            # Fit vectorizer on placeholder data
            vectors = self.vectorizer.fit_transform(self.chunks).toarray().astype('float32')
            
            # Create FAISS index
            dimension = vectors.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(vectors)
            
            # Save the database
            self._save_vector_db()
    
    def _save_vector_db(self):
        """Save the vector database"""
        faiss.write_index(self.index, self.index_path)
        
        with open(self.chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
            
        with open(self.vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
            
        logger.info(f"Saved vector database with {len(self.chunks)} chunks")
    
    def _initialize_routing_feedback(self):
        """Initialize or load routing feedback"""
        if not os.path.exists(self.routing_feedback_path):
            with open(self.routing_feedback_path, 'w') as f:
                json.dump([], f)
            logger.info(f"Created new routing feedback file: {self.routing_feedback_path}")
    
    def _load_routing_feedback(self):
        """Load routing feedback from file"""
        try:
            with open(self.routing_feedback_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Error decoding {self.routing_feedback_path}, creating new feedback file")
            return []
    
    def _update_server_weights_from_feedback(self):
        """Update server weights based on feedback"""
        feedback_data = self._load_routing_feedback()
        
        # Count positive and negative feedback for each port
        port_feedback = {port: {"positive": 0, "negative": 0} for port in self.mcp_ports}
        
        for entry in feedback_data:
            port = entry.get("port")
            feedback = entry.get("feedback")
            
            if port in self.mcp_ports and feedback in ["positive", "negative"]:
                port_feedback[port][feedback] += 1
        
        # Update weights based on feedback ratio
        for port in self.mcp_ports:
            positive = port_feedback[port]["positive"]
            negative = port_feedback[port]["negative"]
            
            # Avoid division by zero
            total = positive + negative
            if total > 0:
                # Calculate weight between 0.5 and 1.5 based on feedback
                ratio = positive / total
                self.server_weights[port] = 0.5 + ratio
            
        logger.info(f"Updated server weights from feedback: {self.server_weights}")
    
    def get_top_chunks(self, query, k=3):
        """
        Get top k chunks from the vector database that are most similar to the query
        
        Args:
            query (str): The query to find similar chunks for
            k (int): Number of chunks to return
            
        Returns:
            list: Top k chunks from the vector database
        """
        # Transform query to vector
        query_vector = self.vectorizer.transform([query]).toarray().astype('float32')
        
        # Search for similar chunks
        k = min(k, len(self.chunks))  # Ensure k is not larger than number of chunks
        distances, indices = self.index.search(query_vector, k)
        
        # Get the chunks
        top_chunks = [self.chunks[i] for i in indices[0]]
        
        logger.info(f"Retrieved top {len(top_chunks)} chunks for query")
        return top_chunks
    
    def score_mcp_servers(self, query):
        """
        Score MCP servers based on relevance to the query
        
        Args:
            query (str): The query to score servers for
            
        Returns:
            dict: Dictionary of port to relevance score
        """
        # Create vectors for query and server descriptions
        texts = [query] + [self.mcp_descriptions[port] for port in self.mcp_ports]
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        # Calculate cosine similarity between query and each server description
        query_vector = tfidf_matrix[0:1]
        server_vectors = tfidf_matrix[1:]
        similarities = cosine_similarity(query_vector, server_vectors)[0]
        
        # Apply weights from feedback
        weighted_similarities = [similarities[i] * self.server_weights[port] 
                               for i, port in enumerate(self.mcp_ports)]
        
        # Create dictionary of port to score
        scores = {port: float(score) for port, score in zip(self.mcp_ports, weighted_similarities)}
        
        logger.info(f"Scored MCP servers: {scores}")
        return scores
    
    def route_query(self, query, force_port=None):
        """
        Route a query to the most relevant MCP server
        
        Args:
            query (str): The query to route
            force_port (int, optional): Force routing to a specific port
            
        Returns:
            dict: Result containing response, route info, and metadata
        """
        start_time = datetime.now()
        
        # Get top chunks from RAG
        top_chunks = self.get_top_chunks(query)
        
        # Combine chunks with query
        context = "\n\n".join(["CONTEXT:"] + top_chunks + ["\nQUERY:", query])
        
        # Determine which MCP server to use
        if force_port is not None and force_port in self.mcp_ports:
            selected_port = force_port
            logger.info(f"Forced routing to port {selected_port}")
        else:
            # Score servers and select the highest scoring one
            scores = self.score_mcp_servers(query)
            selected_port = max(scores, key=scores.get)
            logger.info(f"Selected port {selected_port} with score {scores[selected_port]}")
        
        # Send the query to the selected MCP server
        result = self.mcp_client.query_mcp_server(context, selected_port)
        
        # Add metadata to the result
        result["metadata"] = {
            "query": query,
            "port": selected_port,
            "processing_time": (datetime.now() - start_time).total_seconds(),
            "rag_chunks_used": len(top_chunks),
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def add_feedback(self, query, port, feedback_type):
        """
        Add feedback for a routing decision
        
        Args:
            query (str): The query that was routed
            port (int): The port that was used
            feedback_type (str): Either "positive" or "negative"
            
        Returns:
            bool: True if feedback was added successfully
        """
        if feedback_type not in ["positive", "negative"]:
            logger.error(f"Invalid feedback type: {feedback_type}")
            return False
            
        if port not in self.mcp_ports:
            logger.error(f"Invalid port: {port}")
            return False
        
        # Load existing feedback
        feedback_data = self._load_routing_feedback()
        
        # Add new feedback
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "port": port,
            "feedback": feedback_type
        }
        
        feedback_data.append(feedback_entry)
        
        # Save feedback
        with open(self.routing_feedback_path, 'w') as f:
            json.dump(feedback_data, f, indent=2)
        
        # Update weights
        self._update_server_weights_from_feedback()
        
        logger.info(f"Added {feedback_type} feedback for port {port}")
        return True

# Command line interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Neural Router")
    parser.add_argument("--query", required=True, help="Query to route")
    parser.add_argument("--port", type=int, help="Force routing to a specific port")
    
    args = parser.parse_args()
    
    router = NeuralRouter()
    result = router.route_query(args.query, args.port)
    
    print(json.dumps(result, indent=2))
