#!/usr/bin/env python3
"""
Streamlit App Launcher for Chaos Monkey Demo
Simple launcher script that handles environment setup and app startup
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import plotly
        import pandas
        print("✅ All dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("🔧 Installing required packages...")
        
        # Install requirements
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "streamlit==1.28.1", "plotly==5.17.0", "pandas==2.1.3", 
                "numpy==1.25.2", "matplotlib==3.8.2"
            ])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def launch_streamlit():
    """Launch the Streamlit application"""
    print("🚀 Starting Chaos Monkey Streamlit Dashboard...")
    print("🌐 The dashboard will open in your default web browser")
    print("📊 Access URL: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the dashboard")
    print("-" * 60)
    
    try:
        # Change to the project directory
        os.chdir("/Users/kunnath/Projects/Chaos Monkey")
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

if __name__ == "__main__":
    print("🐒 Chaos Monkey Streamlit Dashboard Launcher")
    print("=" * 50)
    
    if check_dependencies():
        launch_streamlit()
    else:
        print("❌ Cannot start dashboard due to missing dependencies")
        print("💡 Try running: pip install -r requirements.txt")
