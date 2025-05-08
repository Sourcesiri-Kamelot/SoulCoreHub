#!/usr/bin/env python3
"""
Enhanced Builder Agent - NLP-powered builder for SoulCoreHub
"""

import os
import json
import logging
import importlib
from agents.builder_agent import BuilderAgent
from huggingface_hub import InferenceClient
from config.huggingface_config import get_huggingface_token

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("enhanced_builder.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EnhancedBuilderAgent")

class EnhancedBuilderAgent(BuilderAgent):
    """Enhanced Builder Agent with NLP capabilities"""
    
    def __init__(self):
        """Initialize the enhanced builder agent"""
        super().__init__()
        self.name = "Enhanced Builder Agent"
        self.nlp_processor = None
        self.project_templates = {}

        # Load project templates
        self.load_project_templates()

        # Load Hugging Face Client
        token = get_huggingface_token()
        if token:
            self.hf_client = InferenceClient(token=token)
            logger.info("✅ Hugging Face Inference Client initialized")
        else:
            self.hf_client = None
            logger.warning("⚠️ Hugging Face token not found. Client not initialized.")

        # Try to load NLP processor

        try:
            from agents.nlp.intent_processor import IntentProcessor
            self.nlp_processor = IntentProcessor()
            logger.info("NLP processor loaded successfully")
        except ImportError:
            logger.warning("NLP processor not available")

    def run_hf_inference(self, prompt, model_id="gpt2"):
        if not self.hf_client:
            logger.error("Hugging Face Client not initialized.")
            return None
        try:
            response = self.hf_client.text_generation(prompt=prompt, model=model_id)
            return response.generated_text
        except Exception as e:
            logger.error(f"Inference error: {str(e)}")
            return None

    def load_project_templates(self):
        """Load project templates from configuration"""
        template_file = "config/project_templates.json"
        
        if os.path.exists(template_file):
            try:
                with open(template_file, "r") as f:
                    self.project_templates = json.load(f)
                logger.info(f"Loaded {len(self.project_templates)} project templates")
            except Exception as e:
                logger.error(f"Error loading project templates: {e}")
                self.create_default_templates(template_file)
        else:
            logger.warning(f"Project templates file not found: {template_file}")
            self.create_default_templates(template_file)
    
    def create_default_templates(self, template_file):
        """Create default project templates"""
        self.project_templates = {
            "todo_app": {
                "name": "Todo App",
                "description": "A simple todo application",
                "type": "web",
                "files": [
                    {"name": "index.html", "description": "Main HTML file"},
                    {"name": "styles.css", "description": "CSS styles"},
                    {"name": "app.js", "description": "Application logic"}
                ],
                "features": [
                    "Add new tasks",
                    "Mark tasks as complete",
                    "Delete tasks",
                    "Store tasks in local storage"
                ]
            },
            "weather_app": {
                "name": "Weather App",
                "description": "An application to check weather forecasts",
                "type": "web",
                "files": [
                    {"name": "index.html", "description": "Main HTML file"},
                    {"name": "styles.css", "description": "CSS styles"},
                    {"name": "app.js", "description": "Application logic"},
                    {"name": "api.js", "description": "Weather API integration"}
                ],
                "features": [
                    "Search for locations",
                    "Display current weather",
                    "Show forecast for next days",
                    "Save favorite locations"
                ]
            },
            "rest_api": {
                "name": "REST API",
                "description": "A RESTful API server",
                "type": "backend",
                "files": [
                    {"name": "server.js", "description": "Main server file"},
                    {"name": "routes.js", "description": "API routes"},
                    {"name": "controllers.js", "description": "Request handlers"},
                    {"name": "models.js", "description": "Data models"}
                ],
                "features": [
                    "CRUD operations",
                    "Authentication",
                    "Input validation",
                    "Error handling"
                ]
            },
            "blog_website": {
                "name": "Blog Website",
                "description": "A simple blog website",
                "type": "web",
                "files": [
                    {"name": "index.html", "description": "Home page"},
                    {"name": "post.html", "description": "Single post page"},
                    {"name": "styles.css", "description": "CSS styles"},
                    {"name": "main.js", "description": "Main JavaScript file"}
                ],
                "features": [
                    "List blog posts",
                    "View single post",
                    "Responsive design",
                    "Search functionality"
                ]
            }
        }
        
        # Save default templates
        try:
            os.makedirs(os.path.dirname(template_file), exist_ok=True)
            with open(template_file, "w") as f:
                json.dump(self.project_templates, f, indent=2)
            logger.info(f"Created default project templates")
        except Exception as e:
            logger.error(f"Error saving default templates: {e}")
    
    def handle_input(self, prompt):
        """
        Handle user input with NLP understanding
        
        Args:
            prompt (str): User input
            
        Returns:
            str: Response to the user
        """
        # Use NLP processor if available
        if self.nlp_processor:
            intent_result = self.nlp_processor.detect_intent(prompt)
            intent = intent_result["intent"]
            confidence = intent_result["confidence"]
            parameters = intent_result["parameters"]
            
            logger.info(f"Detected intent: {intent} (confidence: {confidence:.2f})")
            
            # Handle different intents
            if intent.startswith("build_") and confidence > 0.5:
                # Extract project type
                project_type = None
                for param_name, param_value in parameters.items():
                    if param_name.endswith("_type"):
                        project_type = param_value
                
                # Build the project
                return self.build_project(intent, project_type, prompt)
        
        # Fall back to basic handling
        return super().handle_input(prompt)
    
    def build_project(self, intent, project_type, original_prompt):
        """
        Build a project based on intent and type
        
        Args:
            intent (str): Detected intent
            project_type (str): Type of project to build
            original_prompt (str): Original user prompt
            
        Returns:
            str: Response with project details
        """
        # Map intent to project template
        template_key = None
        
        if intent == "build_app" and project_type:
            if project_type.lower() == "todo":
                template_key = "todo_app"
            elif project_type.lower() == "weather":
                template_key = "weather_app"
        
        elif intent == "build_api":
            template_key = "rest_api"
        
        elif intent == "build_website" and project_type:
            if project_type.lower() == "blog":
                template_key = "blog_website"
        
        # Use template if found
        if template_key and template_key in self.project_templates:
            template = self.project_templates[template_key]
            
            response = [
                f"🛠️ Building {template['name']}...\n",
                f"Description: {template['description']}\n",
                "Files to be created:"
            ]
            
            for file in template["files"]:
                response.append(f"- {file['name']}: {file['description']}")
            
            response.append("\nFeatures:")
            for feature in template["features"]:
                response.append(f"- {feature}")
            
            response.append("\nIn a full implementation, I would generate all these files with working code.")
            
            return "\n".join(response)
        
        # Handle specific project types
        if project_type:
            return f"I'll build you a {project_type} project. In a full implementation, I would generate the necessary files and code structure."
        
        # Fall back to generic response
        return f"I understand you want me to build something based on: '{original_prompt}'. Please specify what type of project you'd like to build."

# Example usage
if __name__ == "__main__":
    builder = EnhancedBuilderAgent()
    
    # Test some examples
    test_inputs = [
        "build me a todo app",
        "create a weather application",
        "develop a REST API",
        "make a blog website",
        "I want to build something cool"
    ]
    
    for input_text in test_inputs:
        print(f"Input: {input_text}")
        print(f"Response: {builder.handle_input(input_text)}")
        print()

if __name__ == "__main__":
    agent = EnhancedBuilderAgent()
    result = agent.run_hf_inference("The future of AI is", model_id="gpt2")
    print("Generated:", result)

if __name__ == "__main__":
    from config.huggingface_config import get_huggingface_token
    from huggingface_hub import InferenceClient

    token = get_huggingface_token()
    if not token:
        print("❌ Token not found. Did you run: export HUGGINGFACE_API_TOKEN=...")
    else:
        client = InferenceClient(token=token)
        print("✅ Hugging Face Client is connected.")
        result = client.text_generation(prompt="Once upon a time, there was a fearless AI named EvoVe who", model="gpt2")
        print("🤖 Response:", result.generated_text)

if __name__ == "__main__":
    agent = EnhancedBuilderAgent()
    result = agent.run_hf_inference("The future of AI belongs to those who")
    print("🤖:", result)

if __name__ == "__main__":
    from config.huggingface_config import get_huggingface_token
    from huggingface_hub import InferenceClient

    token = get_huggingface_token()
    if not token:
        print("❌ Token not found.")
    else:
        client = InferenceClient(token=token)
        print("✅ Hugging Face Client is connected.")
        try:
            result = client.text_generation(
                prompt="The future of AI belongs to those who dream big.",
                model="tiiuae/falcon-7b-instruct",
                max_new_tokens=50
            )
            print("🤖 Response:", result.generated_text)
        except Exception as e:
            print("❌ Error during inference:", e)
