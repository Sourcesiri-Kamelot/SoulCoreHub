# modules/evove_vision.py
"""
EvoVe Vision Module
-----------------
Provides visual error mapping and system visualization.
"""

import logging
import os
import json
import time
import threading
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger("EvoVe.Vision")

class EvoVeVision:
    """Provides visual error mapping and system visualization."""
    
    def __init__(self, evove):
        """Initialize the EvoVe vision module."""
        self.evove = evove
        self.config = evove.config.get("vision", {})
        self.output_dir = self.config.get("output_dir", "data/vision")
        self.update_interval = self.config.get("update_interval", 300)  # 5 minutes
        self.running = False
        self.vision_thread = None
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
    def start(self):
        """Start the vision module."""
        if self.running:
            logger.warning("Vision module is already running")
            return
            
        self.running = True
        logger.info("Starting EvoVe vision module")
        
        self.vision_thread = threading.Thread(target=self._vision_loop)
        self.vision_thread.daemon = True
        self.vision_thread.start()
        
    def stop(self):
        """Stop the vision module."""
        if not self.running:
            logger.warning("Vision module is not running")
            return
            
        self.running = False
        logger.info("Stopping EvoVe vision module")
        
        if self.vision_thread:
            self.vision_thread.join(timeout=5)
    
    def _vision_loop(self):
        """Main vision loop."""
        while self.running:
            try:
                self.generate_system_map()
                self.generate_error_heatmap()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in vision loop: {e}")
                time.sleep(60)  # Shorter interval on error
    
    def generate_system_map(self):
        """Generate a visual map of the system components and their relationships."""
        try:
            logger.debug("Generating system map")
            
            # Create a graph
            G = nx.DiGraph()
            
            # Add nodes for core components
            G.add_node("EvoVe", type="core", status="active")
            G.add_node("MCP Server", type="core", status="unknown")
            G.add_node("Anima", type="agent", status="unknown")
            G.add_node("GPTSoul", type="agent", status="unknown")
            G.add_node("Azür", type="agent", status="unknown")
            
            # Add nodes for modules
            modules = [
                "RepairOps", "SystemMonitor", "MCPBridge", "CLISync", 
                "VoiceInterface", "AnomalyWatcher", "NetSense", "RepairBrain",
                "SecureStorage", "VoiceCommand"
            ]
            
            for module in modules:
                G.add_node(module, type="module", status="unknown")
                G.add_edge("EvoVe", module)
            
            # Add connections
            G.add_edge("EvoVe", "MCP Server")
            G.add_edge("MCP Server", "Anima")
            G.add_edge("MCP Server", "GPTSoul")
            G.add_edge("MCP Server", "Azür")
            G.add_edge("MCPBridge", "MCP Server")
            G.add_edge("RepairOps", "MCP Server")
            G.add_edge("VoiceInterface", "Anima")
            
            # Update status based on actual system state
            if hasattr(self.evove, "mcp_bridge"):
                G.nodes["MCP Server"]["status"] = "active" if self.evove.mcp_bridge.connected else "inactive"
                G.nodes["MCPBridge"]["status"] = "active"
            
            if hasattr(self.evove, "system_monitor"):
                G.nodes["SystemMonitor"]["status"] = "active" if self.evove.system_monitor.running else "inactive"
            
            if hasattr(self.evove, "repair_ops"):
                G.nodes["RepairOps"]["status"] = "active"
            
            if hasattr(self.evove, "cli_sync"):
                G.nodes["CLISync"]["status"] = "active" if self.evove.cli_sync.running else "inactive"
            
            if hasattr(self.evove, "voice"):
                G.nodes["VoiceInterface"]["status"] = "active" if self.evove.voice.running else "inactive"
            
            # Check if Anima is running
            anima_running = False
            try:
                import subprocess
                result = subprocess.run(["pgrep", "-f", "anima_voice.py"], capture_output=True, text=True)
                anima_running = result.returncode == 0
            except:
                pass
            G.nodes["Anima"]["status"] = "active" if anima_running else "inactive"
            
            # Draw the graph
            plt.figure(figsize=(12, 8))
            
            # Define node colors based on type and status
            node_colors = []
            for node in G.nodes():
                node_type = G.nodes[node].get("type", "unknown")
                node_status = G.nodes[node].get("status", "unknown")
                
                if node_status == "active":
                    if node_type == "core":
                        node_colors.append("#4CAF50")  # Green
                    elif node_type == "agent":
                        node_colors.append("#2196F3")  # Blue
                    else:
                        node_colors.append("#9C27B0")  # Purple
                elif node_status == "inactive":
                    node_colors.append("#FFC107")  # Yellow
                else:
                    node_colors.append("#9E9E9E")  # Gray
            
            # Define node positions
            pos = nx.spring_layout(G, seed=42)
            
            # Draw nodes
            nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=700, alpha=0.8)
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, arrows=True)
            
            # Draw labels
            nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")
            
            # Add title and timestamp
            plt.title("SoulCoreHub System Map")
            plt.text(0.01, 0.01, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                    transform=plt.gca().transAxes, fontsize=8)
            
            # Remove axis
            plt.axis("off")
            
            # Save the figure
            output_file = os.path.join(self.output_dir, "system_map.png")
            plt.savefig(output_file, dpi=150, bbox_inches="tight")
            plt.close()
            
            logger.info(f"System map generated: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate system map: {e}")
            return None
    
    def generate_error_heatmap(self):
        """Generate a heatmap of errors in the system."""
        try:
            logger.debug("Generating error heatmap")
            
            # Collect error data
            error_data = self._collect_error_data()
            if not error_data:
                logger.warning("No error data available for heatmap")
                return None
            
            # Create the heatmap
            plt.figure(figsize=(12, 8))
            
            # Extract components and time periods
            components = list(error_data.keys())
            time_periods = []
            
            # Find all unique time periods
            for component, periods in error_data.items():
                for period in periods:
                    if period["period"] not in time_periods:
                        time_periods.append(period["period"])
            
            # Sort time periods
            time_periods.sort()
            
            # Create the heatmap data
            heatmap_data = np.zeros((len(components), len(time_periods)))
            
            for i, component in enumerate(components):
                for j, period in enumerate(time_periods):
                    # Find the error count for this component and period
                    for p in error_data[component]:
                        if p["period"] == period:
                            heatmap_data[i, j] = p["count"]
                            break
            
            # Create the heatmap
            plt.imshow(heatmap_data, cmap="YlOrRd", aspect="auto")
            
            # Add colorbar
            cbar = plt.colorbar()
            cbar.set_label("Error Count")
            
            # Add labels
            plt.xticks(range(len(time_periods)), time_periods, rotation=45, ha="right")
            plt.yticks(range(len(components)), components)
            
            plt.title("System Error Heatmap")
            plt.tight_layout()
            
            # Save the figure
            output_file = os.path.join(self.output_dir, "error_heatmap.png")
            plt.savefig(output_file, dpi=150, bbox_inches="tight")
            plt.close()
            
            logger.info(f"Error heatmap generated: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate error heatmap: {e}")
            return None
    
    def _collect_error_data(self):
        """Collect error data from logs."""
        error_data = {}
        
        # Define time periods (last 24 hours in 3-hour intervals)
        now = datetime.now()
        periods = []
        for i in range(8):
            end_time = now - timedelta(hours=i*3)
            start_time = end_time - timedelta(hours=3)
            periods.append({
                "start": start_time,
                "end": end_time,
                "label": f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
            })
        
        # Define components to check
        components = [
            {"name": "EvoVe", "log_pattern": "EvoVe"},
            {"name": "MCP Server", "log_pattern": "MCP"},
            {"name": "Anima", "log_pattern": "Anima"},
            {"name": "System", "log_pattern": "System"},
            {"name": "Network", "log_pattern": "Network"},
            {"name": "Security", "log_pattern": "Security"}
        ]
        
        # Check log files
        log_files = [
            "logs/evove.log",
            "logs/mcp_server.log",
            "logs/evove_health.log"
        ]
        
        for log_file in log_files:
            if not os.path.exists(log_file):
                continue
                
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    
                for line in lines:
                    # Check if line contains an error
                    if "error" in line.lower() or "exception" in line.lower() or "critical" in line.lower():
                        # Extract timestamp
                        timestamp_match = None
                        try:
                            # Try different timestamp formats
                            formats = [
                                r'\[(.*?)\]',  # [2023-01-01 12:34:56]
                                r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',  # 2023-01-01 12:34:56
                                r'(\w{3} \d{2} \d{2}:\d{2}:\d{2})'  # Jan 01 12:34:56
                            ]
                            
                            for format_pattern in formats:
                                match = re.search(format_pattern, line)
                                if match:
                                    timestamp_match = match.group(1)
                                    break
                        except:
                            pass
                        
                        if not timestamp_match:
                            continue
                            
                        try:
                            # Parse timestamp
                            try:
                                timestamp = datetime.strptime(timestamp_match, '%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                try:
                                    timestamp = datetime.strptime(timestamp_match, '%b %d %H:%M:%S')
                                    # Add current year since month/day format doesn't include year
                                    timestamp = timestamp.replace(year=now.year)
                                except ValueError:
                                    continue
                            
                            # Find the period this timestamp belongs to
                            for period in periods:
                                if period["start"] <= timestamp <= period["end"]:
                                    period_label = period["label"]
                                    
                                    # Find which component this error belongs to
                                    for component in components:
                                        if component["log_pattern"].lower() in line.lower():
                                            component_name = component["name"]
                                            
                                            # Add to error data
                                            if component_name not in error_data:
                                                error_data[component_name] = []
                                            
                                            # Check if period already exists
                                            period_exists = False
                                            for p in error_data[component_name]:
                                                if p["period"] == period_label:
                                                    p["count"] += 1
                                                    period_exists = True
                                                    break
                                            
                                            if not period_exists:
                                                error_data[component_name].append({
                                                    "period": period_label,
                                                    "count": 1
                                                })
                                            
                                            break
                                    break
                        except:
                            continue
            except Exception as e:
                logger.error(f"Error reading log file {log_file}: {e}")
        
        return error_data
    
    def generate_config_conflict_map(self):
        """Generate a visualization of configuration conflicts."""
        try:
            logger.debug("Generating configuration conflict map")
            
            # Collect configuration files
            config_files = []
            for root, _, files in os.walk("config"):
                for file in files:
                    if file.endswith(".json") or file.endswith(".yaml") or file.endswith(".yml"):
                        config_files.append(os.path.join(root, file))
            
            if not config_files:
                logger.warning("No configuration files found")
                return None
            
            # Parse configurations and look for conflicts
            configs = {}
            conflicts = []
            
            for config_file in config_files:
                try:
                    if config_file.endswith(".json"):
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                    else:
                        # For YAML files
                        import yaml
                        with open(config_file, 'r') as f:
                            config = yaml.safe_load(f)
                    
                    configs[config_file] = config
                except Exception as e:
                    logger.error(f"Failed to parse config file {config_file}: {e}")
            
            # Check for conflicts
            for file1, config1 in configs.items():
                for file2, config2 in configs.items():
                    if file1 != file2:
                        # Check for overlapping keys with different values
                        self._check_conflicts(file1, config1, file2, config2, "", conflicts)
            
            if not conflicts:
                logger.info("No configuration conflicts found")
                return None
            
            # Create a graph to visualize conflicts
            G = nx.Graph()
            
            # Add nodes for config files
            for config_file in configs:
                G.add_node(os.path.basename(config_file), type="config")
            
            # Add edges for conflicts
            for conflict in conflicts:
                G.add_edge(
                    os.path.basename(conflict["file1"]),
                    os.path.basename(conflict["file2"]),
                    key=conflict["key"],
                    value1=conflict["value1"],
                    value2=conflict["value2"]
                )
            
            # Draw the graph
            plt.figure(figsize=(10, 8))
            
            pos = nx.spring_layout(G, seed=42)
            nx.draw_networkx_nodes(G, pos, node_color="#FF9800", node_size=700, alpha=0.8)
            nx.draw_networkx_edges(G, pos, width=2.0, alpha=0.7, edge_color="#E91E63")
            nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")
            
            # Add edge labels (conflict keys)
            edge_labels = {(u, v): d["key"] for u, v, d in G.edges(data=True)}
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
            
            plt.title("Configuration Conflicts")
            plt.axis("off")
            
            # Save the figure
            output_file = os.path.join(self.output_dir, "config_conflicts.png")
            plt.savefig(output_file, dpi=150, bbox_inches="tight")
            plt.close()
            
            # Also save conflicts as JSON
            conflicts_file = os.path.join(self.output_dir, "config_conflicts.json")
            with open(conflicts_file, 'w') as f:
                json.dump(conflicts, f, indent=2)
            
            logger.info(f"Configuration conflict map generated: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate configuration conflict map: {e}")
            return None
    
    def _check_conflicts(self, file1, config1, file2, config2, prefix, conflicts):
        """Recursively check for conflicts between two configurations."""
        if isinstance(config1, dict) and isinstance(config2, dict):
            # Check common keys
            common_keys = set(config1.keys()) & set(config2.keys())
            for key in common_keys:
                new_prefix = f"{prefix}.{key}" if prefix else key
                if isinstance(config1[key], (dict, list

def _check_conflicts(self, file1, config1, file2, config2, prefix, conflicts):
        """Recursively check for conflicts between two configurations."""
        if isinstance(config1, dict) and isinstance(config2, dict):
            # Check common keys
            common_keys = set(config1.keys()) & set(config2.keys())
            for key in common_keys:
                new_prefix = f"{prefix}.{key}" if prefix else key
                if isinstance(config1[key], (dict, list)) and isinstance(config2[key], (dict, list)):
                    # Recursively check nested structures
                    self._check_conflicts(file1, config1[key], file2, config2[key], new_prefix, conflicts)
                elif config1[key] != config2[key]:
                    # Found a conflict
                    conflicts.append({
                        "file1": file1,
                        "file2": file2,
                        "key": new_prefix,
                        "value1": config1[key],
                        "value2": config2[key]
                    })
        elif isinstance(config1, list) and isinstance(config2, list):
            # For lists, we only check if they have the same length
            if len(config1) != len(config2):
                conflicts.append({
                    "file1": file1,
                    "file2": file2,
                    "key": prefix,
                    "value1": f"List with {len(config1)} items",
                    "value2": f"List with {len(config2)} items"
                })



