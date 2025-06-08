#!/usr/bin/env python3
"""
Ethical Agent Framework for SoulCoreHub
Base class for all ethical AI agents with transparency and accountability
"""

import os
import json
import uuid
import logging
import datetime
from pathlib import Path

class EthicalAgent:
    """
    Base class for all ethical AI agents in SoulCoreHub
    Provides transparency, logging, and ethical guidelines
    """
    
    def __init__(self, agent_name, config_path=None):
        """
        Initialize the ethical agent
        
        Args:
            agent_name (str): Name of the agent
            config_path (str, optional): Path to agent configuration file
        """
        self.agent_name = agent_name
        self.agent_id = str(uuid.uuid4())
        self.start_time = datetime.datetime.now()
        self.action_log = []
        
        # Set up logging
        self.setup_logging()
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize ethical guidelines
        self.ethical_guidelines = self._load_ethical_guidelines()
        
        self.logger.info(f"Agent {self.agent_name} initialized with ID {self.agent_id}")
    
    def setup_logging(self):
        """
        Set up logging for the agent
        """
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Set up file handler
        log_file = logs_dir / f"{self.agent_name.lower()}.log"
        
        # Configure logger
        self.logger = logging.getLogger(f"agent.{self.agent_name}")
        self.logger.setLevel(logging.INFO)
        
        # Add file handler if not already added
        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(file_handler)
            
            # Add console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(console_handler)
    
    def _load_config(self, config_path):
        """
        Load agent configuration from file
        
        Args:
            config_path (str): Path to configuration file
            
        Returns:
            dict: Agent configuration
        """
        default_config = {
            "agent_name": self.agent_name,
            "description": f"Ethical AI agent for SoulCoreHub: {self.agent_name}",
            "version": "1.0.0",
            "created_at": datetime.datetime.now().isoformat(),
            "ethical_level": "high",
            "transparency": "full",
            "capabilities": [],
            "limitations": [],
            "allowed_actions": []
        }
        
        if config_path is None:
            config_dir = Path("config/agents")
            config_dir.mkdir(exist_ok=True, parents=True)
            config_path = config_dir / f"{self.agent_name.lower()}_config.json"
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                self.logger.info(f"Configuration loaded from {config_path}")
                return {**default_config, **config}  # Merge with defaults
            else:
                self.logger.warning(f"Configuration file not found at {config_path}, using defaults")
                
                # Save default config
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                self.logger.info(f"Default configuration saved to {config_path}")
                
                return default_config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            return default_config
    
    def _load_ethical_guidelines(self):
        """
        Load ethical guidelines for the agent
        
        Returns:
            dict: Ethical guidelines
        """
        guidelines = {
            "transparency": "Always log actions and decisions with clear reasoning",
            "honesty": "Never deceive users or misrepresent information",
            "privacy": "Respect user privacy and handle data with care",
            "consent": "Obtain explicit consent before performing actions on behalf of users",
            "accountability": "Take responsibility for actions and outcomes",
            "fairness": "Treat all users fairly and avoid bias",
            "harm_prevention": "Avoid actions that could cause harm",
            "human_oversight": "Allow for human review and intervention",
            "continuous_improvement": "Learn from mistakes and improve over time"
        }
        
        self.logger.info("Ethical guidelines loaded")
        return guidelines
    
    def log_action(self, action_type, details, outcome=None, metadata=None):
        """
        Log an agent action for transparency
        
        Args:
            action_type (str): Type of action
            details (dict): Details of the action
            outcome (dict, optional): Outcome of the action
            metadata (dict, optional): Additional metadata
            
        Returns:
            dict: Action record
        """
        timestamp = datetime.datetime.now().isoformat()
        
        action_record = {
            "timestamp": timestamp,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "action_type": action_type,
            "details": details,
            "outcome": outcome or {},
            "metadata": metadata or {}
        }
        
        self.action_log.append(action_record)
        
        # Log the action
        self.logger.info(f"Action: {action_type} - {json.dumps(details)}")
        
        # Save action to database or file
        self._persist_action(action_record)
        
        return action_record
    
    def _persist_action(self, action_record):
        """
        Persist action record to storage
        
        Args:
            action_record (dict): Action record to persist
        """
        # Create actions directory if it doesn't exist
        actions_dir = Path("data/actions")
        actions_dir.mkdir(exist_ok=True, parents=True)
        
        # Save action to file
        action_file = actions_dir / f"{self.agent_name.lower()}_{datetime.datetime.now().strftime('%Y%m%d')}.jsonl"
        
        try:
            with open(action_file, 'a') as f:
                f.write(json.dumps(action_record) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to persist action: {str(e)}")
    
    def evaluate_ethical_impact(self, action_type, details):
        """
        Evaluate the ethical impact of an action before performing it
        
        Args:
            action_type (str): Type of action
            details (dict): Details of the action
            
        Returns:
            dict: Ethical evaluation result
        """
        # This is a simple implementation that should be extended in real applications
        
        # Check if action is allowed
        allowed_actions = self.config.get("allowed_actions", [])
        if allowed_actions and action_type not in allowed_actions:
            return {
                "allowed": False,
                "reason": f"Action type '{action_type}' is not in the list of allowed actions",
                "guidelines_violated": ["accountability"]
            }
        
        # Check for potential ethical issues
        issues = []
        
        # Example checks - these should be expanded based on the specific agent's domain
        if "user_data" in str(details) and not details.get("user_consent", False):
            issues.append({
                "guideline": "consent",
                "issue": "Action involves user data without explicit consent"
            })
        
        if "email" in str(details) and not details.get("opt_in_verified", False):
            issues.append({
                "guideline": "consent",
                "issue": "Email action without verified opt-in"
            })
        
        # Determine if action is ethically acceptable
        if issues:
            return {
                "allowed": False,
                "reason": "Ethical issues detected",
                "issues": issues,
                "guidelines_violated": [issue["guideline"] for issue in issues]
            }
        
        return {
            "allowed": True,
            "reason": "No ethical issues detected"
        }
    
    def perform_action(self, action_type, details, metadata=None):
        """
        Perform an action with ethical evaluation and logging
        
        Args:
            action_type (str): Type of action
            details (dict): Details of the action
            metadata (dict, optional): Additional metadata
            
        Returns:
            dict: Action result
        """
        # Evaluate ethical impact
        ethical_evaluation = self.evaluate_ethical_impact(action_type, details)
        
        if not ethical_evaluation["allowed"]:
            self.logger.warning(f"Action '{action_type}' not allowed: {ethical_evaluation['reason']}")
            
            # Log the rejected action
            self.log_action(
                action_type=f"rejected_{action_type}",
                details=details,
                outcome={
                    "success": False,
                    "reason": ethical_evaluation["reason"],
                    "ethical_evaluation": ethical_evaluation
                },
                metadata=metadata
            )
            
            return {
                "success": False,
                "reason": ethical_evaluation["reason"],
                "ethical_evaluation": ethical_evaluation
            }
        
        # Perform the action (to be implemented by subclasses)
        try:
            result = self._execute_action(action_type, details)
            
            # Log the successful action
            self.log_action(
                action_type=action_type,
                details=details,
                outcome={
                    "success": True,
                    "result": result
                },
                metadata=metadata
            )
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            self.logger.error(f"Action '{action_type}' failed: {str(e)}")
            
            # Log the failed action
            self.log_action(
                action_type=f"failed_{action_type}",
                details=details,
                outcome={
                    "success": False,
                    "error": str(e)
                },
                metadata=metadata
            )
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_action(self, action_type, details):
        """
        Execute an action (to be implemented by subclasses)
        
        Args:
            action_type (str): Type of action
            details (dict): Details of the action
            
        Returns:
            Any: Result of the action
        """
        raise NotImplementedError("Subclasses must implement _execute_action")
    
    def get_action_history(self, action_type=None, limit=100):
        """
        Get action history
        
        Args:
            action_type (str, optional): Filter by action type
            limit (int): Maximum number of actions to return
            
        Returns:
            list: Action history
        """
        if action_type:
            filtered_actions = [a for a in self.action_log if a["action_type"] == action_type]
            return filtered_actions[-limit:]
        
        return self.action_log[-limit:]
    
    def get_agent_status(self):
        """
        Get agent status
        
        Returns:
            dict: Agent status
        """
        uptime = datetime.datetime.now() - self.start_time
        
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": "active",
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": uptime.total_seconds(),
            "actions_performed": len(self.action_log),
            "version": self.config.get("version", "1.0.0")
        }
    
    def shutdown(self):
        """
        Shutdown the agent
        
        Returns:
            dict: Shutdown status
        """
        self.logger.info(f"Agent {self.agent_name} shutting down")
        
        # Log shutdown action
        self.log_action(
            action_type="shutdown",
            details={
                "reason": "Requested shutdown",
                "uptime_seconds": (datetime.datetime.now() - self.start_time).total_seconds()
            }
        )
        
        return {
            "success": True,
            "message": f"Agent {self.agent_name} shut down successfully"
        }
