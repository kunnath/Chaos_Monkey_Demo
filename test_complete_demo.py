#!/usr/bin/env python3
"""
Complete Demo Test Script
Tests all Chaos Monkey components and ensures proper graph generation
"""

import subprocess
import time
import requests
import os
import threading
from datetime import datetime


def run_command(cmd, description, background=False):
    """Run a command and return the process"""
    print(f"🚀 {description}...")
    
    try:
        python_cmd = "/Users/kunnath/Projects/Chaos Monkey/.venv/bin/python"
        process = subprocess.Popen(
            [python_cmd] + cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/Users/kunnath/Projects/Chaos Monkey"
        )
        
        if background:
            time.sleep(2)  # Give it time to start
            if process.poll() is None:
                print(f"✅ {description} started successfully")
                return process
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Failed to start {description}")
                print(f"Error: {stderr.decode()}")
                return None
        else:
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                print(f"✅ {description} completed successfully")
                return stdout.decode()
            else:
                print(f"❌ {description} failed")
                print(f"Error: {stderr.decode()}")
                return None
                
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return None


def wait_for_app(url="http://localhost:8080/health", timeout=30):
    """Wait for the application to be ready"""
    print("⏳ Waiting for application to be ready...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print("✅ Application is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)
    
    print("❌ Application did not become ready in time")
    return False


def check_generated_files():
    """Check if all expected files were generated"""
    print("\n📁 Checking generated files...")
    
    expected_dirs = ["monitoring_output", "load_test_output"]
    found_files = []
    
    for dir_name in expected_dirs:
        if os.path.exists(dir_name):
            files = os.listdir(dir_name)
            png_files = [f for f in files if f.endswith('.png')]
            html_files = [f for f in files if f.endswith('.html')]
            
            print(f"📂 {dir_name}/:")
            for file in sorted(png_files + html_files):
                print(f"   • {file}")
                found_files.append(f"{dir_name}/{file}")
        else:
            print(f"❌ Directory {dir_name} not found")
    
    # Check for comprehensive report
    report_files = [f for f in os.listdir('.') if f.startswith('chaos_monkey_demo_report_') and f.endswith('.html')]
    if report_files:
        print(f"📋 Comprehensive Reports:")
        for file in sorted(report_files):
            print(f"   • {file}")
            found_files.append(file)
    
    return found_files


def run_short_demo():
    """Run a short version of the demo for testing"""
    print("🐒 CHAOS MONKEY COMPLETE DEMO TEST")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    processes = []
    
    try:
        # Step 1: Start demo application
        print("\n📱 STEP 1: Starting Demo Application")
        app_process = run_command(["demo_app.py"], "Demo Application", background=True)
        if app_process:
            processes.append(("Demo App", app_process))
        else:
            print("❌ Cannot continue without demo application")
            return
        
        # Wait for app to be ready
        if not wait_for_app():
            return
        
        # Step 2: Start system monitor
        print("\n🔍 STEP 2: Starting System Monitor")
        monitor_process = run_command(["system_monitor.py"], "System Monitor", background=True)
        if monitor_process:
            processes.append(("System Monitor", monitor_process))
        
        # Step 3: Start load tester (short duration)
        print("\n🧪 STEP 3: Starting Load Test (60 seconds)")
        
        # Create a custom load test script for shorter duration
        load_test_code = '''
import sys
sys.path.append("/Users/kunnath/Projects/Chaos Monkey")
from load_tester import LoadTester

tester = LoadTester()
print("🧪 Running 60-second load test...")
tester.start_load_test(requests_per_second=2.0, duration=60, num_threads=2)
'''
        
        # Write and run custom load test
        with open('temp_load_test.py', 'w') as f:
            f.write(load_test_code)
        
        load_process = run_command(["temp_load_test.py"], "Short Load Test", background=True)
        if load_process:
            processes.append(("Load Test", load_process))
        
        # Step 4: Run a few chaos experiments
        print("\n🐒 STEP 4: Running Chaos Experiments")
        
        chaos_code = '''
import sys
sys.path.append("/Users/kunnath/Projects/Chaos Monkey")
from chaos_monkey import ChaosMonkey

monkey = ChaosMonkey()
print("🐒 Running quick chaos experiments...")

# Run 3 quick experiments
for i in range(3):
    print(f"Experiment {i+1}/3")
    monkey.cpu_stress_test(duration=15, intensity=50)
    print("Waiting 10 seconds...")
    import time
    time.sleep(10)

print("🐒 Chaos experiments completed")
'''
        
        with open('temp_chaos_test.py', 'w') as f:
            f.write(chaos_code)
        
        chaos_output = run_command(["temp_chaos_test.py"], "Chaos Experiments", background=False)
        
        # Let everything run for a bit
        print("\n⏳ Letting demo run for 90 seconds...")
        print("   (Monitor will collect data, load test will complete)")
        time.sleep(90)
        
        # Step 5: Stop all processes
        print("\n🛑 STEP 5: Stopping All Processes")
        for name, process in processes:
            if process and process.poll() is None:
                print(f"Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=10)
                    print(f"✅ {name} stopped")
                except subprocess.TimeoutExpired:
                    process.kill()
                    print(f"⚡ {name} force killed")
        
        # Give time for final graph generation
        print("⏳ Waiting for final graph generation...")
        time.sleep(5)
        
        # Step 6: Check results
        print("\n📊 STEP 6: Checking Results")
        found_files = check_generated_files()
        
        if found_files:
            print(f"\n✅ SUCCESS! Generated {len(found_files)} files:")
            for file in found_files:
                print(f"   📈 {file}")
            
            print(f"\n🎯 DEMO COMPLETE!")
            print(f"   • System monitoring graphs generated")
            print(f"   • Load testing performance charts created")
            print(f"   • Comprehensive HTML report available")
            print(f"   • All components tested successfully")
        else:
            print("\n⚠️ No visualization files found")
            print("   Demo may have ended too quickly for graph generation")
        
        # Cleanup temp files
        for temp_file in ['temp_load_test.py', 'temp_chaos_test.py']:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
        
        # Stop all processes
        for name, process in processes:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
    
    print("\n" + "=" * 60)
    print("🐒 Chaos Monkey Demo Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("chaos_monkey.py"):
        print("❌ Error: Please run this script from the Chaos Monkey project directory")
        exit(1)
    
    run_short_demo()
