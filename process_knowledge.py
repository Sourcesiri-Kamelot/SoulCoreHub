#!/usr/bin/env python3
"""
SoulCoreHub Knowledge Processing System
---------------------------------------
This script processes various document types into knowledge chunks for RAG.
It handles PDF, DOCX, TXT, and other formats, parsing them into semantic chunks
that can be retrieved by SoulCoreHub agents during conversations.
"""

import os
import re
import json
import hashlib
import argparse
from typing import List, Dict, Any, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SoulCoreRAG")

try:
    from langchain_community.document_loaders import (
        PyPDFLoader, 
        Docx2txtLoader,
        TextLoader,
        UnstructuredMarkdownLoader,
        UnstructuredHTMLLoader
    )
    from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings
    import tiktoken
except ImportError:
    logger.error("Required packages not found. Installing dependencies...")
    import subprocess  # nosec B404
    import sys
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "langchain", "langchain_community", "langchain_openai", 
                       "tiktoken", "faiss-cpu", "pypdf", "docx2txt", "unstructured", "bs4"], 
                      shell=False, check=True, timeout=300)  # nosec B603
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        raise
    except subprocess.TimeoutExpired:
        logger.error("Package installation timed out")
        raise
    
    # Retry imports
    from langchain_community.document_loaders import (
        PyPDFLoader, 
        Docx2txtLoader,
        TextLoader,
        UnstructuredMarkdownLoader,
        UnstructuredHTMLLoader
    )
    from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings
    import tiktoken

# Constants
UPLOADS_DIR = os.path.expanduser("~/SoulCoreHub/rag_knowledge/uploads")
CHUNKS_DIR = os.path.expanduser("~/SoulCoreHub/rag_knowledge/chunks")
VECTOR_DB_PATH = os.path.expanduser("~/SoulCoreHub/rag_knowledge/vector_db")
METADATA_PATH = os.path.expanduser("~/SoulCoreHub/rag_knowledge/metadata.json")

# Ensure directories exist
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(CHUNKS_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_PATH, exist_ok=True)

class DocumentProcessor:
    """Handles the processing of various document types into knowledge chunks."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load existing metadata or create new if not exists."""
        if os.path.exists(METADATA_PATH):
            with open(METADATA_PATH, 'r') as f:
                return json.load(f)
        return {"processed_files": {}, "chunk_count": 0}
    
    def _save_metadata(self):
        """Save metadata to disk."""
        with open(METADATA_PATH, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _get_file_hash(self, filepath: str) -> str:
        """Generate a hash for a file to track changes."""
        hasher = hashlib.md5(usedforsecurity=False)
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    
    def _get_loader(self, filepath: str):
        """Select appropriate document loader based on file extension."""
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.pdf':
            return PyPDFLoader(filepath)
        elif ext == '.docx':
            return Docx2txtLoader(filepath)
        elif ext == '.md':
            return UnstructuredMarkdownLoader(filepath)
        elif ext == '.html' or ext == '.htm':
            return UnstructuredHTMLLoader(filepath)
        elif ext == '.txt' or ext in ['.py', '.js', '.java', '.c', '.cpp', '.cs', '.rb']:
            return TextLoader(filepath)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _get_splitter(self, filepath: str):
        """Select appropriate text splitter based on file content and type."""
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.md':
            return MarkdownTextSplitter(chunk_size=1000, chunk_overlap=200)
        else:
            # Default recursive splitter with smart defaults
            return RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
    
    def process_file(self, filepath: str) -> Tuple[int, str]:
        """
        Process a single file into chunks and store in vector database.
        
        Args:
            filepath: Path to the file to process
            
        Returns:
            Tuple of (number of chunks created, file_id)
        """
        file_hash = self._get_file_hash(filepath)
        file_id = os.path.basename(filepath)
        
        # Check if file already processed and unchanged
        if file_id in self.metadata["processed_files"] and self.metadata["processed_files"][file_id]["hash"] == file_hash:
            logger.info(f"File {file_id} already processed and unchanged. Skipping.")
            return 0, file_id
        
        try:
            # Load document
            loader = self._get_loader(filepath)
            documents = loader.load()
            
            # Split text
            text_splitter = self._get_splitter(filepath)
            chunks = text_splitter.split_documents(documents)
            
            # Save chunks to files
            chunk_ids = []
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_id}_{i}"
                chunk_path = os.path.join(CHUNKS_DIR, f"{chunk_id}.json")
                
                # Store chunk with metadata
                chunk_data = {
                    "text": chunk.page_content,
                    "metadata": {
                        "source": file_id,
                        "chunk_id": chunk_id,
                        "page": chunk.metadata.get("page", None),
                        **chunk.metadata
                    }
                }
                
                with open(chunk_path, 'w') as f:
                    json.dump(chunk_data, f, indent=2)
                
                chunk_ids.append(chunk_id)
            
            # Store in vector database
            vector_store = FAISS.from_documents(chunks, self.embeddings)
            vector_store.save_local(os.path.join(VECTOR_DB_PATH, file_id))
            
            # Update metadata
            self.metadata["processed_files"][file_id] = {
                "hash": file_hash,
                "chunks": chunk_ids,
                "chunk_count": len(chunks),
                "path": filepath
            }
            self.metadata["chunk_count"] += len(chunks)
            self._save_metadata()
            
            logger.info(f"Processed {file_id}: Created {len(chunks)} chunks")
            return len(chunks), file_id
            
        except Exception as e:
            logger.error(f"Error processing {filepath}: {str(e)}")
            return 0, file_id
    
    def process_directory(self, directory: str = UPLOADS_DIR) -> Dict[str, int]:
        """
        Process all files in a directory.
        
        Args:
            directory: Directory containing files to process
            
        Returns:
            Dictionary mapping file IDs to number of chunks created
        """
        results = {}
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                try:
                    num_chunks, file_id = self.process_file(filepath)
                    results[file_id] = num_chunks
                except ValueError as e:
                    logger.warning(str(e))
        
        return results
    
    def query_knowledge(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Query the knowledge base for relevant chunks.
        
        Args:
            query: The query string
            top_k: Number of results to return
            
        Returns:
            List of relevant chunks with their metadata
        """
        # Combine all vector stores
        all_vector_stores = []
        for file_id in self.metadata["processed_files"]:
            vector_store_path = os.path.join(VECTOR_DB_PATH, file_id)
            if os.path.exists(vector_store_path):
                try:
                    vs = FAISS.load_local(vector_store_path, self.embeddings)
                    all_vector_stores.append(vs)
                except Exception as e:
                    logger.error(f"Error loading vector store for {file_id}: {str(e)}")
        
        if not all_vector_stores:
            return []
        
        # Merge vector stores if multiple exist
        if len(all_vector_stores) > 1:
            main_vs = all_vector_stores[0]
            for vs in all_vector_stores[1:]:
                main_vs.merge_from(vs)
            vector_store = main_vs
        else:
            vector_store = all_vector_stores[0]
        
        # Query the vector store
        results = vector_store.similarity_search_with_score(query, k=top_k)
        
        # Format results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "text": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": float(score)
            })
        
        return formatted_results

def main():
    parser = argparse.ArgumentParser(description="SoulCoreHub Knowledge Processing System")
    parser.add_argument("--process", action="store_true", help="Process all files in the uploads directory")
    parser.add_argument("--file", type=str, help="Process a specific file")
    parser.add_argument("--query", type=str, help="Query the knowledge base")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return for query")
    
    args = parser.parse_args()
    processor = DocumentProcessor()
    
    if args.process:
        results = processor.process_directory()
        print(f"Processed {len(results)} files, created {sum(results.values())} chunks")
    
    elif args.file:
        if os.path.exists(args.file):
            num_chunks, file_id = processor.process_file(args.file)
            print(f"Processed {file_id}: Created {num_chunks} chunks")
        else:
            print(f"File not found: {args.file}")
    
    elif args.query:
        results = processor.query_knowledge(args.query, args.top_k)
        print(f"Found {len(results)} relevant chunks:")
        for i, result in enumerate(results):
            print(f"\n--- Result {i+1} (Score: {result['relevance_score']:.4f}) ---")
            print(f"Source: {result['metadata'].get('source', 'Unknown')}")
            print(f"Text: {result['text'][:200]}...")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
