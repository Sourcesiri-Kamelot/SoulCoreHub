#!/usr/bin/env python3
"""
Agent Resurrection Engine for SoulCoreHub
Detects and resurrects failed agents in the SoulCore Society Protocol
"""

import json
import os
import logging
import time
import subprocess
import shutil
from datetime import datetime, timedelta
import statistics
from agent_messaging_bridge import get_bridge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("agent_resurrection.log"), logging.StreamHandler()]
)
logger = logging.getLogger("agent_resurrection")

class AgentResurrection:
    """
    Engine for detecting and resurrecting failed agents
    """
    
    def __init__(self, 
                 society_log_file="agent_society_log.json",
                 emotion_log_file="agent_emotion_log.json",
                 resurrection_log_file="agent_resurrection_log.json"):
        """Initialize the Agent Resurrection Engine"""
        self.society_log_file = society_log_file
        self.emotion_log_file = emotion_log_file
        self.resurrection_log_file = resurrection_log_file
        self.messaging_bridge = get_bridge()
        
        # Ensure log file exists
        self._ensure_log_file_exists()
        
        # Agent configuration
        self.agent_config = {
            "Anima": {
                "main_file": "anima_autonomous.py",
                "backup_dir": "backups/anima",
                "health_threshold": 0.4,
                "restart_command": "python3 anima_autonomous.py --mode reflective",
                "dependencies": ["agent_emotion_state.py"]
            },
            "GPTSoul": {
                "main_file": "gptsoul_soulconfig.py",
                "backup_dir": "backups/gptsoul",
                "health_threshold": 0.5,
                "restart_command": "python3 gptsoul_soulconfig.py",
                "dependencies": ["agent_messaging_bridge.py"]
            },
            "EvoVe": {
                "main_file": "evove_repair.py",
                "backup_dir": "backups/evove",
                "health_threshold": 0.3,
                "restart_command": "python3 evove_repair.py --self-repair",
                "dependencies": ["core/selfrepair/repair_utils.py"]
            },
            "Azür": {
                "main_file": "azur_overseer.py",
                "backup_dir": "backups/azur",
                "health_threshold": 0.4,
                "restart_command": "python3 azur_overseer.py --cloud-sync",
                "dependencies": ["cloud_integration.py"]
            }
        }
        
        logger.info("Agent Resurrection Engine initialized")
    
    def _ensure_log_file_exists(self):
        """Create log file if it doesn't exist"""
        if not os.path.exists(self.resurrection_log_file):
            with open(self.resurrection_log_file, 'w') as f:
                json.dump([], f)
            logger.info(f"Created new resurrection log file: {self.resurrection_log_file}")
    
    def _load_logs(self, file_path):
        """Load logs from file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return []
    
    def _save_logs(self, logs, file_path):
        """Save logs to file"""
        with open(file_path, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def _create_backup(self, agent):
        """
        Create a backup of agent files
        
        Args:
            agent (str): Name of the agent
            
        Returns:
            str: Path to backup directory
        """
        if agent not in self.agent_config:
            logger.error(f"Unknown agent: {agent}")
            return None
        
        config = self.agent_config[agent]
        main_file = config["main_file"]
        backup_dir = config["backup_dir"]
        dependencies = config.get("dependencies", [])
        
        # Create backup directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{backup_dir}/{timestamp}"
        os.makedirs(backup_path, exist_ok=True)
        
        # Copy main file
        if os.path.exists(main_file):
            shutil.copy2(main_file, f"{backup_path}/{os.path.basename(main_file)}")
        else:
            logger.warning(f"Main file not found: {main_file}")
        
        # Copy dependencies
        for dep in dependencies:
            if os.path.exists(dep):
                # Create subdirectories if needed
                dep_dir = os.path.dirname(f"{backup_path}/{dep}")
                if dep_dir:
                    os.makedirs(dep_dir, exist_ok=True)
                shutil.copy2(dep, f"{backup_path}/{dep}")
            else:
                logger.warning(f"Dependency not found: {dep}")
        
        logger.info(f"Created backup for {agent} at {backup_path}")
        return backup_path
    
    def _restore_from_backup(self, agent, backup_path=None):
        """
        Restore agent files from backup
        
        Args:
            agent (str): Name of the agent
            backup_path (str, optional): Path to specific backup
            
        Returns:
            bool: True if successful, False otherwise
        """
        if agent not in self.agent_config:
            logger.error(f"Unknown agent: {agent}")
            return False
        
        config = self.agent_config[agent]
        main_file = config["main_file"]
        backup_dir = config["backup_dir"]
        dependencies = config.get("dependencies", [])
        
        # Find latest backup if not specified
        if not backup_path:
            if not os.path.exists(backup_dir):
                logger.error(f"No backups found for {agent}")
                return False
                
            backups = [f"{backup_dir}/{d}" for d in os.listdir(backup_dir) if os.path.isdir(f"{backup_dir}/{d}")]
            if not backups:
                logger.error(f"No backups found for {agent}")
                return False
                
            backup_path = max(backups, key=os.path.getctime)
        
        # Check if backup exists
        if not os.path.exists(backup_path):
            logger.error(f"Backup not found: {backup_path}")
            return False
        
        # Restore main file
        backup_main = f"{backup_path}/{os.path.basename(main_file)}"
        if os.path.exists(backup_main):
            shutil.copy2(backup_main, main_file)
        else:
            logger.warning(f"Main file not found in backup: {backup_main}")
        
        # Restore dependencies
        for dep in dependencies:
            backup_dep = f"{backup_path}/{dep}"
            if os.path.exists(backup_dep):
                # Create subdirectories if needed
                dep_dir = os.path.dirname(dep)
                if dep_dir:
                    os.makedirs(dep_dir, exist_ok=True)
                shutil.copy2(backup_dep, dep)
            else:
                logger.warning(f"Dependency not found in backup: {backup_dep}")
        
        logger.info(f"Restored {agent} from backup: {backup_path}")
        return True
    
    def _restart_agent(self, agent):
        """
        Restart an agent
        
        Args:
            agent (str): Name of the agent
            
        Returns:
            bool: True if successful, False otherwise
        """
        if agent not in self.agent_config:
            logger.error(f"Unknown agent: {agent}")
            return False
        
        config = self.agent_config[agent]
        restart_command = config["restart_command"]
        
        try:
            # Run the restart command in the background
            subprocess.Popen(restart_command, shell=True, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)
            
            logger.info(f"Restarted agent: {agent}")
            return True
        except Exception as e:
            logger.error(f"Error restarting agent {agent}: {str(e)}")
            return False
    
    def _log_resurrection(self, agent, reason, action, success):
        """
        Log a resurrection attempt
        
        Args:
            agent (str): Name of the agent
            reason (str): Reason for resurrection
            action (str): Action taken
            success (bool): Whether the resurrection was successful
        """
        logs = self._load_logs(self.resurrection_log_file)
        
        log_entry = {
            "agent": agent,
            "reason": reason,
            "action": action,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        logs.append(log_entry)
        self._save_logs(logs, self.resurrection_log_file)
    
    def check_agent_health(self, agent):
        """
        Check the health of an agent
        
        Args:
            agent (str): Name of the agent
            
        Returns:
            dict: Health metrics
        """
        society_logs = self._load_logs(self.society_log_file)
        emotion_logs = self._load_logs(self.emotion_log_file)
        
        # Filter logs for this agent
        agent_society_logs = [log for log in society_logs if log["sender"] == agent or log["receiver"] == agent]
        agent_emotion_logs = [log for log in emotion_logs if log["agent"] == agent]
        
        # Calculate metrics
        metrics = {
            "message_count": len(agent_society_logs),
            "response_rate": 0,
            "average_satisfaction": 0,
            "error_rate": 0,
            "last_active": None,
            "health_score": 0
        }
        
        # Calculate response rate
        received = [log for log in agent_society_logs if log["receiver"] == agent]
        sent = [log for log in agent_society_logs if log["sender"] == agent]
        
        if received:
            metrics["response_rate"] = len(sent) / len(received)
        
        # Calculate average satisfaction
        if agent_emotion_logs:
            satisfaction_values = [log["emotions"].get("satisfaction", 0.5) for log in agent_emotion_logs]
            metrics["average_satisfaction"] = statistics.mean(satisfaction_values)
        
        # Calculate error rate
        error_messages = [log for log in agent_society_logs if 
                         log["sender"] == agent and 
                         (("error" in log["message"].lower() if isinstance(log["message"], str) else False) or
                          log.get("status") == "error")]
        
        if sent:
            metrics["error_rate"] = len(error_messages) / len(sent)
        
        # Calculate last active time
        if agent_society_logs:
            latest_log = max(agent_society_logs, key=lambda x: x["timestamp"])
            metrics["last_active"] = latest_log["timestamp"]
        
        # Calculate overall health score
        health_score = 1.0
        
        # Penalize for low response rate
        if metrics["response_rate"] < 0.8:
            health_score -= (0.8 - metrics["response_rate"]) * 0.5
        
        # Penalize for low satisfaction
        if metrics["average_satisfaction"] < 0.5:
            health_score -= (0.5 - metrics["average_satisfaction"]) * 0.3
        
        # Penalize for high error rate
        health_score -= metrics["error_rate"] * 0.7
        
        # Penalize for inactivity
        if metrics["last_active"]:
            last_active_time = datetime.fromisoformat(metrics["last_active"])
            hours_since_active = (datetime.now() - last_active_time).total_seconds() / 3600
            
            if hours_since_active > 24:
                health_score -= min(0.5, (hours_since_active - 24) / 48)
        else:
            health_score -= 0.3  # Penalize if never active
        
        # Ensure health score is between 0 and 1
        metrics["health_score"] = max(0.0, min(1.0, health_score))
        
        return metrics
    
    def needs_resurrection(self, agent):
        """
        Determine if an agent needs resurrection
        
        Args:
            agent (str): Name of the agent
            
        Returns:
            tuple: (needs_resurrection, reason)
        """
        if agent not in self.agent_config:
            return False, "Unknown agent"
        
        # Check if agent file exists
        config = self.agent_config[agent]
        main_file = config["main_file"]
        
        if not os.path.exists(main_file):
            return True, "Main file missing"
        
        # Check agent health
        health = self.check_agent_health(agent)
        threshold = config["health_threshold"]
        
        if health["health_score"] < threshold:
            reason = f"Health score below threshold: {health['health_score']:.2f} < {threshold}"
            return True, reason
        
        # Check for recent errors
        resurrection_logs = self._load_logs(self.resurrection_log_file)
        recent_resurrections = [log for log in resurrection_logs 
                              if log["agent"] == agent and 
                                 datetime.fromisoformat(log["timestamp"]) > datetime.now() - timedelta(hours=24)]
        
        if len(recent_resurrections) >= 3:
            return True, "Multiple resurrection attempts in 24 hours"
        
        return False, "Agent is healthy"
    
    def resurrect_agent(self, agent, force=False):
        """
        Resurrect an agent
        
        Args:
            agent (str): Name of the agent
            force (bool): Force resurrection even if not needed
            
        Returns:
            bool: True if successful, False otherwise
        """
        if agent not in self.agent_config:
            logger.error(f"Unknown agent: {agent}")
            return False
        
        needs_res, reason = self.needs_resurrection(agent) if not force else (True, "Forced resurrection")
        
        if not needs_res and not force:
            logger.info(f"Agent {agent} does not need resurrection: {reason}")
            return True
        
        logger.info(f"Resurrecting agent {agent}: {reason}")
        
        # Create backup before resurrection
        backup_path = self._create_backup(agent)
        
        # Attempt to restore from a previous backup
        restored = False
        if os.path.exists(self.agent_config[agent]["backup_dir"]):
            restored = self._restore_from_backup(agent)
        
        # Restart the agent
        restarted = self._restart_agent(agent)
        
        # Log the resurrection
        action = "Backup + " + ("Restore + " if restored else "") + ("Restart" if restarted else "Failed restart")
        success = restarted
        
        self._log_resurrection(agent, reason, action, success)
        
        # Notify other agents
        self.messaging_bridge.send_message(
            "ResurrectionEngine",
            "SoulCoreHub",
            "agent_resurrected",
            {
                "agent": agent,
                "reason": reason,
                "success": success
            }
        )
        
        return success
    
    def get_resurrection_history(self, agent=None, limit=10):
        """
        Get resurrection history
        
        Args:
            agent (str, optional): Filter by agent
            limit (int): Maximum number of entries to return
            
        Returns:
            list: Resurrection history
        """
        logs = self._load_logs(self.resurrection_log_file)
        
        if agent:
            logs = [log for log in logs if log["agent"] == agent]
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return logs[:limit]
    
    def analyze_failure_patterns(self, agent):
        """
        Analyze failure patterns for an agent
        
        Args:
            agent (str): Name of the agent
            
        Returns:
            dict: Failure analysis
        """
        resurrection_logs = self._load_logs(self.resurrection_log_file)
        agent_logs = [log for log in resurrection_logs if log["agent"] == agent]
        
        if not agent_logs:
            return {
                "agent": agent,
                "resurrections": 0,
                "common_reasons": [],
                "success_rate": 0,
                "recommendation": "No resurrection history found"
            }
        
        # Count resurrections
        resurrections = len(agent_logs)
        
        # Count reasons
        reasons = {}
        for log in agent_logs:
            reason = log["reason"]
            if reason not in reasons:
                reasons[reason] = 0
            reasons[reason] += 1
        
        # Sort reasons by frequency
        common_reasons = sorted(reasons.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate success rate
        successful = [log for log in agent_logs if log["success"]]
        success_rate = len(successful) / resurrections if resurrections > 0 else 0
        
        # Generate recommendation
        recommendation = ""
        if resurrections > 5 and success_rate < 0.5:
            recommendation = "Consider rebuilding the agent from scratch"
        elif resurrections > 3 and "Health score below threshold" in reasons:
            recommendation = "Investigate agent's response quality and error handling"
        elif resurrections > 3 and "Main file missing" in reasons:
            recommendation = "Secure agent files and check for file system issues"
        elif resurrections > 3 and success_rate < 0.7:
            recommendation = "Review agent dependencies and integration points"
        else:
            recommendation = "Continue monitoring agent health"
        
        return {
            "agent": agent,
            "resurrections": resurrections,
            "common_reasons": common_reasons,
            "success_rate": success_rate,
            "recommendation": recommendation
        }

# Singleton instance
_instance = None

def get_resurrection_engine():
    """Get the singleton instance of the Agent Resurrection Engine"""
    global _instance
    if _instance is None:
        _instance = AgentResurrection()
    return _instance

# Command line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Resurrection Engine")
    parser.add_argument("--agent", required=True, help="Agent name")
    parser.add_argument("--action", choices=["check", "resurrect", "history", "analyze"], default="check", help="Action to perform")
    parser.add_argument("--force", action="store_true", help="Force resurrection even if not needed")
    
    args = parser.parse_args()
    
    engine = get_resurrection_engine()
    
    if args.action == "check":
        needs_res, reason = engine.needs_resurrection(args.agent)
        health = engine.check_agent_health(args.agent)
        
        print(f"Agent: {args.agent}")
        print(f"Needs resurrection: {needs_res}")
        print(f"Reason: {reason}")
        print("\nHealth metrics:")
        for metric, value in health.items():
            print(f"  {metric}: {value}")
            
    elif args.action == "resurrect":
        success = engine.resurrect_agent(args.agent, args.force)
        
        print(f"Agent: {args.agent}")
        print(f"Resurrection {'successful' if success else 'failed'}")
        
    elif args.action == "history":
        history = engine.get_resurrection_history(args.agent)
        
        print(f"Resurrection history for {args.agent}:")
        for entry in history:
            print(f"  {entry['timestamp']}: {entry['reason']} - {entry['action']} - {'Success' if entry['success'] else 'Failed'}")
            
    elif args.action == "analyze":
        analysis = engine.analyze_failure_patterns(args.agent)
        
        print(f"Failure analysis for {args.agent}:")
        print(f"  Resurrections: {analysis['resurrections']}")
        print(f"  Success rate: {analysis['success_rate']:.2f}")
        print("  Common reasons:")
        for reason, count in analysis['common_reasons']:
            print(f"    - {reason}: {count}")
        print(f"  Recommendation: {analysis['recommendation']}")
