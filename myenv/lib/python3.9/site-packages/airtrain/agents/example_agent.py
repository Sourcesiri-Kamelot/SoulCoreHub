"""
Example Agent implementation for AirTrain.

This module provides a simple example agent that demonstrates the use of
the AirTrain agent framework with memory and tool integration.
"""

from typing import List, Any, Optional

from airtrain.agents.registry import BaseAgent, register_agent
from airtrain.agents.memory import SharedMemory
from airtrain.tools import ToolFactory, execute_tool_call

try:
    from airtrain.integrations.groq.skills import GroqChatSkill, GroqInput
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

try:
    from airtrain.integrations.fireworks.skills import (
        FireworksChatSkill, 
        FireworksInput
    )
    HAS_FIREWORKS = True
except ImportError:
    HAS_FIREWORKS = False


@register_agent("conversation_agent")
class ConversationAgent(BaseAgent):
    """Agent specialized for conversation with memory management."""
    
    def __init__(
        self,
        name: str,
        models: Optional[List[str]] = None, 
        tools: Optional[List[Any]] = None,
        memory_size: int = 10,
        temperature: float = 0.2,
        max_tokens: int = 1024
    ):
        """
        Initialize conversation agent.
        
        Args:
            name: Name of the agent
            models: List of model identifiers
            tools: List of tools for the agent
            memory_size: Size of the conversation memory
            temperature: Temperature for generation
            max_tokens: Maximum tokens for responses
        """
        super().__init__(name, models, tools)
        
        # Create specialized memories
        self.create_memory("dialog", memory_size)
        self.create_memory("reasoning", 5)  # Shorter context for reasoning
        
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize model backends
        self._initialize_backends()
    
    def _initialize_backends(self):
        """Initialize available LLM backends based on installed integrations."""
        self.backends = {}
        
        if HAS_GROQ:
            self.backends["groq"] = GroqChatSkill()
        
        if HAS_FIREWORKS:
            self.backends["fireworks"] = FireworksChatSkill()
        
        if not self.backends:
            raise ImportError(
                "No LLM backend available. Please install at least one of: "
                "airtrain-groq, airtrain-fireworks"
            )
    
    def _get_backend_for_model(self, model: str):
        """Get the appropriate backend for a model."""
        if model.startswith("llama-") or model.endswith("-groq"):
            return self.backends.get("groq")
        elif "fireworks" in model:
            return self.backends.get("fireworks")
        
        # Default to first available backend
        return next(iter(self.backends.values()))
    
    def _get_tool_definitions(self):
        """Get tool definitions for LLM function calling."""
        return [tool.to_dict() for tool in self.tools]
    
    def process(self, user_input: str, memory_name: str = "dialog") -> str:
        """
        Process user input and generate a response.
        
        Args:
            user_input: User input to process
            memory_name: Name of the memory to use
            
        Returns:
            Agent's response
        """
        if not self.models:
            raise ValueError("No models configured for agent")
        
        # 1. Add user input to memories
        user_message = {"role": "user", "content": user_input}
        self.memory.add_to_all(user_message)
        
        # 2. Get context from memory
        context = self.memory.get_context(memory_name)
        
        # 3. Prepare conversation history
        conversation_history = []
        for message in context:
            # Skip messages that aren't relevant to the conversation
            if "role" not in message:
                continue
                
            # Convert to format expected by LLM
            if message["role"] in ["user", "assistant", "system"]:
                conversation_history.append({
                    "role": message["role"],
                    "content": message.get("content", "")
                })
        
        # Add system message if none present
        if not any(msg["role"] == "system" for msg in conversation_history):
            conversation_history.insert(0, {
                "role": "system",
                "content": (
                    f"You are {self.name}, a helpful AI assistant. "
                    "Provide accurate and concise responses."
                )
            })
        
        # 4. Prepare tool definitions
        tool_defs = self._get_tool_definitions() if self.tools else None
        
        # 5. Call primary model
        primary_model = self.models[0]
        backend = self._get_backend_for_model(primary_model)
        
        if "groq" in str(backend.__class__.__name__).lower():
            # Groq backend
            input_data = GroqInput(
                model=primary_model,
                conversation_history=conversation_history,
                tools=tool_defs,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        elif "fireworks" in str(backend.__class__.__name__).lower():
            # Fireworks backend
            input_data = FireworksInput(
                model=primary_model,
                conversation_history=conversation_history,
                tools=tool_defs,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        else:
            raise ValueError(f"Unsupported backend for model: {primary_model}")
        
        # Process the request
        result = backend.process(input_data)
        
        # 6. Handle tool calls if any
        if hasattr(result, "tool_calls") and result.tool_calls:
            # We have tool calls - execute them and get results
            tool_results = []
            
            for tool_call in result.tool_calls:
                # Execute the tool call
                tool_result = execute_tool_call(tool_call)
                tool_results.append((tool_call, tool_result))
                
                # Add to reasoning memory
                self.memory.add_to_memory("reasoning", {
                    "role": "function",
                    "name": tool_call.get("function", {}).get("name"),
                    "content": str(tool_result)
                })
            
            # Create followup with tool results
            followup_messages = conversation_history.copy()
            
            # Add the assistant's response that led to tool calls
            if result.response:
                followup_messages.append({
                    "role": "assistant",
                    "content": result.response
                })
            
            # Add tool results
            for tool_call, tool_result in tool_results:
                followup_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", "unknown"),
                    "content": str(tool_result)
                })
            
            # Get completion with tool results
            if "groq" in str(backend.__class__.__name__).lower():
                followup_input = GroqInput(
                    model=primary_model,
                    conversation_history=followup_messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            else:
                followup_input = FireworksInput(
                    model=primary_model,
                    conversation_history=followup_messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            
            followup_result = backend.process(followup_input)
            response = followup_result.response
        else:
            # No tool calls, just use the direct response
            response = result.response
        
        # 7. Add response to memory
        self.memory.add_to_all({"role": "assistant", "content": response})
        
        # 8. Return final response
        return response


def create_agent_team(shared_memory_name: str = "team_knowledge"):
    """
    Create a team of agents that share memory.
    
    Args:
        shared_memory_name: Name for the shared memory
        
    Returns:
        Tuple of agent instances
    """
    # Create shared memory
    shared_memory = SharedMemory(shared_memory_name)
    
    # Get tools from tool registry
    calculator_tool = None
    memory_tool = None
    
    try:
        calculator_tool = ToolFactory.get_tool("calculator")
    except ValueError:
        pass
        
    try:
        memory_tool = ToolFactory.get_tool("conversation_memory", "stateful")
    except ValueError:
        pass
    
    # Determine available models
    groq_model = "llama-3.1-8b-instant" if HAS_GROQ else None
    fireworks_model = None
    if HAS_FIREWORKS:
        fireworks_model = "accounts/fireworks/models/firefunction-v1"
    
    # Create agents
    agents = []
    
    if groq_model:
        # Create Groq-based agent
        agent1 = ConversationAgent(
            name="GroqAgent",
            models=[groq_model],
            tools=[calculator_tool] if calculator_tool else []
        )
        agent1.memory.add_shared_memory(shared_memory)
        agents.append(agent1)
    
    if fireworks_model:
        # Create Fireworks-based agent
        agent2 = ConversationAgent(
            name="FireworksAgent",
            models=[fireworks_model],
            tools=[memory_tool] if memory_tool else []
        )
        agent2.memory.add_shared_memory(shared_memory)
        agents.append(agent2)
    
    # Return the created agents
    return tuple(agents)


# Example usage
if __name__ == "__main__":
    import os
    import dotenv
    
    # Load environment variables for API keys
    dotenv.load_dotenv()
    
    if not (os.getenv("GROQ_API_KEY") or os.getenv("FIREWORKS_API_KEY")):
        print("No API keys found. Set GROQ_API_KEY or FIREWORKS_API_KEY in .env file.")
        exit(1)
    
    # Create an agent
    try:
        # Set model based on available backend
        groq_model = "llama-3.1-8b-instant"
        fw_model = "accounts/fireworks/models/firefunction-v1"
        model = groq_model if HAS_GROQ else fw_model
        
        agent = ConversationAgent(
            name="TestAgent",
            models=[model],
            memory_size=5
        )
        
        # Add calculator tool if available
        try:
            calculator = ToolFactory.get_tool("calculator")
            agent.add_tool(calculator)
            print(f"Added calculator tool to {agent.name}")
        except ValueError:
            pass
            
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
    
    except ImportError as e:
        print(f"Error creating agent: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}") 