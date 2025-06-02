#!/usr/bin/env python3
"""
Quick Launch Script for Chaos Monkey Streamlit Dashboard
"""

import subprocess
import sys
import os

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    
    print("🐒 Chaos Monkey Streamlit Dashboard")
    print("=" * 50)
    print("🚀 Starting interactive web dashboard...")
    print("🌐 Dashboard URL: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Change to project directory
        project_dir = "/Users/kunnath/Projects/Chaos Monkey"
        os.chdir(project_dir)
        
        # Launch Streamlit with the simplified demo
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_demo.py",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false",
            "--server.headless", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")
    except FileNotFoundError:
        print("❌ Streamlit not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit", "plotly", "pandas"])
        print("✅ Packages installed. Please run the script again.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    launch_dashboard()
