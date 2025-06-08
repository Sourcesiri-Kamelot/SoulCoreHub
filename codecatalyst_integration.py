#!/usr/bin/env python3
"""
AWS CodeCatalyst Integration for SoulCoreHub
Manages CI/CD pipelines and development workflows using AWS CodeCatalyst
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
logger = logging.getLogger('CodeCatalystIntegration')

class CodeCatalystIntegration:
    """
    Integrates with AWS CodeCatalyst for CI/CD and development workflows
    """
    
    def __init__(self):
        """
        Initialize CodeCatalyst Integration
        """
        load_dotenv()
        
        self.access_token = os.getenv('CODECATALYST_ACCESS_TOKEN')
        self.space_name = os.getenv('CODECATALYST_SPACE_NAME')
        self.project_name = os.getenv('CODECATALYST_PROJECT_NAME')
        
        if not self.access_token:
            logger.warning("CodeCatalyst access token not found in environment variables")
        
        if not self.space_name:
            self.space_name = "SoulCoreHubSpace"
            logger.info(f"Using default space name: {self.space_name}")
        
        if not self.project_name:
            self.project_name = "SoulCoreHub"
            logger.info(f"Using default project name: {self.project_name}")
        
        self.api_base_url = "https://api.codecatalyst.aws/v1"
        
        logger.info("CodeCatalyst Integration initialized")
    
    def authenticate(self):
        """
        Authenticate with AWS CodeCatalyst
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self.access_token:
            logger.error("Cannot authenticate: CodeCatalyst access token not set")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Test authentication by getting user info
            response = requests.get(f"{self.api_base_url}/me", headers=headers)
            
            if response.status_code == 200:
                user_info = response.json()
                logger.info(f"CodeCatalyst authentication successful for user: {user_info.get('displayName', 'Unknown')}")
                return True
            else:
                logger.error(f"CodeCatalyst authentication failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to authenticate with CodeCatalyst: {str(e)}")
            return False
    
    def create_workflow_definition(self, workflow_name, workflow_definition, output_file=None):
        """
        Create a workflow definition file for CodeCatalyst
        
        Args:
            workflow_name (str): Name of the workflow
            workflow_definition (dict): Workflow definition
            output_file (str, optional): Path to output file
            
        Returns:
            str: Path to the created workflow file
        """
        try:
            if output_file is None:
                workflows_dir = Path(".codecatalyst/workflows")
                workflows_dir.mkdir(exist_ok=True, parents=True)
                output_file = workflows_dir / f"{workflow_name}.yaml"
            
            # Convert workflow definition to YAML
            import yaml
            with open(output_file, 'w') as f:
                yaml.dump(workflow_definition, f, default_flow_style=False)
            
            logger.info(f"Created workflow definition at {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Failed to create workflow definition: {str(e)}")
            return None
    
    def create_ci_workflow(self, output_file=None):
        """
        Create a CI workflow definition for CodeCatalyst
        
        Args:
            output_file (str, optional): Path to output file
            
        Returns:
            str: Path to the created workflow file
        """
        workflow_definition = {
            "Name": "SoulCoreHub-CI",
            "SchemaVersion": "1.0",
            "Triggers": [
                {
                    "Type": "PUSH",
                    "Branches": ["main", "develop"]
                },
                {
                    "Type": "PULLREQUEST",
                    "Events": ["OPEN", "REVISION"]
                }
            ],
            "Actions": {
                "Build": {
                    "Identifier": "aws/build@v1",
                    "Inputs": {
                        "Sources": ["WorkflowSource"]
                    },
                    "Environment": {
                        "Connections": [
                            {
                                "Name": "AWS",
                                "Role": "CodeCatalystWorkflowDevelopmentRole-SoulCoreHub"
                            }
                        ],
                        "Name": "python3.9"
                    },
                    "Configuration": {
                        "Steps": [
                            "pip install -r requirements.txt",
                            "pip install pytest pytest-cov flake8",
                            "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
                            "pytest --cov=src tests/"
                        ]
                    }
                },
                "Package": {
                    "Identifier": "aws/build@v1",
                    "DependsOn": ["Build"],
                    "Inputs": {
                        "Sources": ["WorkflowSource"]
                    },
                    "Environment": {
                        "Connections": [
                            {
                                "Name": "AWS",
                                "Role": "CodeCatalystWorkflowDevelopmentRole-SoulCoreHub"
                            }
                        ],
                        "Name": "python3.9"
                    },
                    "Configuration": {
                        "Steps": [
                            "pip install build wheel",
                            "python -m build",
                            "mkdir -p dist",
                            "cp -r dist $CATALYST_OUTPUT_ARTIFACTS_DIR/"
                        ]
                    },
                    "Outputs": {
                        "Artifacts": [
                            {
                                "Name": "BuildOutput",
                                "Files": ["dist/**/*"]
                            }
                        ]
                    }
                }
            }
        }
        
        return self.create_workflow_definition("ci", workflow_definition, output_file)
    
    def create_cd_workflow(self, output_file=None):
        """
        Create a CD workflow definition for CodeCatalyst
        
        Args:
            output_file (str, optional): Path to output file
            
        Returns:
            str: Path to the created workflow file
        """
        workflow_definition = {
            "Name": "SoulCoreHub-CD",
            "SchemaVersion": "1.0",
            "Triggers": [
                {
                    "Type": "PUSH",
                    "Branches": ["main"]
                }
            ],
            "Actions": {
                "DeployDev": {
                    "Identifier": "aws/cfn-deploy@v1",
                    "Inputs": {
                        "Sources": ["WorkflowSource"]
                    },
                    "Environment": {
                        "Connections": [
                            {
                                "Name": "AWS",
                                "Role": "CodeCatalystWorkflowDevelopmentRole-SoulCoreHub"
                            }
                        ],
                        "Name": "aws-cli"
                    },
                    "Configuration": {
                        "region": "us-east-1",
                        "template": "infrastructure/cloudformation/agent_base_stack.yaml",
                        "capabilities": "CAPABILITY_IAM,CAPABILITY_NAMED_IAM",
                        "parameter-overrides": "Environment=dev,AgentName=GPTSoul",
                        "stack-name": "soulcorehub-gptsoul-dev"
                    }
                },
                "DeployProd": {
                    "Identifier": "aws/cfn-deploy@v1",
                    "DependsOn": ["DeployDev"],
                    "Environment": {
                        "Connections": [
                            {
                                "Name": "AWS",
                                "Role": "CodeCatalystWorkflowDevelopmentRole-SoulCoreHub"
                            }
                        ],
                        "Name": "aws-cli"
                    },
                    "Configuration": {
                        "region": "us-east-1",
                        "template": "infrastructure/cloudformation/agent_base_stack.yaml",
                        "capabilities": "CAPABILITY_IAM,CAPABILITY_NAMED_IAM",
                        "parameter-overrides": "Environment=prod,AgentName=GPTSoul",
                        "stack-name": "soulcorehub-gptsoul-prod"
                    }
                }
            }
        }
        
        return self.create_workflow_definition("cd", workflow_definition, output_file)
    
    def setup_codecatalyst_project(self):
        """
        Set up a CodeCatalyst project with CI/CD workflows
        
        Returns:
            bool: True if setup successful, False otherwise
        """
        try:
            # Create .codecatalyst directory
            codecatalyst_dir = Path(".codecatalyst")
            codecatalyst_dir.mkdir(exist_ok=True)
            
            # Create workflows directory
            workflows_dir = codecatalyst_dir / "workflows"
            workflows_dir.mkdir(exist_ok=True)
            
            # Create CI workflow
            ci_workflow = self.create_ci_workflow()
            
            # Create CD workflow
            cd_workflow = self.create_cd_workflow()
            
            # Create README file
            readme_file = codecatalyst_dir / "README.md"
            with open(readme_file, 'w') as f:
                f.write("# SoulCoreHub CodeCatalyst Configuration\n\n")
                f.write("This directory contains AWS CodeCatalyst configuration files for CI/CD workflows.\n\n")
                f.write("## Workflows\n\n")
                f.write("- **CI Workflow**: Builds and tests the application on every push and pull request.\n")
                f.write("- **CD Workflow**: Deploys the application to development and production environments on pushes to main branch.\n\n")
                f.write("## Setup\n\n")
                f.write("1. Connect your GitHub repository to CodeCatalyst.\n")
                f.write("2. Create an IAM role for CodeCatalyst workflows.\n")
                f.write("3. Configure environment variables in CodeCatalyst.\n")
            
            logger.info("CodeCatalyst project setup completed")
            return True
        except Exception as e:
            logger.error(f"Failed to set up CodeCatalyst project: {str(e)}")
            return False
    
    def generate_iam_policy(self, output_file=None):
        """
        Generate an IAM policy for CodeCatalyst workflows
        
        Args:
            output_file (str, optional): Path to output file
            
        Returns:
            str: Path to the generated policy file
        """
        try:
            if output_file is None:
                output_file = "codecatalyst_iam_policy.json"
            
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "cloudformation:*",
                            "s3:*",
                            "lambda:*",
                            "apigateway:*",
                            "dynamodb:*",
                            "logs:*",
                            "iam:GetRole",
                            "iam:PassRole"
                        ],
                        "Resource": "*"
                    }
                ]
            }
            
            with open(output_file, 'w') as f:
                json.dump(policy, f, indent=2)
            
            logger.info(f"Generated IAM policy at {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Failed to generate IAM policy: {str(e)}")
            return None

if __name__ == "__main__":
    # Example usage
    codecatalyst = CodeCatalystIntegration()
    
    # Set up CodeCatalyst project
    codecatalyst.setup_codecatalyst_project()
    
    # Generate IAM policy
    codecatalyst.generate_iam_policy()
