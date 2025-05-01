# modules/anomaly_watcher.py
"""
Anomaly Pattern Detection Engine
-------------------------------
Detects patterns in system failures and anomalies.
Uses machine learning to predict and prevent future issues.
"""

import logging
import os
import re
import time
import json
import threading
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import pickle

logger = logging.getLogger("EvoVe.AnomalyWatcher")

class AnomalyWatcher:
    """Watches for anomalies in system behavior and logs."""
    
    def __init__(self, evove):
        """Initialize the anomaly watcher."""
        self.evove = evove
        self.config = evove.config.get("anomaly", {})
        self.running = False
        self.watch_thread = None
        self.anomaly_patterns = []
        self.log_vectors = []
        self.error_history = defaultdict(list)
        self.model_path = "data/anomaly_model.pkl"
        self.max_history = self.config.get("max_history", 1000)
        self.scan_interval = self.config.get("scan_interval", 300)  # 5 minutes
        self.threshold = self.config.get("threshold", 0.7)
        
        # Load existing model if available
        self._load_model()
        
    def start(self):
        """Start the anomaly watcher."""
        if self.running:
            logger.warning("Anomaly watcher is already running")
            return
            
        self.running = True
        logger.info("Starting anomaly watcher")
        
        self.watch_thread = threading.Thread(target=self._watch_loop)
        self.watch_thread.daemon = True
        self.watch_thread.start()
        
    def stop(self):
        """Stop the anomaly watcher."""
        if not self.running:
            logger.warning("Anomaly watcher is not running")
            return
            
        self.running = False
        logger.info("Stopping anomaly watcher")
        
        if self.watch_thread:
            self.watch_thread.join(timeout=5)
            
        # Save model before stopping
        self._save_model()
        
    def _watch_loop(self):
        """Main watching loop."""
        while self.running:
            try:
                self._scan_logs()
                self._analyze_patterns()
                time.sleep(self.scan_interval)
            except Exception as e:
                logger.error(f"Error in anomaly watch loop: {e}")
                time.sleep(60)  # Shorter interval on error
    
    def _scan_logs(self):
        """Scan log files for anomalies."""
        logger.debug("Scanning logs for anomalies")
        
        log_files = [
            "logs/evove.log",
            "logs/mcp_server.log",
            "logs/evove_health.log"
        ]
        
        for log_file in log_files:
            if not os.path.exists(log_file):
                continue
                
            try:
                # Read the log file
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                
                # Process only the last N lines to avoid reprocessing the entire file
                last_n = min(1000, len(lines))
                for line in lines[-last_n:]:
                    self._process_log_line(line, log_file)
                    
            except Exception as e:
                logger.error(f"Error scanning log file {log_file}: {e}")
    
    def _process_log_line(self, line, log_file):
        """Process a single log line."""
        # Extract timestamp and log level if available
        timestamp_match = re.search(r'\[(.*?)\]', line)
        timestamp = timestamp_match.group(1) if timestamp_match else None
        
        # Check for errors and exceptions
        if re.search(r'error|exception|traceback|critical|fail', line, re.IGNORECASE):
            # Extract the error type
            error_type = "unknown"
            error_match = re.search(r'(Error|Exception|Traceback)[\s\:]+(.*?)[\s\:]', line)
            if error_match:
                error_type = error_match.group(1)
            
            # Add to error history
            self.error_history[error_type].append({
                'timestamp': timestamp,
                'file': log_file,
                'line': line.strip()
            })
            
            # Trim history if needed
            if len(self.error_history[error_type]) > self.max_history:
                self.error_history[error_type] = self.error_history[error_type][-self.max_history:]
            
            # Vectorize the log line for pattern matching
            vector = self._vectorize_log(line)
            if vector:
                self.log_vectors.append({
                    'vector': vector,
                    'line': line.strip(),
                    'file': log_file,
                    'timestamp': timestamp,
                    'error_type': error_type
                })
                
                # Trim vectors if needed
                if len(self.log_vectors) > self.max_history:
                    self.log_vectors = self.log_vectors[-self.max_history:]
    
    def _vectorize_log(self, log_line):
        """Convert a log line to a feature vector."""
        # This is a simple vectorization approach
        # In a production system, you might use more sophisticated NLP techniques
        
        # Extract features
        features = {
            'has_error': 1 if re.search(r'error', log_line, re.IGNORECASE) else 0,
            'has_exception': 1 if re.search(r'exception', log_line, re.IGNORECASE) else 0,
            'has_traceback': 1 if re.search(r'traceback', log_line, re.IGNORECASE) else 0,
            'has_critical': 1 if re.search(r'critical', log_line, re.IGNORECASE) else 0,
            'has_warning': 1 if re.search(r'warning', log_line, re.IGNORECASE) else 0,
            'has_fail': 1 if re.search(r'fail', log_line, re.IGNORECASE) else 0,
            'has_timeout': 1 if re.search(r'timeout', log_line, re.IGNORECASE) else 0,
            'has_connection': 1 if re.search(r'connection', log_line, re.IGNORECASE) else 0,
            'has_memory': 1 if re.search(r'memory', log_line, re.IGNORECASE) else 0,
            'has_disk': 1 if re.search(r'disk', log_line, re.IGNORECASE) else 0,
            'has_cpu': 1 if re.search(r'cpu', log_line, re.IGNORECASE) else 0,
            'has_mcp': 1 if re.search(r'mcp', log_line, re.IGNORECASE) else 0,
            'has_anima': 1 if re.search(r'anima', log_line, re.IGNORECASE) else 0,
            'has_evove': 1 if re.search(r'evove', log_line, re.IGNORECASE) else 0,
            'length': len(log_line)
        }
        
        # Convert to vector
        return list(features.values())
    
    def _analyze_patterns(self):
        """Analyze patterns in the collected data."""
        if not self.log_vectors:
            return
            
        logger.debug("Analyzing anomaly patterns")
        
        # Group errors by type
        error_counts = Counter([v['error_type'] for v in self.log_vectors])
        
        # Check for frequent errors
        for error_type, count in error_counts.items():
            if count >= 3:  # If an error occurs 3 or more times
                recent_errors = [v for v in self.log_vectors if v['error_type'] == error_type][-10:]
                
                # Check if these errors occurred close together in time
                if self._check_temporal_pattern(recent_errors):
                    pattern = {
                        'error_type': error_type,
                        'count': count,
                        'examples': [e['line'] for e in recent_errors[:3]],
                        'detected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Check if this is a new pattern
                    if not self._pattern_exists(pattern):
                        self.anomaly_patterns.append(pattern)
                        self._report_anomaly(pattern)
    
    def _check_temporal_pattern(self, errors):
        """Check if errors form a temporal pattern."""
        if len(errors) < 3:
            return False
            
        # Check if timestamps are available
        if not all('timestamp' in e and e['timestamp'] for e in errors):
            return True  # If we can't check timestamps, assume it's a pattern
            
        try:
            # Parse timestamps
            timestamps = []
            for e in errors:
                try:
                    dt = datetime.strptime(e['timestamp'], '%Y-%m-%d %H:%M:%S')
                    timestamps.append(dt)
                except (ValueError, TypeError):
                    continue
            
            if len(timestamps) < 3:
                return True  # Not enough valid timestamps, assume it's a pattern
                
            # Sort timestamps
            timestamps.sort()
            
            # Check if all errors occurred within a short time window
            time_window = timedelta(minutes=30)
            return (timestamps[-1] - timestamps[0]) <= time_window
            
        except Exception:
            return True  # If there's an error parsing timestamps, assume it's a pattern
    
    def _pattern_exists(self, pattern):
        """Check if a pattern already exists in our records."""
        for p in self.anomaly_patterns:
            if p['error_type'] == pattern['error_type'] and p['count'] <= pattern['count']:
                return True
        return False
    
    def _report_anomaly(self, pattern):
        """Report a detected anomaly pattern."""
        logger.warning(f"Anomaly pattern detected: {pattern['error_type']} ({pattern['count']} occurrences)")
        logger.warning(f"Examples: {pattern['examples'][0]}")
        
        # Get repair suggestion
        suggestion = self._get_repair_suggestion(pattern)
        
        # Log the suggestion
        if suggestion:
            logger.info(f"Repair suggestion: {suggestion}")
            
        # Notify the system
        if hasattr(self.evove, 'mcp_bridge') and self.evove.mcp_bridge.connected:
            self.evove.mcp_bridge.send_message({
                'type': 'anomaly_detected',
                'pattern': pattern,
                'suggestion': suggestion
            })
    
    def _get_repair_suggestion(self, pattern):
        """Get a repair suggestion for an anomaly pattern."""
        # This is where you could integrate with GPT-4 or Amazon Q
        # For now, we'll use simple rule-based suggestions
        
        error_type = pattern['error_type'].lower()
        examples = '\n'.join(pattern['examples'])
        
        if 'connection' in error_type or 'timeout' in examples.lower():
            return "Check network connectivity and ensure all services are running."
        elif 'memory' in error_type or 'memory' in examples.lower():
            return "Possible memory leak. Consider restarting services or increasing available memory."
        elif 'disk' in error_type or 'disk' in examples.lower():
            return "Check disk space and clean up unnecessary files."
        elif 'mcp' in error_type or 'mcp' in examples.lower():
            return "MCP server may need to be restarted. Run scripts/check_mcp_health.sh."
        else:
            return "Review recent system changes and check logs for more details."
    
    def _load_model(self):
        """Load the anomaly detection model."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.anomaly_patterns = data.get('patterns', [])
                    self.log_vectors = data.get('vectors', [])
                    self.error_history = data.get('history', defaultdict(list))
                logger.info(f"Loaded anomaly model with {len(self.anomaly_patterns)} patterns")
            except Exception as e:
                logger.error(f"Failed to load anomaly model: {e}")
    
    def _save_model(self):
        """Save the anomaly detection model."""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'patterns': self.anomaly_patterns,
                    'vectors': self.log_vectors,
                    'history': self.error_history
                }, f)
            logger.info(f"Saved anomaly model with {len(self.anomaly_patterns)} patterns")
        except Exception as e:
            logger.error(f"Failed to save anomaly model: {e}")
    
    def get_anomaly_report(self):
        """Get a report of detected anomalies."""
        return {
            'patterns': self.anomaly_patterns,
            'error_counts': {k: len(v) for k, v in self.error_history.items()},
            'total_vectors': len(self.log_vectors)
        }



