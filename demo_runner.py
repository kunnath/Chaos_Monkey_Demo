#!/usr/bin/env python3
"""
Chaos Monkey Demo Runner
This script orchestrates the complete chaos engineering demonstration.
"""

import subprocess
import time
import threading
import signal
import sys
import os
from datetime import datetime


class ChaosDemo:
    """Orchestrates the complete chaos engineering demo"""
    
    def __init__(self):
        self.processes = []
        self.running = False
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n🛑 Stopping Chaos Monkey Demo...")
        self.stop_all()
        sys.exit(0)
    
    def start_component(self, script_name: str, description: str, wait_time: int = 2):
        """Start a demo component"""
        print(f"🚀 Starting {description}...")
        
        try:
            # Get the Python executable path
            python_cmd = "/Users/kunnath/Projects/Chaos Monkey/.venv/bin/python"
            
            process = subprocess.Popen(
                [python_cmd, script_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd="/Users/kunnath/Projects/Chaos Monkey"
            )
            
            self.processes.append({
                'process': process,
                'name': description,
                'script': script_name
            })
            
            time.sleep(wait_time)
            
            # Check if process started successfully
            if process.poll() is None:
                print(f"✅ {description} started successfully (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Failed to start {description}")
                print(f"   Error: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting {description}: {e}")
            return False
    
    def stop_all(self):
        """Stop all running components and generate final report"""
        self.running = False
        
        print("\n🛑 STOPPING ALL COMPONENTS")
        print("=" * 60)
        
        for component in self.processes:
            try:
                process = component['process']
                name = component['name']
                
                if process.poll() is None:  # Process is still running
                    print(f"🛑 Stopping {name}...")
                    process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=10)  # Give more time for graceful shutdown
                    except subprocess.TimeoutExpired:
                        print(f"⚡ Force killing {name}...")
                        process.kill()
                        process.wait()
                    
                    print(f"✅ {name} stopped")
                    
            except Exception as e:
                print(f"❌ Error stopping {component['name']}: {e}")
        
        self.processes.clear()
        
        # Generate final comprehensive report
        print("\n📊 GENERATING FINAL REPORT")
        print("=" * 60)
        self._generate_final_report()
    
    def _generate_final_report(self):
        """Generate comprehensive final report with all graphs and summaries"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        print("📈 Collecting and analyzing results...")
        
        # Check for generated files
        monitoring_dir = "monitoring_output"
        load_test_dir = "load_test_output"
        
        monitoring_files = []
        load_test_files = []
        
        if os.path.exists(monitoring_dir):
            monitoring_files = [f for f in os.listdir(monitoring_dir) if f.endswith('.png') or f.endswith('.html')]
        
        if os.path.exists(load_test_dir):
            load_test_files = [f for f in os.listdir(load_test_dir) if f.endswith('.png')]
        
        # Generate comprehensive HTML report
        self._create_comprehensive_report(monitoring_files, load_test_files, timestamp)
        
        print("\n✅ DEMO COMPLETE - FINAL RESULTS")
        print("=" * 60)
        print(f"📊 Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if monitoring_files or load_test_files:
            print(f"\n📈 GENERATED VISUALIZATIONS:")
            
            if monitoring_files:
                print(f"   🔍 System Monitoring:")
                for file in sorted(monitoring_files):
                    if file.endswith('.png'):
                        print(f"      • {monitoring_dir}/{file}")
                    elif file.endswith('.html'):
                        print(f"      🌐 {monitoring_dir}/{file}")
            
            if load_test_files:
                print(f"   🧪 Load Testing:")
                for file in sorted(load_test_files):
                    print(f"      • {load_test_dir}/{file}")
            
            print(f"\n🌐 COMPREHENSIVE REPORT:")
            print(f"   📋 chaos_monkey_demo_report_{timestamp}.html")
            
        else:
            print("⚠️ No visualization files found. Demo may have been stopped too early.")
        
        print(f"\n🎯 CHAOS ENGINEERING INSIGHTS:")
        print(f"   • Review the graphs to identify performance impacts")
        print(f"   • Look for correlation between chaos events and system metrics")
        print(f"   • Analyze application resilience and recovery patterns")
        print(f"   • Use insights to improve system robustness")
        
        print("\n" + "=" * 60)
        print("🐒 Thank you for using Chaos Monkey Demo!")
        print("=" * 60)
    
    def _create_comprehensive_report(self, monitoring_files, load_test_files, timestamp):
        """Create a comprehensive HTML report combining all results"""
        
        monitoring_dir = "monitoring_output"
        load_test_dir = "load_test_output"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Chaos Monkey Demo - Comprehensive Report</title>
    <meta charset="UTF-8">
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{ 
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white; 
            padding: 40px 30px; 
            text-align: center; 
        }}
        .header h1 {{ margin: 0; font-size: 2.5em; font-weight: 300; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 1.1em; }}
        .section {{ 
            padding: 30px; 
            border-bottom: 1px solid #eee; 
        }}
        .section:last-child {{ border-bottom: none; }}
        .section h2 {{ 
            color: #2c3e50; 
            border-bottom: 3px solid #3498db; 
            padding-bottom: 10px; 
            margin-bottom: 25px;
            font-weight: 300;
        }}
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
            gap: 25px; 
            margin-top: 25px; 
        }}
        .card {{ 
            background: #f8f9fa; 
            padding: 25px; 
            border-radius: 10px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.08); 
            transition: transform 0.3s ease;
        }}
        .card:hover {{ transform: translateY(-5px); }}
        .card h3 {{ 
            margin: 0 0 15px 0; 
            color: #34495e; 
            font-weight: 500;
        }}
        .card img {{ 
            width: 100%; 
            height: auto; 
            border-radius: 8px; 
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }}
        .metric {{ 
            display: inline-block; 
            margin: 10px 15px; 
            padding: 20px; 
            background: white; 
            border-radius: 10px; 
            text-align: center; 
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            min-width: 120px;
        }}
        .metric strong {{ 
            display: block; 
            font-size: 1.8em; 
            color: #2c3e50; 
            margin-bottom: 5px;
        }}
        .metric span {{ 
            color: #7f8c8d; 
            font-size: 0.9em;
        }}
        .insights {{ 
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white; 
            padding: 30px; 
            border-radius: 10px; 
            margin: 25px 0;
        }}
        .insights h3 {{ 
            margin: 0 0 15px 0; 
            font-weight: 300;
        }}
        .insights ul {{ 
            margin: 0; 
            padding-left: 20px;
        }}
        .insights li {{ 
            margin: 8px 0; 
            line-height: 1.6;
        }}
        .file-list {{ 
            background: #f1f2f6; 
            padding: 20px; 
            border-radius: 8px; 
            margin: 15px 0;
        }}
        .file-list ul {{ 
            margin: 0; 
            padding-left: 20px;
        }}
        .file-list li {{ 
            margin: 5px 0; 
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        .badge {{ 
            background: #3498db; 
            color: white; 
            padding: 4px 12px; 
            border-radius: 15px; 
            font-size: 0.8em; 
            margin-left: 10px;
        }}
        .footer {{ 
            background: #2c3e50; 
            color: white; 
            text-align: center; 
            padding: 25px;
        }}
        .emoji {{ font-size: 1.2em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="emoji">🐒</span> Chaos Monkey Demo</h1>
            <p>Comprehensive Chaos Engineering Analysis Report</p>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2><span class="emoji">📊</span> Demo Summary</h2>
            <div class="metric">
                <strong>{len(monitoring_files) + len(load_test_files)}</strong>
                <span>Visualizations Generated</span>
            </div>
            <div class="metric">
                <strong>{len(monitoring_files)}</strong>
                <span>Monitoring Charts</span>
            </div>
            <div class="metric">
                <strong>{len(load_test_files)}</strong>
                <span>Performance Charts</span>
            </div>
            <div class="metric">
                <strong>4</strong>
                <span>Components Tested</span>
            </div>
        </div>
        
        <div class="section">
            <h2><span class="emoji">🔍</span> System Monitoring Results</h2>
            <p>Real-time monitoring of system resources and application health during chaos experiments.</p>
            
            <div class="grid">"""
        
        # Add monitoring visualizations
        for file in sorted(monitoring_files):
            if file.endswith('.png'):
                title = file.replace('_', ' ').replace('.png', '').title()
                html_content += f"""
                <div class="card">
                    <h3>{title}</h3>
                    <img src="{monitoring_dir}/{file}" alt="{title}">
                </div>"""
        
        html_content += """
            </div>
        </div>
        
        <div class="section">
            <h2><span class="emoji">🧪</span> Load Testing Results</h2>
            <p>Performance analysis under continuous load during chaos engineering experiments.</p>
            
            <div class="grid">"""
        
        # Add load testing visualizations
        for file in sorted(load_test_files):
            title = file.replace('_', ' ').replace('.png', '').title()
            html_content += f"""
            <div class="card">
                <h3>{title}</h3>
                <img src="{load_test_dir}/{file}" alt="{title}">
            </div>"""
        
        # Create monitoring and load test file lists
        monitoring_files_html = ""
        if monitoring_files:
            monitoring_files_html = f'''<div class="file-list">
                <h4>System Monitoring Output:</h4>
                <ul>
                    {chr(10).join([f"<li>{monitoring_dir}/{file}</li>" for file in sorted(monitoring_files)])}
                </ul>
            </div>'''
        
        load_test_files_html = ""
        if load_test_files:
            load_test_files_html = f'''<div class="file-list">
                <h4>Load Testing Output:</h4>
                <ul>
                    {chr(10).join([f"<li>{load_test_dir}/{file}</li>" for file in sorted(load_test_files)])}
                </ul>
            </div>'''
        
        html_content += f"""
            </div>
        </div>
        
        <div class="section">
            <h2><span class="emoji">🎯</span> Chaos Engineering Insights</h2>
            
            <div class="insights">
                <h3><span class="emoji">🔍</span> Key Analysis Areas</h3>
                <ul>
                    <li><strong>Resource Correlation:</strong> Examine how CPU and memory spikes correlate with application response times</li>
                    <li><strong>Error Patterns:</strong> Identify error rate increases during high resource usage periods</li>
                    <li><strong>Recovery Behavior:</strong> Analyze how quickly the system recovers from chaos events</li>
                    <li><strong>Performance Baseline:</strong> Compare normal operation metrics with chaos event periods</li>
                    <li><strong>Resilience Patterns:</strong> Look for system behaviors that indicate good or poor resilience</li>
                </ul>
            </div>
            
            <div class="insights">
                <h3><span class="emoji">💡</span> Recommended Actions</h3>
                <ul>
                    <li>Review response time spikes and implement caching or optimization strategies</li>
                    <li>Set up automated alerts based on the thresholds observed during testing</li>
                    <li>Implement circuit breakers for services that showed poor resilience</li>
                    <li>Consider auto-scaling policies based on resource usage patterns</li>
                    <li>Establish monitoring baselines from the healthy operation periods</li>
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2><span class="emoji">📁</span> Generated Files</h2>
            
            {monitoring_files_html}
            {load_test_files_html}
            
            <div class="file-list">
                <h4>Demo Components:</h4>
                <ul>
                    <li>chaos_monkey.py <span class="badge">Chaos Engine</span></li>
                    <li>demo_app.py <span class="badge">Target Application</span></li>
                    <li>system_monitor.py <span class="badge">Resource Monitor</span></li>
                    <li>load_tester.py <span class="badge">Performance Tester</span></li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p><span class="emoji">🐒</span> Chaos Monkey Demo - Building Resilient Systems Through Controlled Failure</p>
            <p>Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""
        
        # Save the comprehensive report
        report_filename = f"chaos_monkey_demo_report_{timestamp}.html"
        with open(report_filename, 'w') as f:
            f.write(html_content)
        
        print(f"📋 Comprehensive report generated: {report_filename}")
    
    def check_status(self):
        """Check status of all components"""
        print("\n📊 Component Status:")
        print("-" * 40)
        
        for component in self.processes:
            process = component['process']
            name = component['name']
            
            if process.poll() is None:
                print(f"✅ {name}: Running (PID: {process.pid})")
            else:
                print(f"❌ {name}: Stopped")
    
    def run_full_demo(self):
        """Run the complete chaos engineering demo"""
        print("🐒 CHAOS MONKEY DEMONSTRATION")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Setup signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        self.running = True
        
        # Phase 1: Start the demo application
        print("\n📱 PHASE 1: Starting Demo Application")
        print("-" * 40)
        if not self.start_component("demo_app.py", "Demo Web Application", wait_time=3):
            print("❌ Cannot continue without the demo application")
            return
        
        # Wait for app to be fully ready
        print("⏳ Waiting for application to be ready...")
        time.sleep(5)
        
        # Phase 2: Start system monitoring
        print("\n🔍 PHASE 2: Starting System Monitor")
        print("-" * 40)
        self.start_component("system_monitor.py", "System Monitor", wait_time=2)
        
        # Phase 3: Start load testing
        print("\n🧪 PHASE 3: Starting Load Testing")
        print("-" * 40)
        self.start_component("load_tester.py", "Load Tester", wait_time=3)
        
        # Phase 4: Start chaos monkey
        print("\n🐒 PHASE 4: Starting Chaos Monkey")
        print("-" * 40)
        print("⚠️  The Chaos Monkey will start introducing failures...")
        print("    Monitor the system behavior and application resilience.")
        time.sleep(2)
        self.start_component("chaos_monkey.py", "Chaos Monkey", wait_time=2)
        
        # Demo monitoring loop
        print("\n🎯 DEMO RUNNING")
        print("=" * 60)
        print("The chaos engineering demo is now running with:")
        print("• Demo web application (http://localhost:8080)")
        print("• System resource monitoring")
        print("• Continuous load testing")
        print("• Chaos Monkey introducing failures")
        print("\nPress Ctrl+C to stop the demo")
        print("=" * 60)
        
        try:
            # Monitor demo status
            status_interval = 30  # Check every 30 seconds
            last_status_check = time.time()
            
            while self.running:
                current_time = time.time()
                
                # Periodic status check
                if current_time - last_status_check >= status_interval:
                    self.check_status()
                    last_status_check = current_time
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            pass  # Handled by signal handler
    
    def run_interactive_demo(self):
        """Run an interactive demo where user can control components"""
        print("🐒 CHAOS MONKEY INTERACTIVE DEMO")
        print("=" * 50)
        
        # Setup signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        
        while True:
            print("\n🎮 Interactive Demo Menu:")
            print("1. Start Demo Application")
            print("2. Start System Monitor")
            print("3. Start Load Tester")
            print("4. Start Chaos Monkey")
            print("5. Check Component Status")
            print("6. Stop All Components")
            print("7. Run Full Auto Demo")
            print("8. Launch Streamlit Dashboard")
            print("0. Exit")
            
            choice = input("\nSelect option (0-8): ").strip()
            
            if choice == "1":
                self.start_component("demo_app.py", "Demo Web Application")
            elif choice == "2":
                self.start_component("system_monitor.py", "System Monitor")
            elif choice == "3":
                self.start_component("load_tester.py", "Load Tester")
            elif choice == "4":
                self.start_component("chaos_monkey.py", "Chaos Monkey")
            elif choice == "5":
                self.check_status()
            elif choice == "6":
                self.stop_all()
            elif choice == "7":
                self.run_full_demo()
                break
            elif choice == "8":
                self.run_streamlit_dashboard()
            elif choice == "0":
                self.stop_all()
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    def run_streamlit_dashboard(self):
        """Launch the Streamlit interactive dashboard"""
        print("🌐 LAUNCHING STREAMLIT DASHBOARD")
        print("=" * 60)
        print("🚀 Starting interactive web dashboard...")
        print("📊 Dashboard URL: http://localhost:8501")
        print("🎮 Use the web interface to control the demo")
        print("🛑 Press Ctrl+C to stop the dashboard")
        print("=" * 60)
        
        try:
            # Start the Streamlit dashboard
            python_cmd = "/Users/kunnath/Projects/Chaos Monkey/.venv/bin/python"
            
            dashboard_process = subprocess.run([
                python_cmd, "-m", "streamlit", "run", "streamlit_demo.py",
                "--server.port", "8501",
                "--browser.gatherUsageStats", "false"
            ], cwd="/Users/kunnath/Projects/Chaos Monkey")
            
        except KeyboardInterrupt:
            print("\n🛑 Dashboard stopped by user")
        except Exception as e:
            print(f"❌ Error launching dashboard: {e}")
            print("💡 Make sure Streamlit is installed: pip install streamlit plotly pandas")


def show_demo_info():
    """Show information about the demo"""
    print("🐒 CHAOS MONKEY DEMO INFORMATION")
    print("=" * 50)
    print("""
This demonstration includes:

🌐 Demo Web Application (demo_app.py)
   • Flask web server with multiple endpoints
   • Simulates real application behavior
   • Includes health checks and metrics
   • Runs on http://localhost:8080

🔍 System Monitor (system_monitor.py)
   • Monitors CPU, memory, disk, network usage
   • Tracks application health and performance
   • Shows real-time alerts and status
   • Saves metrics to JSON file

🧪 Load Tester (load_tester.py)
   • Generates realistic traffic patterns
   • Tests multiple application endpoints
   • Provides performance statistics
   • Simulates user behavior

🐒 Chaos Monkey (chaos_monkey.py)
   • Introduces various failure scenarios
   • CPU stress, memory pressure, network issues
   • Service disruptions and resource constraints
   • Configurable experiment probabilities

The demo shows how applications behave under stress and helps
identify weaknesses in system resilience.
""")


if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("chaos_monkey.py"):
        print("❌ Error: Please run this script from the Chaos Monkey project directory")
        print("   Expected files: chaos_monkey.py, demo_app.py, load_tester.py, system_monitor.py")
        sys.exit(1)
    
    demo = ChaosDemo()
    
    # Show demo options
    print("🐒 CHAOS MONKEY DEMONSTRATION")
    print("=" * 50)
    print("Choose demo mode:")
    print("1. Full Automatic Demo (recommended)")
    print("2. Interactive Demo (manual control)")
    print("3. Show Demo Information")
    print("0. Exit")
    
    choice = input("\nSelect option (0-3): ").strip()
    
    if choice == "1":
        demo.run_full_demo()
    elif choice == "2":
        demo.run_interactive_demo()
    elif choice == "3":
        show_demo_info()
    elif choice == "0":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid option")
        
    # Cleanup
    demo.stop_all()
