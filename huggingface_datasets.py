#!/usr/bin/env python3
"""
SoulCoreHub Hugging Face Datasets Integration
--------------------------------------------
This module connects to Hugging Face's public datasets and makes them available
to SoulCoreHub agents for reference and learning.
"""

import os
import json
import logging
import tempfile
from typing import Dict, Any, List, Optional, Union
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HuggingFaceDatasets")

try:
    from datasets import load_dataset, Dataset, DatasetDict
    import pandas as pd
except ImportError:
    logger.error("Required packages not found. Installing dependencies...")
    import subprocess
    subprocess.run(["pip", "install", "datasets", "pandas", "huggingface_hub"])
    
    # Retry imports
    from datasets import load_dataset, Dataset, DatasetDict
    import pandas as pd

# Constants
CACHE_DIR = os.path.expanduser("~/SoulCoreHub/huggingface_cache")
DATASETS_CONFIG = {
    "awesome-chatgpt-prompts": {
        "repo_id": "fka/awesome-chatgpt-prompts",
        "description": "A collection of prompt examples to be used with ChatGPT",
        "split": "train"
    },
    "code-search-net": {
        "repo_id": "code_search_net",
        "description": "A collection of code snippets and their natural language descriptions",
        "split": "train",
        "subset": "python"  # Options: go, java, javascript, php, python, ruby
    },
    "web-coding-snippets": {
        "repo_id": "Sentdex/web-coding-snippets",
        "description": "A collection of HTML, CSS, and JavaScript snippets",
        "split": "train"
    },
    "github-code": {
        "repo_id": "codeparrot/github-code",
        "description": "A large collection of code from GitHub repositories",
        "split": "train",
        "subset": "python"  # Options: python, javascript, java, go, etc.
    },
    "codealpaca": {
        "repo_id": "sahil2801/CodeAlpaca-20k",
        "description": "A dataset of coding instructions and completions",
        "split": "train"
    }
}

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

class HuggingFaceDatasetManager:
    """
    Manages Hugging Face datasets for SoulCoreHub agents.
    Provides methods to load, query, and extract information from datasets.
    """
    
    def __init__(self):
        """Initialize the dataset manager."""
        self.datasets = {}
        self.dataset_info = {}
        self.loaded_datasets = set()
    
    def load_dataset(self, dataset_name: str) -> bool:
        """
        Load a dataset from Hugging Face.
        
        Args:
            dataset_name: Name of the dataset to load
            
        Returns:
            True if successful, False otherwise
        """
        if dataset_name not in DATASETS_CONFIG:
            logger.error(f"Dataset '{dataset_name}' not configured")
            return False
        
        if dataset_name in self.loaded_datasets:
            logger.info(f"Dataset '{dataset_name}' already loaded")
            return True
        
        config = DATASETS_CONFIG[dataset_name]
        
        try:
            logger.info(f"Loading dataset '{dataset_name}' from {config['repo_id']}")
            
            # Load the dataset
            if "subset" in config:
                dataset = load_dataset(
                    config["repo_id"],
                    name=config["subset"],
                    split=config["split"],
                    cache_dir=CACHE_DIR
                )
            else:
                dataset = load_dataset(
                    config["repo_id"],
                    split=config["split"],
                    cache_dir=CACHE_DIR
                )
            
            # Store the dataset
            self.datasets[dataset_name] = dataset
            self.loaded_datasets.add(dataset_name)
            
            # Extract and store dataset info
            self.dataset_info[dataset_name] = {
                "name": dataset_name,
                "description": config["description"],
                "size": len(dataset),
                "columns": dataset.column_names,
                "example": dataset[0] if len(dataset) > 0 else None
            }
            
            logger.info(f"Successfully loaded dataset '{dataset_name}' with {len(dataset)} examples")
            return True
        
        except Exception as e:
            logger.error(f"Error loading dataset '{dataset_name}': {str(e)}")
            return False
    
    def load_all_datasets(self) -> Dict[str, bool]:
        """
        Load all configured datasets.
        
        Returns:
            Dictionary mapping dataset names to load success status
        """
        results = {}
        
        for dataset_name in DATASETS_CONFIG:
            results[dataset_name] = self.load_dataset(dataset_name)
        
        return results
    
    def get_dataset_info(self, dataset_name: str = None) -> Dict[str, Any]:
        """
        Get information about loaded datasets.
        
        Args:
            dataset_name: Optional name of a specific dataset
            
        Returns:
            Dictionary with dataset information
        """
        if dataset_name:
            if dataset_name in self.dataset_info:
                return self.dataset_info[dataset_name]
            else:
                return {"error": f"Dataset '{dataset_name}' not loaded"}
        
        return {
            "loaded_datasets": list(self.loaded_datasets),
            "available_datasets": list(DATASETS_CONFIG.keys()),
            "dataset_info": self.dataset_info
        }
    
    def search_dataset(self, dataset_name: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for entries in a dataset that match the query.
        
        Args:
            dataset_name: Name of the dataset to search
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching entries
        """
        if dataset_name not in self.loaded_datasets:
            if not self.load_dataset(dataset_name):
                return [{"error": f"Could not load dataset '{dataset_name}'"}]
        
        dataset = self.datasets[dataset_name]
        query_lower = query.lower()
        results = []
        
        # Convert to pandas for easier filtering
        df = pd.DataFrame(dataset)
        
        # Search through text columns
        text_columns = [col for col in df.columns if df[col].dtype == 'object']
        
        for _, row in df.iterrows():
            for col in text_columns:
                if isinstance(row[col], str) and query_lower in row[col].lower():
                    results.append(dict(row))
                    break
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_examples(self, dataset_name: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get random examples from a dataset.
        
        Args:
            dataset_name: Name of the dataset
            count: Number of examples to return
            
        Returns:
            List of example entries
        """
        if dataset_name not in self.loaded_datasets:
            if not self.load_dataset(dataset_name):
                return [{"error": f"Could not load dataset '{dataset_name}'"}]
        
        dataset = self.datasets[dataset_name]
        
        # Get random examples
        import random
        indices = random.sample(range(len(dataset)), min(count, len(dataset)))
        examples = [dict(dataset[i]) for i in indices]
        
        return examples
    
    def extract_knowledge(self, dataset_name: str, topic: str) -> Dict[str, Any]:
        """
        Extract knowledge about a specific topic from a dataset.
        
        Args:
            dataset_name: Name of the dataset
            topic: Topic to extract knowledge about
            
        Returns:
            Dictionary with extracted knowledge
        """
        if dataset_name not in self.loaded_datasets:
            if not self.load_dataset(dataset_name):
                return {"error": f"Could not load dataset '{dataset_name}'"}
        
        # Search for relevant entries
        results = self.search_dataset(dataset_name, topic, limit=10)
        
        # Extract knowledge based on dataset type
        if dataset_name == "awesome-chatgpt-prompts":
            prompts = [r.get("prompt", "") for r in results if "prompt" in r]
            return {
                "topic": topic,
                "dataset": dataset_name,
                "prompt_count": len(prompts),
                "prompts": prompts
            }
        
        elif dataset_name == "code-search-net" or dataset_name == "github-code":
            code_snippets = [r.get("code", "") for r in results if "code" in r]
            return {
                "topic": topic,
                "dataset": dataset_name,
                "snippet_count": len(code_snippets),
                "code_snippets": code_snippets
            }
        
        # Generic extraction for other datasets
        return {
            "topic": topic,
            "dataset": dataset_name,
            "result_count": len(results),
            "results": results
        }
    
    def save_to_knowledge_base(self, dataset_name: str, topic: str) -> str:
        """
        Save dataset knowledge to the RAG knowledge base.
        
        Args:
            dataset_name: Name of the dataset
            topic: Topic to extract and save
            
        Returns:
            Path to the saved file
        """
        if dataset_name not in self.loaded_datasets:
            if not self.load_dataset(dataset_name):
                return f"Error: Could not load dataset '{dataset_name}'"
        
        # Extract knowledge
        knowledge = self.extract_knowledge(dataset_name, topic)
        
        # Create a file in the uploads directory
        uploads_dir = os.path.expanduser("~/SoulCoreHub/rag_knowledge/uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        
        filename = f"{dataset_name}_{topic.replace(' ', '_')}.json"
        filepath = os.path.join(uploads_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(knowledge, f, indent=2)
        
        logger.info(f"Saved knowledge from '{dataset_name}' about '{topic}' to {filepath}")
        return filepath

def main():
    """Main function for testing the Hugging Face dataset manager."""
    manager = HuggingFaceDatasetManager()
    
    # Load a dataset
    dataset_name = "awesome-chatgpt-prompts"
    if manager.load_dataset(dataset_name):
        print(f"Successfully loaded {dataset_name}")
        
        # Get dataset info
        info = manager.get_dataset_info(dataset_name)
        print(f"Dataset info: {json.dumps(info, indent=2)}")
        
        # Search the dataset
        results = manager.search_dataset(dataset_name, "code", limit=2)
        print(f"Search results: {json.dumps(results, indent=2)}")
        
        # Get examples
        examples = manager.get_examples(dataset_name, count=2)
        print(f"Examples: {json.dumps(examples, indent=2)}")
        
        # Extract knowledge
        knowledge = manager.extract_knowledge(dataset_name, "programming")
        print(f"Knowledge: {json.dumps(knowledge, indent=2)}")
        
        # Save to knowledge base
        filepath = manager.save_to_knowledge_base(dataset_name, "programming")
        print(f"Saved to: {filepath}")

if __name__ == "__main__":
    main()
