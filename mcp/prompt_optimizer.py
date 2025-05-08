"""
Prompt Optimizer for SoulCoreHub
Implements prompt chaining and optimization techniques
"""

import json
import logging
import re
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptTemplate:
    """A template for generating prompts"""
    
    def __init__(self, template: str, variables: List[str] = None):
        """
        Initialize a prompt template
        
        Args:
            template: The template string with placeholders like {variable}
            variables: List of variable names in the template
        """
        self.template = template
        self.variables = variables or self._extract_variables(template)
    
    def _extract_variables(self, template: str) -> List[str]:
        """Extract variable names from a template string"""
        return re.findall(r'\{([^{}]*)\}', template)
    
    def format(self, **kwargs) -> str:
        """
        Format the template with the provided variables
        
        Args:
            **kwargs: Variable values to insert into the template
            
        Returns:
            Formatted prompt string
        """
        missing_vars = [var for var in self.variables if var not in kwargs]
        if missing_vars:
            raise ValueError(f"Missing variables: {', '.join(missing_vars)}")
        
        return self.template.format(**kwargs)

class PromptChain:
    """A chain of prompts that feed into each other"""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a prompt chain
        
        Args:
            name: Name of the chain
            description: Description of what the chain does
        """
        self.name = name
        self.description = description
        self.steps = []
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def add_step(self, template: PromptTemplate, name: str = None, 
                description: str = None) -> 'PromptChain':
        """
        Add a step to the chain
        
        Args:
            template: The prompt template for this step
            name: Name of this step
            description: Description of what this step does
            
        Returns:
            Self for method chaining
        """
        self.steps.append({
            "name": name or f"Step {len(self.steps) + 1}",
            "description": description or "",
            "template": template
        })
        self.metadata["updated_at"] = datetime.now().isoformat()
        return self
    
    async def execute(self, initial_variables: Dict[str, Any], 
                     client) -> List[Dict[str, Any]]:
        """
        Execute the prompt chain
        
        Args:
            initial_variables: Initial variables to start the chain
            client: MCP client to use for execution
            
        Returns:
            List of results from each step
        """
        results = []
        current_vars = initial_variables.copy()
        
        for i, step in enumerate(self.steps):
            logger.info(f"Executing chain step {i+1}/{len(self.steps)}: {step['name']}")
            
            try:
                # Format the prompt with current variables
                prompt = step["template"].format(**current_vars)
                
                # Execute the prompt
                result = await client.sync_invoke("process_text", {"text": prompt})
                
                # Store the result
                step_result = {
                    "step": step["name"],
                    "prompt": prompt,
                    "result": result
                }
                results.append(step_result)
                
                # Update variables for next step
                current_vars["previous_result"] = result.get("response", "")
                current_vars[f"step_{i+1}_result"] = result.get("response", "")
                
            except Exception as e:
                logger.error(f"Error in chain step {step['name']}: {e}")
                step_result = {
                    "step": step["name"],
                    "prompt": step["template"].template,
                    "error": str(e)
                }
                results.append(step_result)
                break
        
        return results

class PromptOptimizer:
    """Optimizes prompts for better results"""
    
    def __init__(self, templates_dir: str = "data/prompt_templates"):
        """
        Initialize the prompt optimizer
        
        Args:
            templates_dir: Directory to store prompt templates
        """
        self.templates_dir = templates_dir
        self.chains = {}
        self.templates = {}
        self.optimization_history = []
        
        # Create templates directory if it doesn't exist
        os.makedirs(templates_dir, exist_ok=True)
        
        # Load existing templates and chains
        self._load_templates()
        self._load_chains()
    
    def _load_templates(self):
        """Load prompt templates from disk"""
        template_path = os.path.join(self.templates_dir, "templates.json")
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r') as f:
                    templates_data = json.load(f)
                
                for name, data in templates_data.items():
                    self.templates[name] = PromptTemplate(
                        template=data["template"],
                        variables=data.get("variables")
                    )
                
                logger.info(f"Loaded {len(self.templates)} prompt templates")
            except Exception as e:
                logger.error(f"Error loading templates: {e}")
    
    def _load_chains(self):
        """Load prompt chains from disk"""
        chains_path = os.path.join(self.templates_dir, "chains.json")
        if os.path.exists(chains_path):
            try:
                with open(chains_path, 'r') as f:
                    chains_data = json.load(f)
                
                for name, data in chains_data.items():
                    chain = PromptChain(name, data.get("description", ""))
                    chain.metadata = data.get("metadata", chain.metadata)
                    
                    for step_data in data.get("steps", []):
                        template_name = step_data.get("template_name")
                        if template_name in self.templates:
                            chain.add_step(
                                template=self.templates[template_name],
                                name=step_data.get("name"),
                                description=step_data.get("description")
                            )
                    
                    self.chains[name] = chain
                
                logger.info(f"Loaded {len(self.chains)} prompt chains")
            except Exception as e:
                logger.error(f"Error loading chains: {e}")
    
    def save_templates(self):
        """Save prompt templates to disk"""
        templates_data = {}
        for name, template in self.templates.items():
            templates_data[name] = {
                "template": template.template,
                "variables": template.variables
            }
        
        template_path = os.path.join(self.templates_dir, "templates.json")
        with open(template_path, 'w') as f:
            json.dump(templates_data, f, indent=2)
        
        logger.info(f"Saved {len(self.templates)} prompt templates")
    
    def save_chains(self):
        """Save prompt chains to disk"""
        chains_data = {}
        for name, chain in self.chains.items():
            steps_data = []
            for i, step in enumerate(chain.steps):
                # Find template name by comparing objects
                template_name = None
                for t_name, template in self.templates.items():
                    if step["template"] == template:
                        template_name = t_name
                        break
                
                if template_name is None:
                    template_name = f"inline_template_{i}"
                    self.templates[template_name] = step["template"]
                
                steps_data.append({
                    "name": step["name"],
                    "description": step["description"],
                    "template_name": template_name
                })
            
            chains_data[name] = {
                "description": chain.description,
                "steps": steps_data,
                "metadata": chain.metadata
            }
        
        chains_path = os.path.join(self.templates_dir, "chains.json")
        with open(chains_path, 'w') as f:
            json.dump(chains_data, f, indent=2)
        
        logger.info(f"Saved {len(self.chains)} prompt chains")
    
    def create_template(self, name: str, template: str) -> PromptTemplate:
        """
        Create a new prompt template
        
        Args:
            name: Name of the template
            template: The template string
            
        Returns:
            The created template
        """
        prompt_template = PromptTemplate(template)
        self.templates[name] = prompt_template
        self.save_templates()
        return prompt_template
    
    def create_chain(self, name: str, description: str = "") -> PromptChain:
        """
        Create a new prompt chain
        
        Args:
            name: Name of the chain
            description: Description of what the chain does
            
        Returns:
            The created chain
        """
        chain = PromptChain(name, description)
        self.chains[name] = chain
        self.save_chains()
        return chain
    
    async def optimize_prompt(self, prompt: str, client, 
                             iterations: int = 3) -> Tuple[str, List[Dict]]:
        """
        Optimize a prompt through multiple iterations
        
        Args:
            prompt: The initial prompt to optimize
            client: MCP client to use for optimization
            iterations: Number of optimization iterations
            
        Returns:
            Tuple of (optimized prompt, optimization history)
        """
        history = []
        current_prompt = prompt
        
        optimization_template = PromptTemplate(
            "I need to optimize the following prompt to get better results:\n\n"
            "PROMPT: {prompt}\n\n"
            "Please suggest an improved version of this prompt that will yield better, "
            "more specific results. Focus on clarity, specificity, and providing the right context. "
            "Return ONLY the improved prompt text without explanations or formatting."
        )
        
        for i in range(iterations):
            logger.info(f"Optimization iteration {i+1}/{iterations}")
            
            # Generate optimization suggestion
            optimization_prompt = optimization_template.format(prompt=current_prompt)
            result = await client.sync_invoke("process_text", {"text": optimization_prompt})
            
            # Extract the optimized prompt
            optimized_prompt = result.get("response", current_prompt)
            
            # Test the optimized prompt
            test_result = await client.sync_invoke("process_text", {"text": optimized_prompt})
            
            # Record the iteration
            iteration = {
                "iteration": i + 1,
                "original_prompt": current_prompt,
                "optimized_prompt": optimized_prompt,
                "test_result": test_result
            }
            history.append(iteration)
            
            # Update for next iteration
            current_prompt = optimized_prompt
        
        # Add to optimization history
        self.optimization_history.append({
            "timestamp": datetime.now().isoformat(),
            "initial_prompt": prompt,
            "final_prompt": current_prompt,
            "iterations": iterations,
            "history": history
        })
        
        return current_prompt, history

# Create some default templates
def create_default_templates() -> Dict[str, PromptTemplate]:
    """Create default prompt templates"""
    return {
        "summarize": PromptTemplate(
            "Please provide a concise summary of the following text:\n\n{text}\n\n"
            "Focus on the key points and main ideas."
        ),
        "code_review": PromptTemplate(
            "Please review the following code and suggest improvements:\n\n```{language}\n{code}\n```\n\n"
            "Focus on: {focus_areas}"
        ),
        "creative_writing": PromptTemplate(
            "Write a {genre} story about {topic} with the following elements:\n"
            "- Setting: {setting}\n"
            "- Main character: {character}\n"
            "- Conflict: {conflict}\n"
            "Length: approximately {length} words."
        ),
        "question_answer": PromptTemplate(
            "Based on the following context, please answer the question:\n\n"
            "Context: {context}\n\n"
            "Question: {question}"
        )
    }

# Create some default chains
def create_default_chains(templates: Dict[str, PromptTemplate]) -> Dict[str, PromptChain]:
    """Create default prompt chains"""
    chains = {}
    
    # Research chain
    research_chain = PromptChain("research", "Research a topic thoroughly")
    research_chain.add_step(
        PromptTemplate("Generate a list of 5 key questions about {topic}"),
        name="Generate Questions",
        description="Generate key questions about the topic"
    )
    research_chain.add_step(
        PromptTemplate("Based on these questions: {previous_result}\n\n"
                      "Research and provide detailed information about {topic}"),
        name="Research",
        description="Research the topic based on the questions"
    )
    research_chain.add_step(
        templates["summarize"],
        name="Summarize",
        description="Summarize the research findings"
    )
    chains["research"] = research_chain
    
    # Code generation chain
    code_chain = PromptChain("code_generation", "Generate and improve code")
    code_chain.add_step(
        PromptTemplate("Design a high-level architecture for: {requirement}"),
        name="Architecture",
        description="Design the high-level architecture"
    )
    code_chain.add_step(
        PromptTemplate("Based on this architecture: {previous_result}\n\n"
                      "Generate {language} code that implements: {requirement}"),
        name="Implementation",
        description="Implement the code"
    )
    code_chain.add_step(
        templates["code_review"],
        name="Review",
        description="Review and improve the code"
    )
    chains["code_generation"] = code_chain
    
    return chains
