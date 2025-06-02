#!/usr/bin/env python3
"""
System Monitor for Chaos Monkey Demo
This script monitors system resources and application health during chaos experiments.
"""

import psutil
import requests
import time
import threading
import logging
from datetime import datetime
import json
from typing import Dict, List
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from matplotlib.animation import FuncAnimation
import os


class SystemMonitor:
    """Monitor system resources and application health"""
    
    def __init__(self, app_url: str = "http://localhost:8080"):
        self.app_url = app_url
        self.monitoring = False
        self.metrics_history: List[Dict] = []
        self.graph_enabled = True
        self.output_dir = "monitoring_output"
        
        # Create output directory
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def collect_system_metrics(self) -> Dict:
        """Collect current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network_io = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'load_avg_1m': load_avg[0],
                    'load_avg_5m': load_avg[1],
                    'load_avg_15m': load_avg[2]
                },
                'memory': {
                    'total_gb': memory.total / (1024**3),
                    'available_gb': memory.available / (1024**3),
                    'percent': memory.percent,
                    'used_gb': memory.used / (1024**3)
                },
                'swap': {
                    'total_gb': swap.total / (1024**3),
                    'used_gb': swap.used / (1024**3),
                    'percent': swap.percent
                },
                'disk': {
                    'total_gb': disk.total / (1024**3),
                    'used_gb': disk.used / (1024**3),
                    'free_gb': disk.free / (1024**3),
                    'percent': (disk.used / disk.total) * 100,
                    'read_mb': disk_io.read_bytes / (1024**2) if disk_io else 0,
                    'write_mb': disk_io.write_bytes / (1024**2) if disk_io else 0
                },
                'network': {
                    'bytes_sent_mb': network_io.bytes_sent / (1024**2),
                    'bytes_recv_mb': network_io.bytes_recv / (1024**2),
                    'packets_sent': network_io.packets_sent,
                    'packets_recv': network_io.packets_recv
                },
                'processes': {
                    'count': process_count
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    def collect_app_metrics(self) -> Dict:
        """Collect application-specific metrics"""
        try:
            # Health check
            health_response = requests.get(f"{self.app_url}/health", timeout=5)
            health_data = health_response.json() if health_response.status_code == 200 else {}
            
            # App stats
            stats_response = requests.get(f"{self.app_url}/stats", timeout=5)
            stats_data = stats_response.json() if stats_response.status_code == 200 else {}
            
            return {
                'timestamp': datetime.now().isoformat(),
                'health': {
                    'status_code': health_response.status_code,
                    'response_time': health_response.elapsed.total_seconds(),
                    'status': health_data.get('status', 'unknown'),
                    'uptime': health_data.get('uptime', 'unknown')
                },
                'stats': stats_data,
                'connectivity': True
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Cannot connect to application: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'health': {
                    'status_code': 0,
                    'response_time': 0,
                    'status': 'unreachable',
                    'uptime': 'unknown'
                },
                'stats': {},
                'connectivity': False,
                'error': str(e)
            }
    
    def monitor_loop(self, interval: int = 10):
        """Main monitoring loop"""
        self.logger.info(f"🔍 Starting system monitoring (interval: {interval}s)")
        
        while self.monitoring:
            try:
                # Collect metrics
                system_metrics = self.collect_system_metrics()
                app_metrics = self.collect_app_metrics()
                
                # Combine metrics
                combined_metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'system': system_metrics,
                    'application': app_metrics
                }
                
                # Store in history
                self.metrics_history.append(combined_metrics)
                
                # Keep only last 100 entries to prevent memory issues
                if len(self.metrics_history) > 100:
                    self.metrics_history = self.metrics_history[-100:]
                
                # Print current status
                self._print_current_status(combined_metrics)
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def _print_current_status(self, metrics: Dict):
        """Print current system status with enhanced formatting"""
        try:
            system = metrics.get('system', {})
            app = metrics.get('application', {})
            
            # Enhanced terminal output with colors and formatting
            self._clear_screen()
            
            print("🔍" + "=" * 79)
            print(f"📊 CHAOS MONKEY SYSTEM MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("🔍" + "=" * 79)
            
            # System metrics with visual indicators
            if system:
                cpu = system.get('cpu', {})
                memory = system.get('memory', {})
                disk = system.get('disk', {})
                
                print(f"💻 SYSTEM RESOURCES:")
                
                # CPU with visual bar
                cpu_percent = cpu.get('percent', 0)
                cpu_bar = self._create_progress_bar(cpu_percent, 100)
                print(f"   CPU Usage: {cpu_bar} {cpu_percent:5.1f}% ({cpu.get('count', 0)} cores)")
                
                # Memory with visual bar
                memory_percent = memory.get('percent', 0)
                memory_bar = self._create_progress_bar(memory_percent, 100)
                print(f"   Memory:    {memory_bar} {memory_percent:5.1f}% " +
                      f"({memory.get('used_gb', 0):.1f}GB / {memory.get('total_gb', 0):.1f}GB)")
                
                # Disk with visual bar
                disk_percent = disk.get('percent', 0)
                disk_bar = self._create_progress_bar(disk_percent, 100)
                print(f"   Disk:      {disk_bar} {disk_percent:5.1f}% " +
                      f"({disk.get('used_gb', 0):.0f}GB / {disk.get('total_gb', 0):.0f}GB)")
                
                if cpu.get('load_avg_1m', 0) > 0:
                    print(f"   Load Avg:  {cpu.get('load_avg_1m', 0):.2f}, " +
                          f"{cpu.get('load_avg_5m', 0):.2f}, " +
                          f"{cpu.get('load_avg_15m', 0):.2f} (1m, 5m, 15m)")
            
            print()
            
            # Application metrics with enhanced formatting
            health = app.get('health', {})
            stats = app.get('stats', {})
            
            print(f"🌐 APPLICATION STATUS:")
            if app.get('connectivity', False):
                status = health.get('status', 'unknown').upper()
                status_icon = "✅" if status == "HEALTHY" else "⚠️" if status == "DEGRADED" else "❌"
                print(f"   Status:       {status_icon} {status}")
                
                response_time = health.get('response_time', 0) * 1000
                response_bar = self._create_response_time_bar(response_time)
                print(f"   Response:     {response_bar} {response_time:6.0f}ms")
                
                print(f"   Uptime:       {health.get('uptime', 'unknown')}")
                
                if stats:
                    total_req = stats.get('total_requests', 0)
                    error_count = stats.get('error_count', 0)
                    error_rate = stats.get('error_rate', 0) * 100
                    
                    print(f"   Requests:     {total_req:,}")
                    print(f"   Errors:       {error_count:,} ({error_rate:.1f}%)")
                    
                    # Error rate bar
                    if error_rate > 0:
                        error_bar = self._create_progress_bar(error_rate, 20, char='▓')
                        print(f"   Error Rate:   {error_bar} {error_rate:.1f}%")
            else:
                print(f"   Status:       ❌ UNREACHABLE")
                print(f"   Error:        {app.get('error', 'Unknown connection error')}")
            
            # Alert conditions with visual emphasis
            alerts = self._check_alerts(metrics)
            if alerts:
                print(f"\n🚨 ALERTS:")
                for i, alert in enumerate(alerts, 1):
                    print(f"   {i:2d}. ⚠️  {alert}")
            else:
                print(f"\n✅ No alerts - System operating normally")
            
            # Performance summary
            if len(self.metrics_history) > 5:
                self._print_performance_summary()
            
            print("🔍" + "=" * 79)
            print("📊 Press Ctrl+C to stop monitoring and generate final report")
            print("🔍" + "=" * 79)
            
        except Exception as e:
            self.logger.error(f"Error printing status: {e}")
    
    def _clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def _create_progress_bar(self, value: float, max_value: float, width: int = 20, char: str = '█') -> str:
        """Create a visual progress bar"""
        if max_value == 0:
            return '▱' * width
        
        filled = int((value / max_value) * width)
        filled = min(filled, width)
        
        # Color coding based on percentage
        if value / max_value < 0.5:
            color = '\033[92m'  # Green
        elif value / max_value < 0.8:
            color = '\033[93m'  # Yellow
        else:
            color = '\033[91m'  # Red
        
        reset_color = '\033[0m'
        
        bar = char * filled + '▱' * (width - filled)
        return f"{color}{bar}{reset_color}"
    
    def _create_response_time_bar(self, response_time_ms: float) -> str:
        """Create response time visualization"""
        # Good: < 100ms, OK: < 500ms, Slow: < 1000ms, Bad: >= 1000ms
        if response_time_ms < 100:
            return '🟢'
        elif response_time_ms < 500:
            return '🟡'
        elif response_time_ms < 1000:
            return '🟠'
        else:
            return '🔴'
    
    def _print_performance_summary(self):
        """Print performance summary from recent metrics"""
        try:
            recent_metrics = self.metrics_history[-10:]  # Last 10 data points
            
            cpu_values = [m.get('system', {}).get('cpu', {}).get('percent', 0) for m in recent_metrics]
            memory_values = [m.get('system', {}).get('memory', {}).get('percent', 0) for m in recent_metrics]
            response_times = [m.get('application', {}).get('health', {}).get('response_time', 0) * 1000 for m in recent_metrics]
            
            if cpu_values and memory_values and response_times:
                print(f"\n📈 PERFORMANCE TREND (Last 10 samples):")
                print(f"   CPU Avg:      {np.mean(cpu_values):.1f}% (min: {min(cpu_values):.1f}%, max: {max(cpu_values):.1f}%)")
                print(f"   Memory Avg:   {np.mean(memory_values):.1f}% (min: {min(memory_values):.1f}%, max: {max(memory_values):.1f}%)")
                print(f"   Response Avg: {np.mean(response_times):.0f}ms (min: {min(response_times):.0f}ms, max: {max(response_times):.0f}ms)")
        
        except Exception as e:
            self.logger.error(f"Error calculating performance summary: {e}")

    def start_monitoring(self, interval: int = 10):
        """Start monitoring in a separate thread"""
        self.monitoring = True
        monitor_thread = threading.Thread(target=self.monitor_loop, args=(interval,))
        monitor_thread.daemon = True
        monitor_thread.start()
        return monitor_thread
    
    def stop_monitoring(self):
        """Stop monitoring and generate final report"""
        self.monitoring = False
        self.logger.info("🛑 Monitoring stopped")
        
        # Generate comprehensive graphs and reports
        if self.metrics_history:
            print("\n📊 Generating final analysis and graphs...")
            self.generate_graphs()
            self.save_metrics_to_file()
            print("✅ Final report generated successfully!")
        else:
            print("⚠️ No data collected for analysis")
    
    def save_metrics_to_file(self, filename: str = None):
        """Save collected metrics to a JSON file"""
        if not filename:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
            self.logger.info(f"📁 Metrics saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")
    
    def plot_metrics(self, metric_name: str, last_n: int = 100):
        """Plot metrics over time"""
        try:
            # Filter history for the last N entries
            data_to_plot = self.metrics_history[-last_n:]
            
            if not data_to_plot:
                self.logger.warning("No data available to plot")
                return
            
            # Create DataFrame
            df = pd.DataFrame(data_to_plot)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Plot
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
            
            for column in df.columns:
                if column != 'timestamp' and isinstance(df[column].iloc[0], dict):
                    # Expand dict columns
                    dict_df = df[column].apply(pd.Series)
                    dict_df['timestamp'] = df['timestamp']
                    dict_df.set_index('timestamp', inplace=True)
                    dict_df.plot(ax=ax, legend=True)
                elif column == metric_name:
                    # Plot the selected metric
                    df.plot(x='timestamp', y=column, ax=ax, label=column, legend=True)
            
            plt.title(f"{metric_name} over time")
            plt.xlabel("Time")
            plt.ylabel(metric_name)
            plt.xticks(rotation=45)
            plt.grid()
            plt.tight_layout()
            
            # Save plot to file
            plot_filename = f"{metric_name}_plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(plot_filename)
            plt.show()
            self.logger.info(f"📈 Plot saved to {plot_filename}")
        
        except Exception as e:
            self.logger.error(f"Error generating plot: {e}")
    
    def generate_graphs(self, save_dir: str = None):
        """Generate comprehensive graphs from collected metrics"""
        if not self.metrics_history:
            self.logger.warning("No metrics data to plot")
            return
        
        save_dir = save_dir or self.output_dir
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Prepare data
            df = self._prepare_dataframe()
            
            # Generate multiple graphs
            self._plot_system_resources(df, save_dir, timestamp)
            self._plot_application_metrics(df, save_dir, timestamp)
            self._plot_combined_overview(df, save_dir, timestamp)
            self._plot_chaos_timeline(df, save_dir, timestamp)
            
            # Generate HTML dashboard
            self._generate_html_dashboard(save_dir, timestamp)
            
            self.logger.info(f"📊 Graphs generated in {save_dir}/")
            print(f"\n📊 VISUALIZATION COMPLETE!")
            print(f"   📁 Output directory: {save_dir}/")
            print(f"   📈 Generated graphs:")
            print(f"      • system_resources_{timestamp}.png")
            print(f"      • application_metrics_{timestamp}.png") 
            print(f"      • overview_{timestamp}.png")
            print(f"      • chaos_timeline_{timestamp}.png")
            print(f"   🌐 HTML Dashboard: dashboard_{timestamp}.html")
            
        except Exception as e:
            self.logger.error(f"Error generating graphs: {e}")
    
    def _prepare_dataframe(self) -> pd.DataFrame:
        """Convert metrics history to pandas DataFrame"""
        data = []
        
        for metric in self.metrics_history:
            timestamp = pd.to_datetime(metric['timestamp'])
            system = metric.get('system', {})
            app = metric.get('application', {})
            
            row = {
                'timestamp': timestamp,
                'cpu_percent': system.get('cpu', {}).get('percent', 0),
                'memory_percent': system.get('memory', {}).get('percent', 0),
                'disk_percent': system.get('disk', {}).get('percent', 0),
                'load_avg_1m': system.get('cpu', {}).get('load_avg_1m', 0),
                'response_time_ms': app.get('health', {}).get('response_time', 0) * 1000,
                'app_status': app.get('health', {}).get('status', 'unknown'),
                'total_requests': app.get('stats', {}).get('total_requests', 0),
                'error_count': app.get('stats', {}).get('error_count', 0),
                'error_rate': app.get('stats', {}).get('error_rate', 0) * 100,
                'connectivity': app.get('connectivity', False)
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def _plot_system_resources(self, df: pd.DataFrame, save_dir: str, timestamp: str):
        """Plot system resource usage over time"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('System Resource Usage Over Time', fontsize=16, fontweight='bold')
        
        # CPU Usage
        axes[0, 0].plot(df['timestamp'], df['cpu_percent'], 'b-', linewidth=2, label='CPU %')
        axes[0, 0].axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='Warning (80%)')
        axes[0, 0].axhline(y=90, color='red', linestyle='--', alpha=0.7, label='Critical (90%)')
        axes[0, 0].set_title('CPU Usage (%)', fontweight='bold')
        axes[0, 0].set_ylabel('Percentage')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].legend()
        axes[0, 0].set_ylim(0, 100)
        
        # Memory Usage
        axes[0, 1].plot(df['timestamp'], df['memory_percent'], 'g-', linewidth=2, label='Memory %')
        axes[0, 1].axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='Warning (80%)')
        axes[0, 1].axhline(y=90, color='red', linestyle='--', alpha=0.7, label='Critical (90%)')
        axes[0, 1].set_title('Memory Usage (%)', fontweight='bold')
        axes[0, 1].set_ylabel('Percentage')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].legend()
        axes[0, 1].set_ylim(0, 100)
        
        # Disk Usage
        axes[1, 0].plot(df['timestamp'], df['disk_percent'], 'purple', linewidth=2, label='Disk %')
        axes[1, 0].axhline(y=85, color='orange', linestyle='--', alpha=0.7, label='Warning (85%)')
        axes[1, 0].axhline(y=95, color='red', linestyle='--', alpha=0.7, label='Critical (95%)')
        axes[1, 0].set_title('Disk Usage (%)', fontweight='bold')
        axes[1, 0].set_ylabel('Percentage')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].legend()
        
        # Load Average
        axes[1, 1].plot(df['timestamp'], df['load_avg_1m'], 'orange', linewidth=2, label='Load Avg (1m)')
        axes[1, 1].set_title('System Load Average', fontweight='bold')
        axes[1, 1].set_ylabel('Load')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].legend()
        
        # Format x-axis
        for ax in axes.flat:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{save_dir}/system_resources_{timestamp}.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_application_metrics(self, df: pd.DataFrame, save_dir: str, timestamp: str):
        """Plot application performance metrics"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Application Performance Metrics', fontsize=16, fontweight='bold')
        
        # Response Time
        axes[0, 0].plot(df['timestamp'], df['response_time_ms'], 'red', linewidth=2, label='Response Time')
        axes[0, 0].axhline(y=500, color='orange', linestyle='--', alpha=0.7, label='Slow (500ms)')
        axes[0, 0].axhline(y=1000, color='red', linestyle='--', alpha=0.7, label='Very Slow (1s)')
        axes[0, 0].set_title('Response Time (ms)', fontweight='bold')
        axes[0, 0].set_ylabel('Milliseconds')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].legend()
        
        # Request Count
        axes[0, 1].plot(df['timestamp'], df['total_requests'], 'blue', linewidth=2, label='Total Requests')
        axes[0, 1].set_title('Total Requests Over Time', fontweight='bold')
        axes[0, 1].set_ylabel('Request Count')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].legend()
        
        # Error Count
        axes[1, 0].plot(df['timestamp'], df['error_count'], 'red', linewidth=2, label='Error Count')
        axes[1, 0].set_title('Error Count Over Time', fontweight='bold')
        axes[1, 0].set_ylabel('Errors')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].legend()
        
        # Error Rate
        axes[1, 1].plot(df['timestamp'], df['error_rate'], 'orange', linewidth=2, label='Error Rate %')
        axes[1, 1].axhline(y=5, color='orange', linestyle='--', alpha=0.7, label='Warning (5%)')
        axes[1, 1].axhline(y=10, color='red', linestyle='--', alpha=0.7, label='Critical (10%)')
        axes[1, 1].set_title('Error Rate (%)', fontweight='bold')
        axes[1, 1].set_ylabel('Percentage')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].legend()
        
        # Format x-axis
        for ax in axes.flat:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{save_dir}/application_metrics_{timestamp}.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_combined_overview(self, df: pd.DataFrame, save_dir: str, timestamp: str):
        """Plot combined overview dashboard"""
        fig, axes = plt.subplots(3, 1, figsize=(15, 12))
        fig.suptitle('Chaos Monkey Demo - Complete Overview', fontsize=16, fontweight='bold')
        
        # System Resources Combined
        ax1 = axes[0]
        ax1_twin = ax1.twinx()
        
        line1 = ax1.plot(df['timestamp'], df['cpu_percent'], 'b-', linewidth=2, label='CPU %')
        line2 = ax1.plot(df['timestamp'], df['memory_percent'], 'g-', linewidth=2, label='Memory %')
        line3 = ax1_twin.plot(df['timestamp'], df['response_time_ms'], 'r-', linewidth=2, label='Response Time (ms)')
        
        ax1.set_title('System Resources vs Application Response Time', fontweight='bold')
        ax1.set_ylabel('Resource Usage (%)', color='black')
        ax1_twin.set_ylabel('Response Time (ms)', color='red')
        ax1.grid(True, alpha=0.3)
        
        # Combine legends
        lines = line1 + line2 + line3
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left')
        
        # Application Health
        ax2 = axes[1]
        ax2_twin = ax2.twinx()
        
        line4 = ax2.plot(df['timestamp'], df['total_requests'], 'b-', linewidth=2, label='Total Requests')
        line5 = ax2_twin.plot(df['timestamp'], df['error_rate'], 'r-', linewidth=2, label='Error Rate %')
        
        ax2.set_title('Request Volume vs Error Rate', fontweight='bold')
        ax2.set_ylabel('Total Requests', color='blue')
        ax2_twin.set_ylabel('Error Rate (%)', color='red')
        ax2.grid(True, alpha=0.3)
        
        lines2 = line4 + line5
        labels2 = [l.get_label() for l in lines2]
        ax2.legend(lines2, labels2, loc='upper left')
        
        # Status Timeline
        ax3 = axes[2]
        status_numeric = df['app_status'].map({'healthy': 1, 'degraded': 0.5, 'unreachable': 0, 'unknown': 0.25})
        ax3.fill_between(df['timestamp'], status_numeric, alpha=0.6, 
                        color=['green' if x == 1 else 'orange' if x == 0.5 else 'red' for x in status_numeric])
        ax3.set_title('Application Health Status Timeline', fontweight='bold')
        ax3.set_ylabel('Health Status')
        ax3.set_yticks([0, 0.25, 0.5, 1])
        ax3.set_yticklabels(['Unreachable', 'Unknown', 'Degraded', 'Healthy'])
        ax3.grid(True, alpha=0.3)
        
        # Format x-axis
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{save_dir}/overview_{timestamp}.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_chaos_timeline(self, df: pd.DataFrame, save_dir: str, timestamp: str):
        """Plot timeline showing chaos events and their impact"""
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # Create a timeline showing when issues occurred
        ax.plot(df['timestamp'], df['cpu_percent'], 'b-', alpha=0.7, label='CPU %')
        ax.plot(df['timestamp'], df['memory_percent'], 'g-', alpha=0.7, label='Memory %')
        
        # Highlight high resource usage periods (potential chaos events)
        high_cpu = df['cpu_percent'] > 70
        high_memory = df['memory_percent'] > 70
        
        ax.fill_between(df['timestamp'], 0, 100, where=high_cpu, 
                       alpha=0.3, color='red', label='High CPU Events')
        ax.fill_between(df['timestamp'], 0, 100, where=high_memory, 
                       alpha=0.3, color='orange', label='High Memory Events')
        
        # Mark application issues
        app_issues = (df['response_time_ms'] > 1000) | (df['error_rate'] > 5)
        issue_times = df[app_issues]['timestamp']
        if not issue_times.empty:
            ax.scatter(issue_times, [95] * len(issue_times), 
                      color='red', s=100, marker='x', label='App Issues', zorder=5)
        
        ax.set_title('Chaos Engineering Timeline - Resource Usage and Events', fontsize=14, fontweight='bold')
        ax.set_ylabel('Resource Usage (%)')
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{save_dir}/chaos_timeline_{timestamp}.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _check_alerts(self, metrics: Dict) -> List[str]:
        """Check for alert conditions based on current metrics"""
        alerts = []
        
        try:
            system = metrics.get('system', {})
            app = metrics.get('application', {})
            
            # CPU alerts
            cpu_percent = system.get('cpu', {}).get('percent', 0)
            if cpu_percent > 90:
                alerts.append(f"Critical CPU usage: {cpu_percent:.1f}%")
            elif cpu_percent > 80:
                alerts.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            # Memory alerts
            memory_percent = system.get('memory', {}).get('percent', 0)
            if memory_percent > 90:
                alerts.append(f"Critical memory usage: {memory_percent:.1f}%")
            elif memory_percent > 80:
                alerts.append(f"High memory usage: {memory_percent:.1f}%")
            
            # Disk alerts
            disk_percent = system.get('disk', {}).get('percent', 0)
            if disk_percent > 95:
                alerts.append(f"Critical disk usage: {disk_percent:.1f}%")
            elif disk_percent > 85:
                alerts.append(f"High disk usage: {disk_percent:.1f}%")
            
            # Load average alerts
            load_avg = system.get('cpu', {}).get('load_avg_1m', 0)
            cpu_count = system.get('cpu', {}).get('count', 1)
            if load_avg > cpu_count * 2:
                alerts.append(f"Very high system load: {load_avg:.2f} (cores: {cpu_count})")
            elif load_avg > cpu_count:
                alerts.append(f"High system load: {load_avg:.2f} (cores: {cpu_count})")
            
            # Application alerts
            if not app.get('connectivity', False):
                alerts.append("Application is unreachable")
            else:
                health = app.get('health', {})
                stats = app.get('stats', {})
                
                # Response time alerts
                response_time = health.get('response_time', 0) * 1000
                if response_time > 2000:
                    alerts.append(f"Very slow response time: {response_time:.0f}ms")
                elif response_time > 1000:
                    alerts.append(f"Slow response time: {response_time:.0f}ms")
                
                # Error rate alerts
                error_rate = stats.get('error_rate', 0) * 100
                if error_rate > 10:
                    alerts.append(f"Critical error rate: {error_rate:.1f}%")
                elif error_rate > 5:
                    alerts.append(f"High error rate: {error_rate:.1f}%")
                
                # Status alerts
                status = health.get('status', '').lower()
                if status == 'unhealthy':
                    alerts.append("Application status is unhealthy")
                elif status == 'degraded':
                    alerts.append("Application status is degraded")
        
        except Exception as e:
            alerts.append(f"Error checking system health: {e}")
        
        return alerts

    def _generate_html_dashboard(self, save_dir: str, timestamp: str):
        """Generate an HTML dashboard with all the graphs"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Chaos Monkey Demo - Monitoring Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }}
        .chart-container {{ background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .chart-container img {{ width: 100%; height: auto; border-radius: 5px; }}
        .overview {{ grid-column: span 2; }}
        .stats {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: white; border-radius: 5px; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🐒 Chaos Monkey Demo - Monitoring Dashboard</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="stats">
        <h3>📊 Session Summary</h3>
        <div class="metric">
            <strong>Duration</strong><br>
            {len(self.metrics_history)} samples
        </div>
        <div class="metric">
            <strong>Monitoring Period</strong><br>
            {self.metrics_history[0]['timestamp'][:19] if self.metrics_history else 'N/A'} to<br>
            {self.metrics_history[-1]['timestamp'][:19] if self.metrics_history else 'N/A'}
        </div>
        <div class="metric">
            <strong>Data Points</strong><br>
            {len(self.metrics_history)} metrics collected
        </div>
    </div>
    
    <div class="container">
        <div class="chart-container overview">
            <h3>📈 Complete Overview</h3>
            <img src="overview_{timestamp}.png" alt="Complete Overview">
        </div>
        
        <div class="chart-container">
            <h3>💻 System Resources</h3>
            <img src="system_resources_{timestamp}.png" alt="System Resources">
        </div>
        
        <div class="chart-container">
            <h3>🌐 Application Metrics</h3>
            <img src="application_metrics_{timestamp}.png" alt="Application Metrics">
        </div>
        
        <div class="chart-container overview">
            <h3>⚡ Chaos Timeline</h3>
            <img src="chaos_timeline_{timestamp}.png" alt="Chaos Timeline">
        </div>
    </div>
    
    <div class="stats">
        <h3>🔍 Analysis Notes</h3>
        <ul>
            <li><strong>Resource Spikes:</strong> Look for correlation between CPU/Memory spikes and application response time</li>
            <li><strong>Error Patterns:</strong> Identify if errors increase during high resource usage periods</li>
            <li><strong>Recovery Time:</strong> Observe how quickly the system recovers from chaos events</li>
            <li><strong>Baseline Performance:</strong> Compare normal operation vs. chaos event periods</li>
        </ul>
    </div>
</body>
</html>"""
        
        with open(f"{save_dir}/dashboard_{timestamp}.html", 'w') as f:
            f.write(html_content)


def test_connectivity():
    """Test if the demo application is running"""
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            print("✅ Demo application is running and healthy")
            return True
        else:
            print(f"⚠️ Demo application responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to demo application at http://localhost:8080")
        print("   Make sure to start the demo app first: python demo_app.py")
        return False


if __name__ == "__main__":
    print("🔍 Chaos Monkey System Monitor")
    print("=" * 50)
    
    # Test connectivity first
    if not test_connectivity():
        print("\n⚠️ Starting monitor anyway - will track system resources")
        print("   Application monitoring will show 'unreachable' status")
    
    # Create system monitor
    monitor = SystemMonitor()
    
    print("\nSystem Monitor Configuration:")
    print("- Monitoring interval: 10 seconds")
    print("- Target application: http://localhost:8080")
    print("- Output directory: monitoring_output/")
    print("- Real-time terminal display: Enabled")
    print("- Graph generation: Enabled")
    print("\nPress Ctrl+C to stop monitoring and generate final report")
    print("=" * 50)
    
    try:
        monitor.start_monitoring(interval=10)
        
        # Keep the main thread alive
        while monitor.monitoring:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitor...")
        monitor.stop_monitoring()
        print("✅ Monitor stopped and final report generated!")
