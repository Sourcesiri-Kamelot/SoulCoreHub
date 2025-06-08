#!/usr/bin/env python3
"""
NVIDIA Integration for SoulCoreHub
Leverages NVIDIA NGC resources for AI model training and inference
"""

import os
import json
import logging
import requests
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('NVIDIAIntegration')

class NVIDIAIntegration:
    """
    Integrates with NVIDIA NGC for AI model training and inference
    """
    
    def __init__(self):
        """
        Initialize NVIDIA Integration
        """
        load_dotenv()
        
        self.api_key = os.getenv('NVIDIA_NGC_API_KEY')
        self.org = os.getenv('NVIDIA_NGC_ORG')
        self.team = os.getenv('NVIDIA_NGC_TEAM')
        
        if not self.api_key:
            logger.warning("NVIDIA NGC API key not found in environment variables")
        
        self.models_dir = Path("models/nvidia")
        self.models_dir.mkdir(exist_ok=True, parents=True)
        
        self.api_base_url = "https://api.ngc.nvidia.com/v2"
        self.registry_url = "nvcr.io"
        
        logger.info("NVIDIA Integration initialized")
    
    def authenticate(self):
        """
        Authenticate with NVIDIA NGC
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self.api_key:
            logger.error("Cannot authenticate: NVIDIA NGC API key not set")
            return False
        
        try:
            # Set up NGC CLI configuration
            ngc_config_dir = Path.home() / ".ngc"
            ngc_config_dir.mkdir(exist_ok=True)
            
            config_file = ngc_config_dir / "config"
            with open(config_file, 'w') as f:
                f.write(f"apikey = {self.api_key}\n")
                if self.org:
                    f.write(f"org = {self.org}\n")
                if self.team:
                    f.write(f"team = {self.team}\n")
            
            # Test authentication
            result = subprocess.run(
                ["ngc", "auth", "test"],
                capture_output=True,
                text=True
            )
            
            if "Authentication successful" in result.stdout:
                logger.info("NVIDIA NGC authentication successful")
                return True
            else:
                logger.error(f"NVIDIA NGC authentication failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Failed to authenticate with NVIDIA NGC: {str(e)}")
            return False
    
    def list_models(self, filter_query=None):
        """
        List available models from NVIDIA NGC
        
        Args:
            filter_query (str, optional): Filter query for models
            
        Returns:
            list: List of available models
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.api_base_url}/resources"
            params = {}
            
            if filter_query:
                params["filter"] = filter_query
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                models = response.json()
                logger.info(f"Retrieved {len(models)} models from NVIDIA NGC")
                return models
            else:
                logger.error(f"Failed to list models: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            return []
    
    def pull_model(self, model_name, model_version="latest"):
        """
        Pull a model from NVIDIA NGC
        
        Args:
            model_name (str): Name of the model
            model_version (str, optional): Version of the model
            
        Returns:
            bool: True if pull successful, False otherwise
        """
        try:
            # Create model directory
            model_dir = self.models_dir / model_name
            model_dir.mkdir(exist_ok=True)
            
            # Pull model using NGC CLI
            result = subprocess.run(
                ["ngc", "registry", "model", "pull", f"{model_name}:{model_version}"],
                cwd=str(model_dir),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully pulled model {model_name}:{model_version}")
                return True
            else:
                logger.error(f"Failed to pull model {model_name}:{model_version}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {str(e)}")
            return False
    
    def run_inference(self, model_name, input_data, model_version="latest"):
        """
        Run inference using a model from NVIDIA NGC
        
        Args:
            model_name (str): Name of the model
            input_data: Input data for inference
            model_version (str, optional): Version of the model
            
        Returns:
            dict: Inference results
        """
        try:
            # Check if model is available locally
            model_dir = self.models_dir / model_name
            if not model_dir.exists():
                logger.info(f"Model {model_name} not found locally, pulling from NGC")
                if not self.pull_model(model_name, model_version):
                    return {"error": f"Failed to pull model {model_name}:{model_version}"}
            
            # Prepare input data
            input_file = model_dir / "input.json"
            with open(input_file, 'w') as f:
                json.dump(input_data, f)
            
            # Run inference using Docker
            container_name = f"soulcorehub-{model_name.replace('/', '-')}"
            image_name = f"{self.registry_url}/{model_name}:{model_version}"
            
            # Pull Docker image if needed
            subprocess.run(
                ["docker", "pull", image_name],
                check=True,
                capture_output=True
            )
            
            # Run inference
            result = subprocess.run(
                [
                    "docker", "run", "--rm", "--gpus", "all",
                    "--name", container_name,
                    "-v", f"{model_dir}:/workspace/input",
                    image_name,
                    "python", "/workspace/inference.py", "--input", "/workspace/input/input.json"
                ],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Parse output
                try:
                    output = json.loads(result.stdout)
                    logger.info(f"Inference completed successfully for {model_name}")
                    return output
                except json.JSONDecodeError:
                    logger.warning(f"Inference output is not valid JSON: {result.stdout}")
                    return {"result": result.stdout}
            else:
                logger.error(f"Inference failed: {result.stderr}")
                return {"error": result.stderr}
        except Exception as e:
            logger.error(f"Failed to run inference: {str(e)}")
            return {"error": str(e)}
    
    def setup_training_environment(self, framework="pytorch", version="latest"):
        """
        Set up a training environment using NVIDIA containers
        
        Args:
            framework (str): ML framework to use (pytorch, tensorflow, etc.)
            version (str): Framework version
            
        Returns:
            dict: Environment setup information
        """
        try:
            # Determine container image
            if framework.lower() == "pytorch":
                image = f"{self.registry_url}/nvidia/pytorch:{version}"
            elif framework.lower() == "tensorflow":
                image = f"{self.registry_url}/nvidia/tensorflow:{version}"
            else:
                image = f"{self.registry_url}/nvidia/{framework}:{version}"
            
            # Pull container image
            subprocess.run(
                ["docker", "pull", image],
                check=True,
                capture_output=True
            )
            
            # Create container name
            container_name = f"soulcorehub-training-{framework}"
            
            # Create training directory
            training_dir = Path("training") / framework
            training_dir.mkdir(exist_ok=True, parents=True)
            
            # Return environment info
            return {
                "framework": framework,
                "version": version,
                "image": image,
                "container_name": container_name,
                "training_dir": str(training_dir),
                "run_command": f"docker run --gpus all -it --rm -v {training_dir}:/workspace --name {container_name} {image}"
            }
        except Exception as e:
            logger.error(f"Failed to set up training environment: {str(e)}")
            return {"error": str(e)}
    
    def list_available_containers(self):
        """
        List available NVIDIA containers
        
        Returns:
            list: List of available containers
        """
        try:
            # Query NGC registry
            result = subprocess.run(
                ["ngc", "registry", "image", "list"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Parse output
                containers = []
                lines = result.stdout.strip().split('\n')
                
                # Skip header
                for line in lines[2:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            containers.append({
                                "name": parts[0],
                                "version": parts[1]
                            })
                
                logger.info(f"Retrieved {len(containers)} containers from NVIDIA NGC")
                return containers
            else:
                logger.error(f"Failed to list containers: {result.stderr}")
                return []
        except Exception as e:
            logger.error(f"Failed to list containers: {str(e)}")
            return []
    
    def get_gpu_info(self):
        """
        Get information about available GPUs
        
        Returns:
            list: Information about available GPUs
        """
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,memory.free,temperature.gpu", "--format=csv,noheader"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                gpus = []
                lines = result.stdout.strip().split('\n')
                
                for i, line in enumerate(lines):
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) >= 4:
                        gpus.append({
                            "index": i,
                            "name": parts[0],
                            "memory_total": parts[1],
                            "memory_free": parts[2],
                            "temperature": parts[3]
                        })
                
                logger.info(f"Found {len(gpus)} GPUs")
                return gpus
            else:
                logger.warning("Failed to get GPU info, NVIDIA driver might not be installed or accessible")
                return []
        except Exception as e:
            logger.warning(f"Failed to get GPU info: {str(e)}")
            return []

if __name__ == "__main__":
    # Example usage
    nvidia = NVIDIAIntegration()
    
    # Check authentication
    if nvidia.authenticate():
        print("Authentication successful")
        
        # List available models
        models = nvidia.list_models("category:NLP")
        print(f"Found {len(models)} NLP models")
        
        # Get GPU info
        gpus = nvidia.get_gpu_info()
        if gpus:
            print(f"Found {len(gpus)} GPUs:")
            for gpu in gpus:
                print(f"  {gpu['name']} - {gpu['memory_free']} free")
        else:
            print("No GPUs found or NVIDIA driver not installed")
        
        # Set up training environment
        env_info = nvidia.setup_training_environment("pytorch", "23.04-py3")
        print(f"Training environment set up with {env_info['framework']} {env_info['version']}")
        print(f"Run command: {env_info['run_command']}")
    else:
        print("Authentication failed")
