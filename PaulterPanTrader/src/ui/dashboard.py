"""
Dashboard Module
Provides a user interface for displaying trading signals and market data.
"""

import logging
import threading
import time
import os
from typing import Dict, List, Any
import json
import datetime

logger = logging.getLogger("PaulterPan.Dashboard")

class Dashboard:
    """Dashboard for displaying trading signals and market data"""
    
    def __init__(self, signal_aggregator):
        """
        Initialize the dashboard
        
        Args:
            signal_aggregator: SignalAggregator instance
        """
        self.signal_aggregator = signal_aggregator
        self.running = False
        self.update_interval = 60  # Update every 60 seconds
        self.thread = None
        logger.info("Dashboard initialized")
        
    def start(self):
        """Start the dashboard update thread"""
        if self.running:
            logger.warning("Dashboard is already running")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._update_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Dashboard started")
        
        # Display initial dashboard
        self.display_dashboard()
        
    def stop(self):
        """Stop the dashboard update thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        logger.info("Dashboard stopped")
        
    def _update_loop(self):
        """Background thread for updating signals"""
        while self.running:
            try:
                self.signal_aggregator.update_signals()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in dashboard update loop: {str(e)}")
                time.sleep(5)  # Sleep briefly before retrying
                
    def display_dashboard(self):
        """Display the main dashboard"""
        self._clear_screen()
        self._print_header()
        self._print_top_signals()
        self._print_asset_breakdown()
        self._print_footer()
        
    def _clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def _print_header(self):
        """Print dashboard header"""
        print("=" * 80)
        print(f"  PAULTERPAN TRADING SIGNALS  |  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
    def _print_top_signals(self):
        """Print top trading signals"""
        signals = self.signal_aggregator.get_top_signals(10)
        
        if not signals:
            print("No trading signals available at this time.")
            print()
            return
            
        print("TOP TRADING SIGNALS:")
        print("-" * 80)
        print(f"{'ASSET TYPE':<12} {'SYMBOL':<10} {'DIRECTION':<8} {'CONFIDENCE':<10} {'TIMEFRAME':<8} {'STRATEGY':<20}")
        print("-" * 80)
        
        for signal in signals:
            confidence_str = f"{signal.confidence:.2f}"
            print(f"{signal.asset_type:<12} {signal.symbol:<10} {signal.direction:<8} {confidence_str:<10} "
                  f"{signal.timeframe:<8} {signal.strategy_name:<20}")
                  
        print()
        
    def _print_asset_breakdown(self):
        """Print breakdown by asset type"""
        signals = self.signal_aggregator.signals
        
        # Group signals by asset type
        asset_groups = {}
        for signal in signals:
            if signal.asset_type not in asset_groups:
                asset_groups[signal.asset_type] = []
            asset_groups[signal.asset_type].append(signal)
            
        if not asset_groups:
            return
            
        print("SIGNALS BY ASSET TYPE:")
        print("-" * 80)
        
        for asset_type, asset_signals in asset_groups.items():
            print(f"{asset_type.upper()} ({len(asset_signals)} signals)")
            
            # Print top 3 signals for this asset type
            for i, signal in enumerate(sorted(asset_signals, key=lambda x: x.confidence, reverse=True)[:3]):
                print(f"  {i+1}. {signal.symbol} - {signal.direction.upper()} "
                      f"({signal.confidence:.2f}) - {signal.strategy_name}")
                      
            print()
            
    def _print_footer(self):
        """Print dashboard footer"""
        print("=" * 80)
        print("  Press Ctrl+C to exit  |  Data updates every 60 seconds")
        print("=" * 80)
        
    def generate_web_dashboard(self):
        """Generate data for web dashboard"""
        signals = self.signal_aggregator.signals
        
        dashboard_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'signals_count': len(signals),
            'top_signals': [s.to_dict() for s in self.signal_aggregator.get_top_signals(10)],
            'asset_breakdown': {}
        }
        
        # Group signals by asset type
        for signal in signals:
            if signal.asset_type not in dashboard_data['asset_breakdown']:
                dashboard_data['asset_breakdown'][signal.asset_type] = []
            dashboard_data['asset_breakdown'][signal.asset_type].append(signal.to_dict())
            
        return dashboard_data
        
    def save_web_dashboard(self, output_path='public/dashboard_data.json'):
        """Save dashboard data for web interface"""
        data = self.generate_web_dashboard()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert datetime objects to strings
        json_data = json.dumps(data, default=str, indent=2)
        
        with open(output_path, 'w') as f:
            f.write(json_data)
            
        logger.info(f"Dashboard data saved to {output_path}")
