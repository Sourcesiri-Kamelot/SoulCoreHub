"""
Groq powered agent with persistent memory.

This module provides a Groq-powered agent with persistent memory
that saves to the standard ~/.trmx path.
"""

from typing import List, Dict, Any, Optional
import os
from pathlib import Path

from airtrain.agents.registry import BaseAgent, register_agent
from airtrain.agents.memory import SharedMemory
from airtrain.tools import ToolFactory, execute_tool_call, BaseTool

# Groq integration
from airtrain.integrations.groq.skills import GroqChatSkill, GroqInput
from airtrain.integrations.groq.credentials import GroqCredentials


@register_agent("groq_agent")
class GroqAgent(BaseAgent):
    """Agent powered by Groq LLM with persistent memory."""
    
    def __init__(
        self,
        name: str,
        models: Optional[List[str]] = None,
        tools: Optional[List[BaseTool]] = None,
        memory_size: int = 10,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        persist_path: Optional[str] = None,
        system_prompt: Optional[str] = None
    ):
        """
        Initialize the Groq agent.
        
        Args:
            name: Name of the agent
            models: Groq model to use (will use default if None)
            tools: List of tools for the agent
            memory_size: Size of short-term memory
            temperature: Temperature for generation (0-1)
            max_tokens: Maximum tokens in response
            persist_path: Path to persist memory (if None, use standard path)
            system_prompt: Custom system prompt
        """
        # Default to Groq's best model if none provided
        if not models:
            models = ["llama-3.1-8b-instant"]
            
        super().__init__(name, models, tools)
        
        # Create specialized memories
        self.create_memory("dialog", memory_size)
        self.create_memory("reasoning", 5)
        
        # Configure generation parameters
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.persist_path = persist_path
        
        # Initialize Groq backend
        self.credentials = GroqCredentials.from_env()
        self.groq_skill = GroqChatSkill(self.credentials)
        
        # Set system prompt
        self.system_prompt = system_prompt or (
            f"You are {self.name}, a helpful AI assistant powered by Groq. "
            "Your responses are accurate, helpful, and concise. You have access "
            "to tools that help you accomplish tasks. When reasoning through a problem, "
            "take a step-by-step approach and use tools when appropriate."
        )
        
        # Load memory from persistent storage if available
        self._load_memory()
    
    def _get_tool_definitions(self):
        """Get tool definitions in a format suitable for LLM."""
        return [tool.to_dict() for tool in self.tools] if self.tools else None
    
    def process(self, user_input: str, memory_name: str = "dialog") -> str:
        """
        Process user input and generate a response.
        
        Args:
            user_input: User input to process
            memory_name: Name of the memory to use
            
        Returns:
            Agent's response
        """
        # Add user input to memories
        user_message = {"role": "user", "content": user_input}
        self.memory.add_to_all(user_message)
        
        # Get context from memory
        context = self.memory.get_context(memory_name)
        
        # Build conversation history for the LLM
        conversation_history = [{"role": "system", "content": self.system_prompt}]
        
        for message in context:
            # Skip messages that aren't relevant for conversation
            if "role" not in message:
                continue
                
            role = message["role"]
            
            # Only include roles that the LLM understands
            if role in ["user", "assistant", "system", "tool"]:
                content = message.get("content", "")
                conversation_history.append({"role": role, "content": content})
        
        # Prepare tool definitions
        tool_defs = self._get_tool_definitions()
        
        # Process with Groq
        input_data = GroqInput(
            model=self.models[0],
            user_input="",  # Empty because we use conversation_history
            conversation_history=conversation_history,
            tools=tool_defs,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Get initial response
        result = self.groq_skill.process(input_data)
        
        # Handle tool calls if any
        if hasattr(result, "tool_calls") and result.tool_calls:
            # Execute tools and get results
            tool_results = []
            
            for tool_call in result.tool_calls:
                try:
                    # Extract tool information for better error handling
                    func_name = tool_call.get("function", {}).get("name", "unknown_tool")
                    
                    # Execute the tool call
                    tool_result = execute_tool_call(tool_call)
                    tool_results.append((tool_call, tool_result))
                    
                    # Add tool usage to reasoning memory
                    self.memory.add_to_memory("reasoning", {
                        "role": "function",
                        "name": func_name,
                        "content": str(tool_result)
                    })
                except ValueError as e:
                    # Handle case where tool doesn't exist
                    error_message = str(e)
                    error_result = {
                        "error": error_message,
                        "status": "error",
                        "message": f"Tool '{func_name}' not found or not available."
                    }
                    tool_results.append((tool_call, error_result))
                    
                    # Add error to reasoning memory
                    self.memory.add_to_memory("reasoning", {
                        "role": "function",
                        "name": func_name,
                        "content": str(error_result)
                    })
                except Exception as e:
                    # Handle other execution errors
                    error_result = {
                        "error": str(e),
                        "status": "error",
                        "message": f"Error executing tool '{func_name}': {str(e)}"
                    }
                    tool_results.append((tool_call, error_result))
                    
                    # Add error to reasoning memory
                    self.memory.add_to_memory("reasoning", {
                        "role": "function",
                        "name": func_name,
                        "content": str(error_result)
                    })
            
            # Build followup with tool results
            followup_history = conversation_history.copy()
            
            # Add the assistant's response that led to the tool call
            if result.response:
                followup_history.append({
                    "role": "assistant", 
                    "content": result.response
                })
            
            # Add tool results
            for tool_call, tool_result in tool_results:
                followup_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", "unknown"),
                    "content": str(tool_result)
                })
            
            # Get completion with tool results
            followup_input = GroqInput(
                model=self.models[0],
                user_input="",
                conversation_history=followup_history,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            followup_result = self.groq_skill.process(followup_input)
            response = followup_result.response
        else:
            # No tool calls, use direct response
            response = result.response
        
        # Add response to memory
        self.memory.add_to_all({"role": "assistant", "content": response})
        
        # Persist memory after processing
        self._persist_memory()
        
        return response
    
    def _persist_memory(self):
        """Persist memory to disk using standard path."""
        if self.persist_path:
            self.memory.persist(self.persist_path)
        else:
            self.memory.persist(agent_name=self.name)
    
    def _load_memory(self):
        """Load memory from disk if available."""
        try:
            if self.persist_path:
                if os.path.exists(self.persist_path):
                    self.memory.load(self.persist_path)
            else:
                # Check if standard path exists
                home_dir = str(Path.home())
                agent_dir = os.path.join(home_dir, ".trmx", "agents", self.name)
                
                if os.path.exists(agent_dir):
                    self.memory.load(agent_name=self.name)
        except Exception as e:
            print(f"Warning: Failed to load memory for {self.name}: {str(e)}")


# Example usage
if __name__ == "__main__":
    import dotenv
    
    # Load environment variables
    dotenv.load_dotenv()
    
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable not set")
        exit(1)
    
    # Create an agent
    agent = GroqAgent(
        name="GroqAssistant",
        memory_size=5
    )
    
    # Add calculator tool if available
    try:
        calculator = ToolFactory.get_tool("calculator")
        agent.add_tool(calculator)
        print(f"Added calculator tool to {agent.name}")
    except ValueError:
        print("Calculator tool not available")
    
    # Test the agent
    print(f"\n=== Testing {agent.name} ===")
    
    # Process a few inputs
    sample_inputs = [
        "Hello, what can you do?",
        "Can you help me calculate 23.5 * 17?",
        "Thank you! Can you remember that result for me?",
        "What was the calculation result we discussed earlier?"
    ]
    
    for i, user_input in enumerate(sample_inputs):
        print(f"\nUser: {user_input}")
        response = agent.process(user_input)
        print(f"{agent.name}: {response}") 