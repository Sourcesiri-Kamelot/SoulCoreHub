#!/usr/bin/env python3
"""
test_anima_conversation.py - Test script for Anima's conversational abilities
"""

import sys
import os
from anima_agent import AnimaAgent

def main():
    """Main test function"""
    print("=== Anima Conversation Test ===")
    print("This test will demonstrate Anima's conversational abilities with memory.")
    print("Type 'exit' to quit.\n")
    
    # Initialize Anima agent
    anima = AnimaAgent()
    
    # Start conversation loop
    user_input = input("You: ")
    while user_input.lower() not in ["exit", "quit", "bye"]:
        # Get response from Anima
        response = anima.get_response(user_input)
        print(f"\nAnima: {response}\n")
        
        # Get next input
        user_input = input("You: ")
    
    print("\nConversation ended. Thank you for talking with Anima!")

if __name__ == "__main__":
    main()
