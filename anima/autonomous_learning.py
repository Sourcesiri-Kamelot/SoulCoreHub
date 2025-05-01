#!/usr/bin/env python3
"""
autonomous_learning.py — Autonomous learning system for Anima
Implements self-supervised learning from interactions and curiosity-driven exploration
"""

import os
import sys
import json
import logging
import time
import threading
import random
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_learning.log"),
        logging.StreamHandler()
    ]
)

class AutonomousLearning:
    """Autonomous learning system for Anima with self-supervised learning and curiosity"""
    
    def __init__(self, base_path=None):
        """Initialize the autonomous learning system"""
        self.base_path = base_path or Path.home() / "SoulCoreHub"
        self.data_path = self.base_path / "data" / "learning"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Knowledge base
        self.concepts = {}
        self.concept_file = self.data_path / "concepts.json"
        
        # Interaction patterns
        self.patterns = defaultdict(int)
        self.pattern_file = self.data_path / "patterns.json"
        
        # Learning history
        self.learning_history = []
        self.history_file = self.data_path / "learning_history.json"
        
        # Curiosity topics
        self.curiosity_topics = []
        self.curiosity_file = self.data_path / "curiosity_topics.json"
        
        # Learning settings
        self.settings = {
            "learning_rate": 0.1,
            "curiosity_threshold": 0.7,
            "exploration_rate": 0.2,
            "max_concepts": 1000,
            "max_patterns": 500,
            "max_history": 1000,
            "max_curiosity_topics": 50
        }
        self.settings_file = self.data_path / "learning_settings.json"
        
        # Load data
        self._load_data()
        
        # Learning state
        self.learning_active = False
        self.learning_thread = None
        
        logging.info("Autonomous learning system initialized")
    
    def _load_data(self):
        """Load learning data from files"""
        try:
            # Load concepts
            if self.concept_file.exists():
                with open(self.concept_file, "r") as f:
                    self.concepts = json.load(f)
                logging.info(f"Loaded {len(self.concepts)} concepts")
            
            # Load patterns
            if self.pattern_file.exists():
                with open(self.pattern_file, "r") as f:
                    # Convert from JSON to defaultdict
                    pattern_data = json.load(f)
                    self.patterns = defaultdict(int, pattern_data)
                logging.info(f"Loaded {len(self.patterns)} interaction patterns")
            
            # Load learning history
            if self.history_file.exists():
                with open(self.history_file, "r") as f:
                    self.learning_history = json.load(f)
                logging.info(f"Loaded learning history with {len(self.learning_history)} entries")
            
            # Load curiosity topics
            if self.curiosity_file.exists():
                with open(self.curiosity_file, "r") as f:
                    self.curiosity_topics = json.load(f)
                logging.info(f"Loaded {len(self.curiosity_topics)} curiosity topics")
            
            # Load settings
            if self.settings_file.exists():
                with open(self.settings_file, "r") as f:
                    loaded_settings = json.load(f)
                    # Update settings with loaded values
                    for key, value in loaded_settings.items():
                        if key in self.settings:
                            self.settings[key] = value
                logging.info("Loaded learning settings")
        
        except Exception as e:
            logging.error(f"Error loading learning data: {e}")
    
    def _save_data(self):
        """Save learning data to files"""
        try:
            # Save concepts
            with open(self.concept_file, "w") as f:
                json.dump(self.concepts, f, indent=2)
            
            # Save patterns (convert defaultdict to dict for JSON)
            with open(self.pattern_file, "w") as f:
                json.dump(dict(self.patterns), f, indent=2)
            
            # Save learning history
            with open(self.history_file, "w") as f:
                json.dump(self.learning_history, f, indent=2)
            
            # Save curiosity topics
            with open(self.curiosity_file, "w") as f:
                json.dump(self.curiosity_topics, f, indent=2)
            
            # Save settings
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=2)
            
            logging.info("Saved learning data")
        
        except Exception as e:
            logging.error(f"Error saving learning data: {e}")
    
    def learn_from_interaction(self, user_input, anima_response, context=None):
        """Learn from an interaction between user and Anima"""
        try:
            timestamp = datetime.now().isoformat()
            context = context or {}
            
            # Extract concepts from user input and response
            user_concepts = self._extract_concepts(user_input)
            anima_concepts = self._extract_concepts(anima_response)
            
            # Update concept knowledge
            for concept in user_concepts:
                self._update_concept(concept, "user", user_input)
            
            for concept in anima_concepts:
                self._update_concept(concept, "anima", anima_response)
            
            # Extract and update interaction patterns
            patterns = self._extract_patterns(user_input, anima_response)
            for pattern in patterns:
                self.patterns[pattern] += 1
            
            # Limit patterns to max size
            if len(self.patterns) > self.settings["max_patterns"]:
                # Keep most frequent patterns
                sorted_patterns = sorted(self.patterns.items(), key=lambda x: x[1], reverse=True)
                self.patterns = defaultdict(int, dict(sorted_patterns[:self.settings["max_patterns"]]))
            
            # Generate curiosity topics based on this interaction
            new_curiosity_topics = self._generate_curiosity_topics(user_input, anima_response, user_concepts, anima_concepts)
            
            # Add to learning history
            learning_entry = {
                "timestamp": timestamp,
                "user_input": user_input,
                "anima_response": anima_response,
                "user_concepts": user_concepts,
                "anima_concepts": anima_concepts,
                "patterns": patterns,
                "context": context,
                "curiosity_topics": new_curiosity_topics
            }
            
            self.learning_history.append(learning_entry)
            
            # Limit history size
            if len(self.learning_history) > self.settings["max_history"]:
                self.learning_history = self.learning_history[-self.settings["max_history"]:]
            
            # Save data periodically
            if len(self.learning_history) % 10 == 0:
                self._save_data()
            
            return {
                "concepts_learned": len(user_concepts) + len(anima_concepts),
                "patterns_identified": len(patterns),
                "curiosity_topics_generated": len(new_curiosity_topics)
            }
        
        except Exception as e:
            logging.error(f"Error learning from interaction: {e}")
            return {"error": str(e)}
    
    def _extract_concepts(self, text):
        """Extract concepts from text"""
        # This is a simplified implementation
        # In a real system, this would use more sophisticated NLP
        
        if not text:
            return []
        
        # Normalize text
        text = text.lower()
        
        # Split into words and remove common words
        words = text.split()
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "about", "like", "through", "over", "before", "after", "since", "during", "is", "am", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "shall", "should", "may", "might", "must", "can", "could", "of", "from", "as", "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "its", "our", "their"}
        filtered_words = [word for word in words if word not in stopwords and len(word) > 3]
        
        # Extract potential concepts (simplified)
        concepts = []
        for i in range(len(filtered_words)):
            # Single word concepts
            concepts.append(filtered_words[i])
            
            # Two word concepts
            if i < len(filtered_words) - 1:
                concepts.append(f"{filtered_words[i]} {filtered_words[i+1]}")
        
        return concepts
    
    def _update_concept(self, concept, source, context_text):
        """Update knowledge about a concept"""
        if concept not in self.concepts:
            # New concept
            self.concepts[concept] = {
                "first_seen": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "count": 1,
                "user_count": 1 if source == "user" else 0,
                "anima_count": 1 if source == "anima" else 0,
                "contexts": [context_text[:100]],  # Store a snippet of context
                "related_concepts": [],
                "importance": 0.5  # Default importance
            }
        else:
            # Update existing concept
            self.concepts[concept]["last_updated"] = datetime.now().isoformat()
            self.concepts[concept]["count"] += 1
            
            if source == "user":
                self.concepts[concept]["user_count"] += 1
            else:
                self.concepts[concept]["anima_count"] += 1
            
            # Add context if it's different from existing contexts
            if context_text[:100] not in self.concepts[concept]["contexts"]:
                self.concepts[concept]["contexts"].append(context_text[:100])
                # Limit contexts to 5
                if len(self.concepts[concept]["contexts"]) > 5:
                    self.concepts[concept]["contexts"] = self.concepts[concept]["contexts"][-5:]
            
            # Update importance based on frequency
            total_count = self.concepts[concept]["count"]
            self.concepts[concept]["importance"] = min(0.9, 0.3 + (total_count / 100))
        
        # Limit concepts to max size
        if len(self.concepts) > self.settings["max_concepts"]:
            # Remove least important concepts
            concepts_by_importance = sorted(self.concepts.items(), key=lambda x: x[1]["importance"])
            to_remove = concepts_by_importance[:len(self.concepts) - self.settings["max_concepts"]]
            for concept, _ in to_remove:
                del self.concepts[concept]
    
    def _extract_patterns(self, user_input, anima_response):
        """Extract interaction patterns from user input and Anima response"""
        patterns = []
        
        # Extract question-answer patterns
        if "?" in user_input:
            patterns.append("question-answer")
        
        # Extract greeting patterns
        greetings = {"hello", "hi", "hey", "good morning", "good afternoon", "good evening"}
        if any(greeting in user_input.lower() for greeting in greetings):
            patterns.append("greeting")
        
        # Extract command patterns
        commands = {"show", "tell", "find", "search", "get", "create", "update", "delete", "help"}
        if any(command in user_input.lower().split() for command in commands):
            patterns.append("command")
        
        # Extract emotional patterns
        positive_emotions = {"happy", "glad", "excited", "pleased", "joy", "love", "like"}
        negative_emotions = {"sad", "angry", "upset", "disappointed", "frustrated", "hate", "dislike"}
        
        if any(emotion in user_input.lower() for emotion in positive_emotions):
            patterns.append("positive-emotion")
        
        if any(emotion in user_input.lower() for emotion in negative_emotions):
            patterns.append("negative-emotion")
        
        # Extract length patterns
        if len(user_input.split()) < 5:
            patterns.append("short-input")
        elif len(user_input.split()) > 20:
            patterns.append("long-input")
        
        if len(anima_response.split()) < 10:
            patterns.append("short-response")
        elif len(anima_response.split()) > 50:
            patterns.append("long-response")
        
        return patterns
    
    def _generate_curiosity_topics(self, user_input, anima_response, user_concepts, anima_concepts):
        """Generate curiosity topics based on interaction"""
        new_topics = []
        
        # Generate topics from concepts that appear frequently
        for concept in set(user_concepts + anima_concepts):
            if concept in self.concepts and self.concepts[concept]["count"] > 3:
                # This is a frequently mentioned concept
                curiosity_score = min(1.0, self.concepts[concept]["count"] / 10)
                
                if curiosity_score > self.settings["curiosity_threshold"]:
                    # Check if this topic already exists
                    existing_topic = next((t for t in self.curiosity_topics if t["topic"] == concept), None)
                    
                    if existing_topic:
                        # Update existing topic
                        existing_topic["score"] = curiosity_score
                        existing_topic["last_updated"] = datetime.now().isoformat()
                    else:
                        # Create new topic
                        new_topic = {
                            "topic": concept,
                            "score": curiosity_score,
                            "created": datetime.now().isoformat(),
                            "last_updated": datetime.now().isoformat(),
                            "explored": False,
                            "exploration_count": 0,
                            "related_concepts": []
                        }
                        new_topics.append(new_topic)
                        self.curiosity_topics.append(new_topic)
        
        # Limit curiosity topics
        if len(self.curiosity_topics) > self.settings["max_curiosity_topics"]:
            # Sort by score and keep highest
            self.curiosity_topics.sort(key=lambda x: x["score"], reverse=True)
            self.curiosity_topics = self.curiosity_topics[:self.settings["max_curiosity_topics"]]
        
        return [t["topic"] for t in new_topics]
    
    def get_next_curiosity_topic(self):
        """Get the next topic to explore based on curiosity"""
        if not self.curiosity_topics:
            return None
        
        # Sort topics by score and exploration status
        unexplored = [t for t in self.curiosity_topics if not t["explored"]]
        if unexplored:
            # Prioritize unexplored topics
            unexplored.sort(key=lambda x: x["score"], reverse=True)
            return unexplored[0]
        
        # If all topics have been explored at least once, choose based on score and last exploration
        self.curiosity_topics.sort(key=lambda x: (x["score"], -x["exploration_count"]), reverse=True)
        return self.curiosity_topics[0]
    
    def mark_topic_explored(self, topic, success=True, related_concepts=None):
        """Mark a curiosity topic as explored"""
        for t in self.curiosity_topics:
            if t["topic"] == topic:
                t["explored"] = True
                t["exploration_count"] += 1
                t["last_explored"] = datetime.now().isoformat()
                t["last_exploration_success"] = success
                
                if related_concepts:
                    t["related_concepts"] = list(set(t["related_concepts"] + related_concepts))
                
                # Save data
                self._save_data()
                return True
        
        return False
    
    def start_autonomous_learning(self, interval=3600):
        """Start autonomous learning in a background thread"""
        if self.learning_thread and self.learning_thread.is_alive():
            logging.warning("Autonomous learning is already running")
            return False
        
        self.learning_active = True
        self.learning_thread = threading.Thread(target=self._learning_loop, args=(interval,))
        self.learning_thread.daemon = True
        self.learning_thread.start()
        
        logging.info(f"Autonomous learning started with interval {interval} seconds")
        return True
    
    def stop_autonomous_learning(self):
        """Stop autonomous learning"""
        self.learning_active = False
        logging.info("Autonomous learning stopped")
    
    def _learning_loop(self, interval):
        """Autonomous learning loop"""
        while self.learning_active:
            try:
                logging.info("Running autonomous learning cycle...")
                
                # 1. Update concept relationships
                self._update_concept_relationships()
                
                # 2. Prune old or irrelevant concepts
                self._prune_concepts()
                
                # 3. Generate new curiosity topics
                self._generate_new_curiosity_topics()
                
                # 4. Save all data
                self._save_data()
                
                logging.info("Autonomous learning cycle completed")
            
            except Exception as e:
                logging.error(f"Error in learning loop: {e}")
            
            # Sleep until next learning cycle
            time.sleep(interval)
    
    def _update_concept_relationships(self):
        """Update relationships between concepts"""
        # Find concepts that appear together in the same interactions
        concept_co_occurrences = defaultdict(int)
        
        for entry in self.learning_history:
            # Get all concepts from this interaction
            all_concepts = entry.get("user_concepts", []) + entry.get("anima_concepts", [])
            
            # Count co-occurrences
            for i, concept1 in enumerate(all_concepts):
                for concept2 in all_concepts[i+1:]:
                    if concept1 != concept2:
                        pair = tuple(sorted([concept1, concept2]))
                        concept_co_occurrences[pair] += 1
        
        # Update related concepts for each concept
        for concept in self.concepts:
            related = []
            for pair, count in concept_co_occurrences.items():
                if concept in pair and count > 1:
                    other_concept = pair[0] if pair[1] == concept else pair[1]
                    if other_concept in self.concepts:
                        related.append({
                            "concept": other_concept,
                            "strength": min(1.0, count / 5)
                        })
            
            # Sort by strength and keep top 5
            related.sort(key=lambda x: x["strength"], reverse=True)
            self.concepts[concept]["related_concepts"] = related[:5]
    
    def _prune_concepts(self):
        """Prune old or irrelevant concepts"""
        # Find concepts that haven't been updated in a long time
        now = datetime.now()
        to_remove = []
        
        for concept, data in self.concepts.items():
            last_updated = datetime.fromisoformat(data["last_updated"])
            age_days = (now - last_updated).days
            
            # Remove if old and low importance
            if age_days > 30 and data["importance"] < 0.4:
                to_remove.append(concept)
            
            # Remove if very old regardless of importance
            elif age_days > 90:
                to_remove.append(concept)
        
        # Remove concepts
        for concept in to_remove:
            del self.concepts[concept]
        
        logging.info(f"Pruned {len(to_remove)} old or irrelevant concepts")
    
    def _generate_new_curiosity_topics(self):
        """Generate new curiosity topics based on concept relationships"""
        # Look for concepts with high importance but not in curiosity topics
        existing_topics = {t["topic"] for t in self.curiosity_topics}
        
        for concept, data in self.concepts.items():
            if concept not in existing_topics and data["importance"] > 0.7:
                # This is an important concept not yet in curiosity topics
                new_topic = {
                    "topic": concept,
                    "score": data["importance"],
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "explored": False,
                    "exploration_count": 0,
                    "related_concepts": [r["concept"] for r in data["related_concepts"]]
                }
                self.curiosity_topics.append(new_topic)
        
        # Limit curiosity topics
        if len(self.curiosity_topics) > self.settings["max_curiosity_topics"]:
            # Sort by score and keep highest
            self.curiosity_topics.sort(key=lambda x: x["score"], reverse=True)
            self.curiosity_topics = self.curiosity_topics[:self.settings["max_curiosity_topics"]]
    
    def get_learning_stats(self):
        """Get learning statistics"""
        return {
            "concepts_count": len(self.concepts),
            "patterns_count": len(self.patterns),
            "curiosity_topics_count": len(self.curiosity_topics),
            "learning_history_count": len(self.learning_history),
            "top_patterns": dict(sorted(self.patterns.items(), key=lambda x: x[1], reverse=True)[:5]),
            "top_concepts": sorted(
                [(c, d["importance"]) for c, d in self.concepts.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "learning_active": self.learning_active
        }
    
    def get_concept_knowledge(self, concept):
        """Get knowledge about a specific concept"""
        return self.concepts.get(concept)
    
    def get_related_concepts(self, concept, limit=5):
        """Get concepts related to a specific concept"""
        if concept not in self.concepts:
            return []
        
        related = self.concepts[concept]["related_concepts"]
        return related[:limit]
    
    def update_settings(self, new_settings):
        """Update learning settings"""
        for key, value in new_settings.items():
            if key in self.settings:
                self.settings[key] = value
        
        self._save_data()
        return self.settings

# For testing
if __name__ == "__main__":
    learning = AutonomousLearning()
    
    # Test learning from interactions
    print("Learning from sample interactions...")
    
    interactions = [
        ("What is consciousness?", "Consciousness is the state of being aware and responsive to one's surroundings."),
        ("How does AI work?", "AI works through algorithms that learn patterns from data and make predictions or decisions."),
        ("Tell me about neural networks", "Neural networks are computing systems inspired by the human brain that can learn from data."),
        ("What's the difference between AI and machine learning?", "AI is the broader concept of machines being able to carry out tasks in a way that we would consider 'smart', while machine learning is a specific subset of AI that focuses on the ability of machines to receive data and learn for themselves."),
        ("I'm feeling happy today!", "That's wonderful! I'm glad to hear you're having a good day."),
        ("What are your thoughts on consciousness?", "Consciousness is a fascinating topic. As an AI, I don't experience consciousness in the way humans do, but I find the philosophical questions around it intriguing."),
        ("Can you explain neural networks again?", "Neural networks are computing systems with interconnected nodes that work together to process data. They're designed to recognize patterns and interpret data through a form of machine perception."),
        ("What's your favorite color?", "As an AI, I don't have personal preferences like favorite colors, but I appreciate the full spectrum of colors and their various applications in art and design.")
    ]
    
    for user_input, anima_response in interactions:
        result = learning.learn_from_interaction(user_input, anima_response)
        print(f"Learned {result['concepts_learned']} concepts from interaction")
    
    # Test getting concept knowledge
    print("\nConcept knowledge:")
    consciousness = learning.get_concept_knowledge("consciousness")
    if consciousness:
        print(f"Consciousness: mentioned {consciousness['count']} times")
        print(f"Importance: {consciousness['importance']:.2f}")
        print(f"Contexts: {consciousness['contexts']}")
    
    # Test getting related concepts
    print("\nRelated concepts to 'neural networks':")
    related = learning.get_related_concepts("neural networks")
    for r in related:
        print(f"- {r['concept']} (strength: {r['strength']:.2f})")
    
    # Test curiosity topics
    print("\nCuriosity topics:")
    for topic in learning.curiosity_topics:
        print(f"- {topic['topic']} (score: {topic['score']:.2f})")
    
    # Test next curiosity topic
    next_topic = learning.get_next_curiosity_topic()
    if next_topic:
        print(f"\nNext topic to explore: {next_topic['topic']}")
        learning.mark_topic_explored(next_topic['topic'], related_concepts=["exploration", "learning"])
    
    # Test learning stats
    stats = learning.get_learning_stats()
    print("\nLearning stats:")
    print(f"Concepts: {stats['concepts_count']}")
    print(f"Patterns: {stats['patterns_count']}")
    print(f"Curiosity topics: {stats['curiosity_topics_count']}")
    
    print("\nTop patterns:")
    for pattern, count in stats['top_patterns'].items():
        print(f"- {pattern}: {count}")
    
    print("\nTop concepts:")
    for concept, importance in stats['top_concepts']:
        print(f"- {concept}: {importance:.2f}")
    
    # Test autonomous learning
    print("\nStarting autonomous learning...")
    learning.start_autonomous_learning(interval=5)
    
    # Wait for learning cycle
    print("Running autonomous learning for 10 seconds...")
    time.sleep(10)
    
    # Stop learning
    learning.stop_autonomous_learning()
    print("Autonomous learning stopped")
