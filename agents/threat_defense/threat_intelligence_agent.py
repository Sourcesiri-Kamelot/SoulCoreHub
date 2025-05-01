"""
Threat Intelligence Agent - Gathers threat intelligence from external feeds and reports new vulnerabilities or attack patterns.
"""

import logging
import time
import threading
import json
import os
import random
from pathlib import Path
from datetime import datetime, timedelta
import hashlib

class ThreatIntelligenceAgent:
    def __init__(self):
        self.name = "Threat Intelligence Agent"
        self.status = "active"
        self.running = False
        self.intel_sources = []
        self.threat_database = []
        self.last_update = None
        self.update_interval = 3600  # Update every hour (in seconds)
        self.log_file = Path("logs/threat_intelligence.log")
        self.config_file = Path("config/intel_sources.json")
        self.database_file = Path("memory/threat_database.json")
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_file.parent, exist_ok=True)
        
        # Load intel sources
        self.load_sources()
        
        # Load threat database
        self.load_database()
        
        # Set up logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)
        self.logger.info(f"{self.name} initialized")
        
        # Thread for intelligence gathering
        self._thread = None
        
        # Event bus reference (will be set by orchestrator)
        self.event_bus = None

    def load_sources(self):
        """Load threat intelligence sources from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.intel_sources = json.load(f)
                    self.logger.info(f"Loaded {len(self.intel_sources)} intelligence sources")
            else:
                # Create default sources if file doesn't exist
                self.intel_sources = [
                    {"name": "MITRE ATT&CK", "url": "https://attack.mitre.org/", "type": "framework", "enabled": True},
                    {"name": "US-CERT", "url": "https://www.us-cert.gov/ncas/alerts", "type": "alerts", "enabled": True},
                    {"name": "AlienVault OTX", "url": "https://otx.alienvault.com/", "type": "indicators", "enabled": True}
                ]
                os.makedirs(self.config_file.parent, exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(self.intel_sources, f, indent=2)
                self.logger.info("Created default intelligence sources")
        except Exception as e:
            self.logger.error(f"Error loading intelligence sources: {e}")
            self.intel_sources = []

    def load_database(self):
        """Load threat database from file"""
        try:
            if self.database_file.exists():
                with open(self.database_file, 'r') as f:
                    data = json.load(f)
                    self.threat_database = data.get("threats", [])
                    self.last_update = data.get("last_update")
                    self.logger.info(f"Loaded {len(self.threat_database)} threats from database")
            else:
                self.threat_database = []
                self.last_update = None
        except Exception as e:
            self.logger.error(f"Error loading threat database: {e}")
            self.threat_database = []
            self.last_update = None

    def save_database(self):
        """Save threat database to file"""
        try:
            os.makedirs(self.database_file.parent, exist_ok=True)
            with open(self.database_file, 'w') as f:
                json.dump({
                    "threats": self.threat_database,
                    "last_update": datetime.now().isoformat()
                }, f, indent=2)
            self.logger.info(f"Saved {len(self.threat_database)} threats to database")
        except Exception as e:
            self.logger.error(f"Error saving threat database: {e}")

    def add_threat(self, threat_type, name, description, source, severity="medium", indicators=None):
        """Add a new threat to the database"""
        # Generate a unique ID for the threat
        threat_id = hashlib.md5(f"{name}:{description}:{source}".encode()).hexdigest()
        
        # Check if this threat already exists
        for threat in self.threat_database:
            if threat.get("id") == threat_id:
                self.logger.debug(f"Threat {name} already exists in database")
                return False
        
        # Create the threat entry
        threat = {
            "id": threat_id,
            "type": threat_type,
            "name": name,
            "description": description,
            "source": source,
            "severity": severity,
            "indicators": indicators or [],
            "discovered": datetime.now().isoformat()
        }
        
        # Add to database
        self.threat_database.append(threat)
        self.logger.info(f"Added new threat: {name} ({threat_type}) from {source}")
        
        # Save database
        self.save_database()
        
        # Emit event if event bus is available
        if self.event_bus:
            self.event_bus.emit("NEW_THREAT", {
                "threat": threat,
                "source_agent": self.name
            })
        
        return True

    def fetch_intelligence(self):
        """Fetch threat intelligence from configured sources (simulation)"""
        self.logger.info("Fetching threat intelligence")
        
        # In a real implementation, this would make HTTP requests to the sources
        # For simulation, we'll generate some random threats
        
        # Simulated threat types
        threat_types = ["malware", "ransomware", "phishing", "vulnerability", "exploit"]
        
        # Simulated severity levels
        severity_levels = ["low", "medium", "high", "critical"]
        
        # Simulated threat names and descriptions
        simulated_threats = [
            {
                "name": "Emotet Variant",
                "description": "New variant of Emotet malware with enhanced evasion techniques"
            },
            {
                "name": "CVE-2023-1234",
                "description": "Remote code execution vulnerability in popular web server software"
            },
            {
                "name": "SpearPhish Campaign",
                "description": "Targeted phishing campaign against financial institutions"
            },
            {
                "name": "RansomCloud",
                "description": "New ransomware targeting cloud storage providers"
            },
            {
                "name": "Supply Chain Attack",
                "description": "Compromise of software supply chain affecting multiple vendors"
            }
        ]
        
        # Simulate finding new threats
        new_threats_count = 0
        for source in self.intel_sources:
            if source.get("enabled", True):
                # Randomly decide if we find a threat from this source
                if random.random() < 0.3:  # 30% chance of finding a threat
                    # Pick a random threat
                    threat = random.choice(simulated_threats)
                    
                    # Add some randomness to make it unique
                    name = f"{threat['name']} {random.randint(1000, 9999)}"
                    
                    # Add the threat to our database
                    if self.add_threat(
                        random.choice(threat_types),
                        name,
                        threat["description"],
                        source["name"],
                        random.choice(severity_levels)
                    ):
                        new_threats_count += 1
        
        self.logger.info(f"Found {new_threats_count} new threats")
        return new_threats_count

    def gather_intelligence(self):
        """Background thread for gathering threat intelligence"""
        self.logger.info("Starting threat intelligence gathering")
        self.running = True
        
        while self.running:
            # Check if it's time to update
            current_time = datetime.now()
            if self.last_update is None or (
                    isinstance(self.last_update, str) and 
                    datetime.fromisoformat(self.last_update) + timedelta(seconds=self.update_interval) < current_time
                ):
                self.fetch_intelligence()
                self.last_update = current_time.isoformat()
            
            # Sleep until next check
            time.sleep(60)  # Check every minute if it's time to update

    def start(self):
        """Start the threat intelligence gathering in a background thread"""
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.gather_intelligence, daemon=True)
            self._thread.start()
            self.logger.info("Threat intelligence gathering started")
            return True
        return False

    def stop(self):
        """Stop the threat intelligence gathering"""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
            self.logger.info("Threat intelligence gathering stopped")
            return True
        return False

    def heartbeat(self):
        """Check if the agent is running properly"""
        if self._thread and self._thread.is_alive():
            self.logger.debug("Heartbeat check: OK")
            return True
        self.logger.warning("Heartbeat check: Failed - thread not running")
        return False

    def run(self):
        """Run the agent (for CLI execution)"""
        # For CLI execution, do an immediate intelligence fetch
        new_threats = self.fetch_intelligence()
        return {
            "status": "completed", 
            "new_threats": new_threats,
            "total_threats": len(self.threat_database)
        }

    def handle_event(self, event):
        """Handle events from the event bus"""
        event_type = event.get("type", "")
        data = event.get("data", {})
        
        if event_type == "FORCE_INTEL_UPDATE":
            # Force an immediate intelligence update
            new_threats = self.fetch_intelligence()
            return new_threats > 0
        
        elif event_type == "ADD_INTEL_SOURCE":
            # Add a new intelligence source
            if all(k in data for k in ["name", "url", "type"]):
                source = {
                    "name": data["name"],
                    "url": data["url"],
                    "type": data["type"],
                    "enabled": data.get("enabled", True)
                }
                self.intel_sources.append(source)
                with open(self.config_file, 'w') as f:
                    json.dump(self.intel_sources, f, indent=2)
                self.logger.info(f"Added new intelligence source: {source['name']}")
                return True
        
        return False

    def search_threats(self, query, field="name"):
        """Search for threats in the database"""
        results = []
        query = query.lower()
        
        for threat in self.threat_database:
            if query in threat.get(field, "").lower():
                results.append(threat)
        
        return results

    def get_recent_threats(self, days=7, severity=None):
        """Get recent threats from the database"""
        results = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for threat in self.threat_database:
            try:
                discovered = datetime.fromisoformat(threat.get("discovered", ""))
                if discovered >= cutoff_date:
                    if severity is None or threat.get("severity") == severity:
                        results.append(threat)
            except (ValueError, TypeError):
                # Skip threats with invalid dates
                pass
        
        return results

    def diagnose(self):
        """Return diagnostic information about the agent"""
        return {
            "name": self.name,
            "status": "running" if self.heartbeat() else "stopped",
            "sources_count": len(self.intel_sources),
            "threats_count": len(self.threat_database),
            "last_update": self.last_update,
            "thread_alive": self._thread.is_alive() if self._thread else False
        }
