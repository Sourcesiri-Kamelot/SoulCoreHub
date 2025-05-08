#!/usr/bin/env python3
"""
EvoVe Dependency Scanner for SoulCoreHub
Scans all agent folders to validate dependencies and backups
"""

import os
import sys
import json
import logging
import shutil
from datetime import datetime
import hashlib
from agent_messaging_bridge import get_bridge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("evove_scanner.log"), logging.StreamHandler()]
)
logger = logging.getLogger("evove_dependency_scanner")

class EvoveDependencyScanner:
    """
    Scanner that validates dependencies and backups for all agents
    """
    
    def __init__(self, scan_report_file="dependency_scan_report.json"):
        """Initialize the EvoVe Dependency Scanner"""
        self.scan_report_file = scan_report_file
        self.messaging_bridge = get_bridge()
        
        # Agent configuration
        self.agent_config = {
            "Anima": {
                "main_file": "anima_autonomous.py",
                "required_files": [
                    "agent_emotion_state.py",
                    "agent_messaging_bridge.py",
                    "fusion_protocol.py"
                ],
                "backup_dir": "backups/anima"
            },
            "GPTSoul": {
                "main_file": "gptsoul_soulconfig.py",
                "required_files": [
                    "agent_messaging_bridge.py",
                    "fusion_protocol.py"
                ],
                "backup_dir": "backups/gptsoul"
            },
            "EvoVe": {
                "main_file": "evove_repair.py",
                "required_files": [
                    "agent_messaging_bridge.py",
                    "agent_resurrection.py"
                ],
                "backup_dir": "backups/evove"
            },
            "Azür": {
                "main_file": "azur_overseer.py",
                "required_files": [
                    "agent_messaging_bridge.py",
                    "cloud_integration.py"
                ],
                "backup_dir": "backups/azur"
            },
            "SoulCoreSociety": {
                "main_file": "soulcore_society.py",
                "required_files": [
                    "agent_messaging_bridge.py",
                    "fusion_protocol.py",
                    "agent_emotion_state.py",
                    "agent_resurrection.py"
                ],
                "backup_dir": "backups/society"
            }
        }
        
        # Core system files
        self.core_files = [
            "agent_messaging_bridge.py",
            "fusion_protocol.py",
            "agent_emotion_state.py",
            "agent_resurrection.py",
            "soulcore_society.py",
            "query_interpreter.py"
        ]
        
        # JSON data files
        self.json_files = [
            "agent_society_log.json",
            "agent_emotion_log.json",
            "agent_fusion_log.json",
            "agent_resurrection_log.json"
        ]
        
        logger.info("EvoVe Dependency Scanner initialized")
    
    def _ensure_directory_exists(self, directory):
        """
        Ensure a directory exists
        
        Args:
            directory (str): Directory path
            
        Returns:
            bool: True if directory exists or was created
        """
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
                return True
            except Exception as e:
                logger.error(f"Error creating directory {directory}: {str(e)}")
                return False
        return True
    
    def _calculate_file_hash(self, file_path):
        """
        Calculate SHA-256 hash of a file
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Hash of the file
        """
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {str(e)}")
            return None
    
    def _create_backup(self, agent):
        """
        Create a backup of agent files
        
        Args:
            agent (str): Name of the agent
            
        Returns:
            dict: Backup result
        """
        if agent not in self.agent_config:
            logger.error(f"Unknown agent: {agent}")
            return {"success": False, "error": "Unknown agent"}
        
        config = self.agent_config[agent]
        main_file = config["main_file"]
        backup_dir = config["backup_dir"]
        required_files = config["required_files"]
        
        # Create backup directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{backup_dir}/{timestamp}"
        
        if not self._ensure_directory_exists(backup_path):
            return {"success": False, "error": f"Failed to create backup directory: {backup_path}"}
        
        backup_files = []
        missing_files = []
        
        # Copy main file
        if os.path.exists(main_file):
            try:
                shutil.copy2(main_file, f"{backup_path}/{os.path.basename(main_file)}")
                backup_files.append(main_file)
            except Exception as e:
                logger.error(f"Error backing up {main_file}: {str(e)}")
                missing_files.append(main_file)
        else:
            logger.warning(f"Main file not found: {main_file}")
            missing_files.append(main_file)
        
        # Copy required files
        for file in required_files:
            if os.path.exists(file):
                try:
                    # Create subdirectories if needed
                    file_dir = os.path.dirname(f"{backup_path}/{file}")
                    if file_dir:
                        os.makedirs(file_dir, exist_ok=True)
                    
                    shutil.copy2(file, f"{backup_path}/{file}")
                    backup_files.append(file)
                except Exception as e:
                    logger.error(f"Error backing up {file}: {str(e)}")
                    missing_files.append(file)
            else:
                logger.warning(f"Required file not found: {file}")
                missing_files.append(file)
        
        logger.info(f"Created backup for {agent} at {backup_path}")
        
        return {
            "success": len(missing_files) == 0,
            "backup_path": backup_path,
            "backup_files": backup_files,
            "missing_files": missing_files,
            "timestamp": timestamp
        }
    
    def scan_agent(self, agent):
        """
        Scan an agent for dependencies and backups
        
        Args:
            agent (str): Name of the agent
            
        Returns:
            dict: Scan result
        """
        if agent not in self.agent_config:
            logger.error(f"Unknown agent: {agent}")
            return {"success": False, "error": "Unknown agent"}
        
        config = self.agent_config[agent]
        main_file = config["main_file"]
        required_files = config["required_files"]
        backup_dir = config["backup_dir"]
        
        # Check main file
        main_file_exists = os.path.exists(main_file)
        main_file_hash = self._calculate_file_hash(main_file) if main_file_exists else None
        
        # Check required files
        required_file_status = {}
        missing_files = []
        
        for file in required_files:
            file_exists = os.path.exists(file)
            file_hash = self._calculate_file_hash(file) if file_exists else None
            
            required_file_status[file] = {
                "exists": file_exists,
                "hash": file_hash
            }
            
            if not file_exists:
                missing_files.append(file)
        
        # Check backup directory
        backup_dir_exists = os.path.exists(backup_dir)
        backups = []
        
        if backup_dir_exists:
            try:
                backup_folders = [d for d in os.listdir(backup_dir) if os.path.isdir(f"{backup_dir}/{d}")]
                backup_folders.sort(reverse=True)  # Newest first
                
                for folder in backup_folders[:3]:  # Only check the 3 most recent backups
                    backup_path = f"{backup_dir}/{folder}"
                    backup_main_file = f"{backup_path}/{os.path.basename(main_file)}"
                    
                    backup_main_exists = os.path.exists(backup_main_file)
                    backup_main_hash = self._calculate_file_hash(backup_main_file) if backup_main_exists else None
                    
                    backups.append({
                        "path": backup_path,
                        "timestamp": folder,
                        "main_file_exists": backup_main_exists,
                        "main_file_hash": backup_main_hash
                    })
            except Exception as e:
                logger.error(f"Error checking backups for {agent}: {str(e)}")
        
        # Create backup if needed
        backup_needed = not backup_dir_exists or not backups or len(missing_files) > 0
        backup_result = None
        
        if backup_needed:
            # Ensure backup directory exists
            self._ensure_directory_exists(backup_dir)
            
            # Create backup
            backup_result = self._create_backup(agent)
        
        return {
            "agent": agent,
            "main_file": {
                "path": main_file,
                "exists": main_file_exists,
                "hash": main_file_hash
            },
            "required_files": required_file_status,
            "missing_files": missing_files,
            "backup_dir": {
                "path": backup_dir,
                "exists": backup_dir_exists
            },
            "recent_backups": backups,
            "backup_needed": backup_needed,
            "backup_created": backup_result is not None,
            "backup_result": backup_result,
            "timestamp": datetime.now().isoformat()
        }
    
    def scan_core_files(self):
        """
        Scan core system files
        
        Returns:
            dict: Scan result
        """
        core_file_status = {}
        missing_files = []
        
        for file in self.core_files:
            file_exists = os.path.exists(file)
            file_hash = self._calculate_file_hash(file) if file_exists else None
            
            core_file_status[file] = {
                "exists": file_exists,
                "hash": file_hash
            }
            
            if not file_exists:
                missing_files.append(file)
        
        return {
            "core_files": core_file_status,
            "missing_files": missing_files,
            "timestamp": datetime.now().isoformat()
        }
    
    def scan_json_files(self):
        """
        Scan JSON data files
        
        Returns:
            dict: Scan result
        """
        json_file_status = {}
        missing_files = []
        
        for file in self.json_files:
            file_exists = os.path.exists(file)
            
            # Check if file is valid JSON
            json_valid = False
            if file_exists:
                try:
                    with open(file, 'r') as f:
                        json.load(f)
                    json_valid = True
                except json.JSONDecodeError:
                    json_valid = False
            
            json_file_status[file] = {
                "exists": file_exists,
                "valid_json": json_valid
            }
            
            if not file_exists:
                missing_files.append(file)
        
        return {
            "json_files": json_file_status,
            "missing_files": missing_files,
            "timestamp": datetime.now().isoformat()
        }
    
    def scan_all(self):
        """
        Scan all agents and system files
        
        Returns:
            dict: Complete scan report
        """
        logger.info("Starting complete system scan")
        
        # Scan core files
        core_scan = self.scan_core_files()
        
        # Scan JSON files
        json_scan = self.scan_json_files()
        
        # Scan agents
        agent_scans = {}
        for agent in self.agent_config:
            agent_scans[agent] = self.scan_agent(agent)
        
        # Compile report
        report = {
            "timestamp": datetime.now().isoformat(),
            "core_files": core_scan,
            "json_files": json_scan,
            "agents": agent_scans
        }
        
        # Calculate overall health
        missing_core_files = len(core_scan["missing_files"])
        missing_json_files = len(json_scan["missing_files"])
        
        agent_health = {}
        for agent, scan in agent_scans.items():
            missing_agent_files = len(scan["missing_files"])
            backup_status = scan["backup_created"] or (scan["recent_backups"] and len(scan["recent_backups"]) > 0)
            
            if missing_agent_files == 0 and backup_status:
                health = "healthy"
            elif missing_agent_files > 0 and backup_status:
                health = "degraded"
            else:
                health = "critical"
            
            agent_health[agent] = health
        
        if missing_core_files == 0 and missing_json_files == 0 and all(health == "healthy" for health in agent_health.values()):
            system_health = "healthy"
        elif missing_core_files > 0 or any(health == "critical" for health in agent_health.values()):
            system_health = "critical"
        else:
            system_health = "degraded"
        
        report["health"] = {
            "system": system_health,
            "agents": agent_health
        }
        
        # Save report
        with open(self.scan_report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Scan completed. System health: {system_health}")
        
        # Notify via messaging bridge
        self.messaging_bridge.send_message(
            "EvoVe",
            "SoulCoreSociety",
            "dependency_scan_complete",
            {
                "system_health": system_health,
                "report_file": self.scan_report_file,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return report
    
    def fix_issues(self, report=None):
        """
        Fix issues found in scan
        
        Args:
            report (dict, optional): Scan report to use
            
        Returns:
            dict: Fix result
        """
        if report is None:
            # Load report from file
            try:
                with open(self.scan_report_file, 'r') as f:
                    report = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.error(f"Error loading scan report: {self.scan_report_file}")
                return {"success": False, "error": "Failed to load scan report"}
        
        fixes = {
            "json_files_created": [],
            "backups_created": [],
            "errors": []
        }
        
        # Fix missing JSON files
        for file in report["json_files"]["missing_files"]:
            try:
                with open(file, 'w') as f:
                    json.dump([], f)
                fixes["json_files_created"].append(file)
                logger.info(f"Created missing JSON file: {file}")
            except Exception as e:
                error = f"Error creating {file}: {str(e)}"
                fixes["errors"].append(error)
                logger.error(error)
        
        # Create backups for agents that need them
        for agent, scan in report["agents"].items():
            if scan["backup_needed"] and not scan["backup_created"]:
                backup_result = self._create_backup(agent)
                
                if backup_result["success"]:
                    fixes["backups_created"].append({
                        "agent": agent,
                        "path": backup_result["backup_path"]
                    })
                else:
                    error = f"Failed to create backup for {agent}: {backup_result.get('error', 'Unknown error')}"
                    fixes["errors"].append(error)
                    logger.error(error)
        
        # Calculate success
        fixes["success"] = len(fixes["errors"]) == 0
        
        # Notify via messaging bridge
        self.messaging_bridge.send_message(
            "EvoVe",
            "SoulCoreSociety",
            "dependency_fix_complete",
            {
                "success": fixes["success"],
                "json_files_created": len(fixes["json_files_created"]),
                "backups_created": len(fixes["backups_created"]),
                "errors": len(fixes["errors"]),
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return fixes

# Singleton instance
_instance = None

def get_scanner():
    """Get the singleton instance of the EvoVe Dependency Scanner"""
    global _instance
    if _instance is None:
        _instance = EvoveDependencyScanner()
    return _instance

# Command line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="EvoVe Dependency Scanner")
    parser.add_argument("--action", choices=["scan", "fix", "scan-agent"], default="scan", help="Action to perform")
    parser.add_argument("--agent", help="Agent to scan (for scan-agent action)")
    parser.add_argument("--report", help="Path to scan report (for fix action)")
    
    args = parser.parse_args()
    
    scanner = get_scanner()
    
    if args.action == "scan":
        print("Scanning all agents and system files...")
        report = scanner.scan_all()
        
        print(f"\nScan complete. System health: {report['health']['system']}")
        print("\nAgent health:")
        for agent, health in report['health']['agents'].items():
            print(f"  {agent}: {health}")
        
        print(f"\nScan report saved to: {scanner.scan_report_file}")
        
    elif args.action == "fix":
        print("Fixing issues...")
        
        report = None
        if args.report:
            try:
                with open(args.report, 'r') as f:
                    report = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                print(f"Error loading scan report: {args.report}")
                sys.exit(1)
        
        fixes = scanner.fix_issues(report)
        
        if fixes["success"]:
            print("\nAll issues fixed successfully!")
        else:
            print("\nSome issues could not be fixed:")
            for error in fixes["errors"]:
                print(f"  - {error}")
        
        print("\nFixes applied:")
        print(f"  - JSON files created: {len(fixes['json_files_created'])}")
        print(f"  - Backups created: {len(fixes['backups_created'])}")
        
    elif args.action == "scan-agent":
        if not args.agent:
            print("Error: agent is required for scan-agent action")
            sys.exit(1)
        
        print(f"Scanning agent: {args.agent}")
        scan = scanner.scan_agent(args.agent)
        
        if "error" in scan:
            print(f"Error: {scan['error']}")
            sys.exit(1)
        
        print("\nMain file:")
        print(f"  Path: {scan['main_file']['path']}")
        print(f"  Exists: {scan['main_file']['exists']}")
        
        print("\nRequired files:")
        for file, status in scan['required_files'].items():
            print(f"  {file}: {'✓' if status['exists'] else '✗'}")
        
        print("\nBackups:")
        if scan['recent_backups']:
            for backup in scan['recent_backups']:
                print(f"  {backup['timestamp']}: {'✓' if backup['main_file_exists'] else '✗'}")
        else:
            print("  No recent backups found")
        
        if scan['backup_created']:
            print(f"\nNew backup created: {scan['backup_result']['backup_path']}")
        elif scan['backup_needed']:
            print("\nBackup needed but not created")
