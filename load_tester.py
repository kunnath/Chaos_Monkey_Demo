#!/usr/bin/env python3
"""
Load Testing Script for Chaos Monkey Demo
This script generates load on the demo application to simulate real traffic.
"""

import requests
import threading
import time
import random
import logging
from datetime import datetime
from typing import Dict, List
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os


class LoadTester:
    """Load testing class to generate traffic"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.running = False
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'errors': []
        }
        self.detailed_stats = []  # Store detailed metrics over time
        self.output_dir = "load_test_output"
        
        # Create output directory
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Define endpoints to test
        self.endpoints = [
            {'path': '/', 'weight': 30},
            {'path': '/health', 'weight': 20},
            {'path': '/api/data', 'weight': 25},
            {'path': '/api/slow', 'weight': 5},
            {'path': '/api/memory-intensive', 'weight': 8},
            {'path': '/api/cpu-intensive', 'weight': 7},
            {'path': '/api/database', 'weight': 15},
            {'path': '/stats', 'weight': 10}
        ]
    
    def _weighted_choice(self) -> str:
        """Choose an endpoint based on weights"""
        total_weight = sum(ep['weight'] for ep in self.endpoints)
        rand = random.randint(1, total_weight)
        
        current_weight = 0
        for endpoint in self.endpoints:
            current_weight += endpoint['weight']
            if rand <= current_weight:
                return endpoint['path']
        
        return self.endpoints[0]['path']  # fallback
    
    def _make_request(self, path: str) -> Dict:
        """Make a single HTTP request"""
        url = f"{self.base_url}{path}"
        start_time = time.time()
        
        try:
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time
            
            self.stats['total_requests'] += 1
            self.stats['response_times'].append(response_time)
            
            if response.status_code < 400:
                self.stats['successful_requests'] += 1
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'path': path
                }
            else:
                self.stats['failed_requests'] += 1
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'path': path,
                    'error': f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self.stats['total_requests'] += 1
            self.stats['failed_requests'] += 1
            self.stats['errors'].append(str(e))
            
            return {
                'success': False,
                'response_time': response_time,
                'path': path,
                'error': str(e)
            }
    
    def _worker_thread(self, requests_per_second: float, duration: int):
        """Worker thread that generates requests"""
        thread_id = threading.current_thread().name
        end_time = time.time() + duration
        
        while time.time() < end_time and self.running:
            path = self._weighted_choice()
            result = self._make_request(path)
            
            if not result['success']:
                self.logger.warning(f"[{thread_id}] Failed request to {path}: {result.get('error')}")
            
            # Sleep to maintain requests per second rate
            sleep_time = 1.0 / requests_per_second
            time.sleep(sleep_time)
    
    def start_load_test(self, 
                       requests_per_second: float = 2.0, 
                       duration: int = 300, 
                       num_threads: int = 3):
        """Start the load test"""
        self.running = True
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'errors': []
        }
        
        self.logger.info(f"🚀 Starting load test:")
        self.logger.info(f"   Requests per second: {requests_per_second}")
        self.logger.info(f"   Duration: {duration} seconds")
        self.logger.info(f"   Number of threads: {num_threads}")
        self.logger.info(f"   Target: {self.base_url}")
        
        # Adjust requests per second per thread
        rps_per_thread = requests_per_second / num_threads
        
        # Start worker threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(
                target=self._worker_thread,
                args=(rps_per_thread, duration),
                name=f"LoadWorker-{i+1}"
            )
            thread.start()
            threads.append(thread)
        
        # Monitor progress
        start_time = time.time()
        try:
            while any(t.is_alive() for t in threads):
                time.sleep(10)
                elapsed = time.time() - start_time
                self._print_stats(elapsed)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Load test interrupted by user")
            self.running = False
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        self.logger.info("✅ Load test completed")
        self._print_final_stats()
        self._plot_results()
    
    def _print_stats(self, elapsed: float):
        """Print current statistics with enhanced formatting"""
        if self.stats['response_times']:
            avg_response_time = sum(self.stats['response_times']) / len(self.stats['response_times'])
            max_response_time = max(self.stats['response_times'])
            min_response_time = min(self.stats['response_times'])
        else:
            avg_response_time = 0
            max_response_time = 0
            min_response_time = 0
        
        success_rate = (self.stats['successful_requests'] / max(self.stats['total_requests'], 1)) * 100
        
        # Clear screen and print enhanced stats
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🧪" + "=" * 79)
        print(f"🚀 LOAD TESTING IN PROGRESS - {datetime.now().strftime('%H:%M:%S')}")
        print("🧪" + "=" * 79)
        
        print(f"⏱️  TIMING:")
        print(f"   Elapsed Time:     {elapsed:.1f}s")
        print(f"   Target URL:       {self.base_url}")
        
        print(f"\n📊 REQUEST STATISTICS:")
        print(f"   Total Requests:   {self.stats['total_requests']:,}")
        print(f"   Successful:       {self.stats['successful_requests']:,}")
        print(f"   Failed:           {self.stats['failed_requests']:,}")
        
        # Success rate with visual indicator
        success_bar = self._create_progress_bar(success_rate, 100)
        print(f"   Success Rate:     {success_bar} {success_rate:.1f}%")
        
        print(f"\n⚡ RESPONSE TIMES:")
        print(f"   Average:          {avg_response_time*1000:.0f}ms")
        print(f"   Minimum:          {min_response_time*1000:.0f}ms")
        print(f"   Maximum:          {max_response_time*1000:.0f}ms")
        
        # Performance indicator
        if avg_response_time < 0.1:
            perf_status = "🟢 Excellent"
        elif avg_response_time < 0.5:
            perf_status = "🟡 Good"
        elif avg_response_time < 1.0:
            perf_status = "🟠 Slow"
        else:
            perf_status = "🔴 Poor"
        
        print(f"   Performance:      {perf_status}")
        
        # Request rate
        if elapsed > 0:
            request_rate = self.stats['total_requests'] / elapsed
            print(f"\n📈 THROUGHPUT:")
            print(f"   Requests/sec:     {request_rate:.1f}")
        
        # Store current stats for graphing
        self.detailed_stats.append({
            'timestamp': datetime.now(),
            'elapsed': elapsed,
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'request_rate': request_rate if elapsed > 0 else 0
        })
        
        print("🧪" + "=" * 79)
        print("📊 Press Ctrl+C to stop and generate final report")
        print("🧪" + "=" * 79)
    
    def _create_progress_bar(self, value: float, max_value: float, width: int = 20) -> str:
        """Create a visual progress bar"""
        if max_value == 0:
            return '▱' * width
        
        filled = int((value / max_value) * width)
        filled = min(filled, width)
        
        # Color coding
        if value / max_value > 0.9:
            color = '\033[92m'  # Green
        elif value / max_value > 0.7:
            color = '\033[93m'  # Yellow
        else:
            color = '\033[91m'  # Red
        
        reset_color = '\033[0m'
        bar = '█' * filled + '▱' * (width - filled)
        return f"{color}{bar}{reset_color}"

    def _print_final_stats(self):
        """Print final statistics and generate graphs"""
        print("\n" + "🧪" + "="*78 + "🧪")
        print("📈 FINAL LOAD TEST RESULTS")
        print("🧪" + "="*78 + "🧪")
        
        if self.stats['response_times']:
            avg_response_time = sum(self.stats['response_times']) / len(self.stats['response_times'])
            max_response_time = max(self.stats['response_times'])
            min_response_time = min(self.stats['response_times'])
            
            # Calculate percentiles
            sorted_times = sorted(self.stats['response_times'])
            p50_index = int(len(sorted_times) * 0.50)
            p90_index = int(len(sorted_times) * 0.90)
            p95_index = int(len(sorted_times) * 0.95)
            p99_index = int(len(sorted_times) * 0.99)
            
            p50_time = sorted_times[p50_index] if p50_index < len(sorted_times) else avg_response_time
            p90_time = sorted_times[p90_index] if p90_index < len(sorted_times) else max_response_time
            p95_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time
            p99_time = sorted_times[p99_index] if p99_index < len(sorted_times) else max_response_time
        else:
            avg_response_time = 0
            max_response_time = 0
            min_response_time = 0
            p50_time = p90_time = p95_time = p99_time = 0
        
        success_rate = (self.stats['successful_requests'] / max(self.stats['total_requests'], 1)) * 100
        
        # Summary statistics
        print(f"📊 SUMMARY STATISTICS:")
        print(f"   Total Requests:        {self.stats['total_requests']:,}")
        print(f"   Successful Requests:   {self.stats['successful_requests']:,}")
        print(f"   Failed Requests:       {self.stats['failed_requests']:,}")
        print(f"   Success Rate:          {success_rate:.2f}%")
        
        print(f"\n⚡ RESPONSE TIME ANALYSIS:")
        print(f"   Average:               {avg_response_time*1000:.0f}ms")
        print(f"   Minimum:               {min_response_time*1000:.0f}ms")
        print(f"   Maximum:               {max_response_time*1000:.0f}ms")
        print(f"   50th Percentile (P50): {p50_time*1000:.0f}ms")
        print(f"   90th Percentile (P90): {p90_time*1000:.0f}ms")
        print(f"   95th Percentile (P95): {p95_time*1000:.0f}ms")
        print(f"   99th Percentile (P99): {p99_time*1000:.0f}ms")
        
        # Error analysis
        if self.stats['errors']:
            print(f"\n🚨 ERROR ANALYSIS:")
            error_counts = {}
            for error in self.stats['errors']:
                error_counts[error] = error_counts.get(error, 0) + 1
            
            print(f"   Total Unique Errors:   {len(error_counts)}")
            print(f"   Top Errors:")
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"      • {error}: {count} times")
        
        # Performance assessment
        print(f"\n🎯 PERFORMANCE ASSESSMENT:")
        if success_rate >= 99:
            reliability = "🟢 Excellent"
        elif success_rate >= 95:
            reliability = "🟡 Good"
        elif success_rate >= 90:
            reliability = "🟠 Fair"
        else:
            reliability = "🔴 Poor"
        
        if avg_response_time < 0.1:
            speed = "🟢 Very Fast"
        elif avg_response_time < 0.5:
            speed = "🟡 Fast"
        elif avg_response_time < 1.0:
            speed = "🟠 Moderate"
        else:
            speed = "🔴 Slow"
        
        print(f"   Reliability:           {reliability} ({success_rate:.1f}%)")
        print(f"   Speed:                 {speed} ({avg_response_time*1000:.0f}ms avg)")
        
        # Generate graphs
        print(f"\n📊 Generating performance graphs...")
        self._generate_load_test_graphs()
        
        print("🧪" + "="*78 + "🧪")
    
    def _generate_load_test_graphs(self):
        """Generate load testing performance graphs"""
        if not self.detailed_stats:
            print("⚠️ No detailed statistics available for graphing")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(self.detailed_stats)
            
            # Create comprehensive load test dashboard
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Load Test Performance Analysis', fontsize=16, fontweight='bold')
            
            # Request rate over time
            axes[0, 0].plot(df['elapsed'], df['request_rate'], 'b-', linewidth=2)
            axes[0, 0].set_title('Requests Per Second Over Time', fontweight='bold')
            axes[0, 0].set_xlabel('Time (seconds)')
            axes[0, 0].set_ylabel('Requests/sec')
            axes[0, 0].grid(True, alpha=0.3)
            
            # Response time over time
            axes[0, 1].plot(df['elapsed'], df['avg_response_time'] * 1000, 'r-', linewidth=2)
            axes[0, 1].axhline(y=500, color='orange', linestyle='--', alpha=0.7, label='500ms threshold')
            axes[0, 1].axhline(y=1000, color='red', linestyle='--', alpha=0.7, label='1s threshold')
            axes[0, 1].set_title('Average Response Time Over Time', fontweight='bold')
            axes[0, 1].set_xlabel('Time (seconds)')
            axes[0, 1].set_ylabel('Response Time (ms)')
            axes[0, 1].grid(True, alpha=0.3)
            axes[0, 1].legend()
            
            # Success rate over time
            axes[1, 0].plot(df['elapsed'], df['success_rate'], 'g-', linewidth=2)
            axes[1, 0].axhline(y=95, color='orange', linestyle='--', alpha=0.7, label='95% threshold')
            axes[1, 0].axhline(y=99, color='green', linestyle='--', alpha=0.7, label='99% threshold')
            axes[1, 0].set_title('Success Rate Over Time', fontweight='bold')
            axes[1, 0].set_xlabel('Time (seconds)')
            axes[1, 0].set_ylabel('Success Rate (%)')
            axes[1, 0].set_ylim(0, 100)
            axes[1, 0].grid(True, alpha=0.3)
            axes[1, 0].legend()
            
            # Cumulative requests
            axes[1, 1].plot(df['elapsed'], df['total_requests'], 'purple', linewidth=2, label='Total')
            axes[1, 1].plot(df['elapsed'], df['successful_requests'], 'green', linewidth=2, label='Successful')
            axes[1, 1].plot(df['elapsed'], df['failed_requests'], 'red', linewidth=2, label='Failed')
            axes[1, 1].set_title('Cumulative Request Count', fontweight='bold')
            axes[1, 1].set_xlabel('Time (seconds)')
            axes[1, 1].set_ylabel('Request Count')
            axes[1, 1].grid(True, alpha=0.3)
            axes[1, 1].legend()
            
            plt.tight_layout()
            
            # Save the graph
            filename = f"{self.output_dir}/load_test_analysis_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Generate response time histogram
            if self.stats['response_times']:
                plt.figure(figsize=(10, 6))
                response_times_ms = [rt * 1000 for rt in self.stats['response_times']]
                plt.hist(response_times_ms, bins=50, alpha=0.7, color='blue', edgecolor='black')
                plt.title('Response Time Distribution', fontsize=14, fontweight='bold')
                plt.xlabel('Response Time (ms)')
                plt.ylabel('Frequency')
                plt.grid(True, alpha=0.3)
                
                # Add statistics to the plot
                avg_ms = np.mean(response_times_ms)
                p95_ms = np.percentile(response_times_ms, 95)
                plt.axvline(avg_ms, color='red', linestyle='--', linewidth=2, label=f'Average: {avg_ms:.0f}ms')
                plt.axvline(p95_ms, color='orange', linestyle='--', linewidth=2, label=f'95th Percentile: {p95_ms:.0f}ms')
                plt.legend()
                
                histogram_filename = f"{self.output_dir}/response_time_histogram_{timestamp}.png"
                plt.savefig(histogram_filename, dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"✅ Load test graphs generated:")
                print(f"   📈 Performance Analysis: {filename}")
                print(f"   📊 Response Time Distribution: {histogram_filename}")
            
        except Exception as e:
            print(f"❌ Error generating graphs: {e}")

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
    print("🧪 Chaos Monkey Load Tester")
    print("=" * 50)
    
    # Test connectivity first
    if not test_connectivity():
        exit(1)
    
    # Create load tester
    tester = LoadTester()
    
    # Configure test parameters
    print("\nLoad Test Configuration:")
    print("- Requests per second: 3.0")
    print("- Duration: 180 seconds (3 minutes)")
    print("- Number of threads: 4")
    print("- Target endpoints: 8 different endpoints")
    print("\nPress Ctrl+C to stop the test early")
    print("=" * 50)
    
    # Start the load test
    tester.start_load_test(
        requests_per_second=3.0,
        duration=180,  # 3 minutes
        num_threads=4
    )
