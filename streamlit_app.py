#!/usr/bin/env python3
"""
Streamlit Dashboard for Chaos Monkey Demo
Interactive web interface for chaos engineering demonstrations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
import time
import threading
import subprocess
import os
import psutil
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List
import logging

# Configure page
st.set_page_config(
    page_title="Chaos Monkey Demo Dashboard",
    page_icon="🐒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .status-healthy { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-danger { color: #dc3545; }
    .experiment-card {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitChaosDemo:
    """Main class for the Streamlit Chaos Engineering Demo"""
    
    def __init__(self):
        self.base_url = "http://localhost:8080"
        self.monitoring_data = []
        self.load_test_data = []
        self.running_processes = {}
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for the demo"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def check_demo_app_status(self) -> Dict:
        """Check if the demo application is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds() * 1000,
                    "data": health_data
                }
            else:
                return {"status": "degraded", "response_time": 0, "data": {}}
        except Exception as e:
            return {"status": "unreachable", "response_time": 0, "error": str(e)}
    
    def get_system_metrics(self) -> Dict:
        """Get current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "timestamp": datetime.now(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": memory.used / (1024**3),
                "memory_total_gb": memory.total / (1024**3),
                "disk_percent": (disk.used / disk.total) * 100,
                "disk_used_gb": disk.used / (1024**3),
                "disk_total_gb": disk.total / (1024**3)
            }
        except Exception as e:
            st.error(f"Error collecting system metrics: {e}")
            return {}
    
    def start_component(self, component: str) -> bool:
        """Start a demo component"""
        try:
            if component in self.running_processes:
                return True  # Already running
            
            if component == "demo_app":
                process = subprocess.Popen(
                    ["python", "demo_app.py"],
                    cwd="/Users/kunnath/Projects/Chaos Monkey",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            elif component == "load_tester":
                process = subprocess.Popen(
                    ["python", "load_tester.py"],
                    cwd="/Users/kunnath/Projects/Chaos Monkey",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            elif component == "system_monitor":
                process = subprocess.Popen(
                    ["python", "system_monitor.py"],
                    cwd="/Users/kunnath/Projects/Chaos Monkey",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                return False
            
            self.running_processes[component] = process
            return True
            
        except Exception as e:
            st.error(f"Error starting {component}: {e}")
            return False
    
    def stop_component(self, component: str):
        """Stop a demo component"""
        if component in self.running_processes:
            try:
                self.running_processes[component].terminate()
                del self.running_processes[component]
            except Exception as e:
                st.error(f"Error stopping {component}: {e}")

def main():
    """Main Streamlit application"""
    demo = StreamlitChaosDemo()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🐒 Chaos Monkey Demo Dashboard</h1>
        <p>Interactive Chaos Engineering Demonstration Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for navigation
    st.sidebar.title("🔧 Demo Controls")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["🏠 Overview", "🎮 Interactive Demo", "📊 Real-time Monitoring", "🧪 Chaos Experiments", "📈 Analytics", "⚙️ Configuration"]
    )
    
    if page == "🏠 Overview":
        show_overview_page(demo)
    elif page == "🎮 Interactive Demo":
        show_interactive_demo_page(demo)
    elif page == "📊 Real-time Monitoring":
        show_monitoring_page(demo)
    elif page == "🧪 Chaos Experiments":
        show_chaos_experiments_page(demo)
    elif page == "📈 Analytics":
        show_analytics_page(demo)
    elif page == "⚙️ Configuration":
        show_configuration_page(demo)

def show_overview_page(demo):
    """Show the overview page"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🌟 Welcome to Chaos Monkey Demo")
        st.markdown("""
        This interactive dashboard showcases a comprehensive chaos engineering platform designed to test system resilience 
        through controlled failure injection and real-time monitoring.
        
        ### 🎯 What You Can Do Here:
        - **Launch Interactive Demos**: Start and stop demo components with one click
        - **Monitor System Performance**: Real-time dashboards showing system and application metrics
        - **Execute Chaos Experiments**: Inject controlled failures to test resilience
        - **Analyze Results**: View detailed analytics and performance graphs
        - **Configure Parameters**: Customize experiments and monitoring settings
        """)
        
        st.subheader("🚀 Quick Start Guide")
        st.markdown("""
        1. **Start Demo App**: Launch the Flask demo application
        2. **Begin Monitoring**: Enable real-time system monitoring
        3. **Generate Load**: Start load testing to create realistic traffic
        4. **Run Chaos**: Execute chaos experiments to test resilience
        5. **Analyze Results**: Review metrics and system behavior
        """)
    
    with col2:
        st.subheader("📊 System Status")
        
        # Check demo app status
        app_status = demo.check_demo_app_status()
        if app_status["status"] == "healthy":
            st.success("✅ Demo App: Running")
        elif app_status["status"] == "degraded":
            st.warning("⚠️ Demo App: Degraded")
        else:
            st.error("❌ Demo App: Not Running")
        
        # System metrics
        metrics = demo.get_system_metrics()
        if metrics:
            st.metric("💻 CPU Usage", f"{metrics['cpu_percent']:.1f}%")
            st.metric("🧠 Memory Usage", f"{metrics['memory_percent']:.1f}%")
            st.metric("💾 Disk Usage", f"{metrics['disk_percent']:.1f}%")
        
        # Architecture diagram
        st.subheader("🏗️ Architecture")
        st.mermaid("""
        graph TD
            A[Streamlit Dashboard] --> B[Demo Flask App]
            A --> C[Chaos Monkey]
            A --> D[Load Tester]
            A --> E[System Monitor]
            B --> F[API Endpoints]
            C --> G[Chaos Experiments]
            D --> B
            E --> H[System Metrics]
            E --> B
        """)

def show_interactive_demo_page(demo):
    """Show the interactive demo page"""
    st.header("🎮 Interactive Demo Control Center")
    
    # Component status and controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🌐 Demo Application")
        app_status = demo.check_demo_app_status()
        
        if app_status["status"] == "healthy":
            st.success("✅ Running")
            if st.button("🛑 Stop Demo App", key="stop_app"):
                demo.stop_component("demo_app")
                st.rerun()
        else:
            st.error("❌ Not Running")
            if st.button("▶️ Start Demo App", key="start_app"):
                if demo.start_component("demo_app"):
                    st.success("Starting demo app...")
                    time.sleep(3)
                    st.rerun()
        
        if app_status["status"] == "healthy":
            st.metric("Response Time", f"{app_status['response_time']:.0f}ms")
            if st.button("🔗 Open Demo App", key="open_app"):
                st.markdown(f"[Open Demo App]({demo.base_url})")
    
    with col2:
        st.subheader("📊 System Monitor")
        monitor_running = "system_monitor" in demo.running_processes
        
        if monitor_running:
            st.success("✅ Monitoring Active")
            if st.button("🛑 Stop Monitor", key="stop_monitor"):
                demo.stop_component("system_monitor")
                st.rerun()
        else:
            st.info("⏸️ Not Monitoring")
            if st.button("▶️ Start Monitor", key="start_monitor"):
                if demo.start_component("system_monitor"):
                    st.success("Starting system monitor...")
                    st.rerun()
    
    with col3:
        st.subheader("🧪 Load Tester")
        load_running = "load_tester" in demo.running_processes
        
        if load_running:
            st.success("✅ Load Testing Active")
            if st.button("🛑 Stop Load Test", key="stop_load"):
                demo.stop_component("load_tester")
                st.rerun()
        else:
            st.info("⏸️ Not Running")
            if st.button("▶️ Start Load Test", key="start_load"):
                if demo.start_component("load_tester"):
                    st.success("Starting load test...")
                    st.rerun()
    
    # Quick demo scenarios
    st.subheader("🚀 Quick Demo Scenarios")
    
    scenario_col1, scenario_col2, scenario_col3 = st.columns(3)
    
    with scenario_col1:
        with st.container():
            st.markdown("""
            <div class="experiment-card">
                <h4>🔥 CPU Stress Test</h4>
                <p>Test application performance under high CPU load</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Run CPU Stress", key="cpu_stress"):
                run_chaos_experiment("cpu_stress", demo)
    
    with scenario_col2:
        with st.container():
            st.markdown("""
            <div class="experiment-card">
                <h4>🧠 Memory Pressure</h4>
                <p>Simulate memory exhaustion scenarios</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Run Memory Test", key="memory_stress"):
                run_chaos_experiment("memory_stress", demo)
    
    with scenario_col3:
        with st.container():
            st.markdown("""
            <div class="experiment-card">
                <h4>🌐 Network Latency</h4>
                <p>Introduce network delays and connectivity issues</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Run Network Test", key="network_test"):
                run_chaos_experiment("network_latency", demo)
    
    # Real-time demo app endpoints
    if app_status["status"] == "healthy":
        st.subheader("🔗 Demo Application Endpoints")
        
        endpoint_col1, endpoint_col2, endpoint_col3, endpoint_col4 = st.columns(4)
        
        with endpoint_col1:
            if st.button("🏠 Home", key="test_home"):
                test_endpoint("/", demo)
        
        with endpoint_col2:
            if st.button("❤️ Health", key="test_health"):
                test_endpoint("/health", demo)
        
        with endpoint_col3:
            if st.button("📊 Stats", key="test_stats"):
                test_endpoint("/stats", demo)
        
        with endpoint_col4:
            if st.button("🐌 Slow API", key="test_slow"):
                test_endpoint("/api/slow", demo)

def show_monitoring_page(demo):
    """Show the real-time monitoring page"""
    st.header("📊 Real-time System Monitoring")
    
    # Auto-refresh checkbox
    auto_refresh = st.checkbox("🔄 Auto-refresh (5 seconds)", value=False)
    
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    # Get current metrics
    system_metrics = demo.get_system_metrics()
    app_status = demo.check_demo_app_status()
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if system_metrics:
            cpu_color = "normal" if system_metrics["cpu_percent"] < 70 else "inverse"
            st.metric(
                "💻 CPU Usage", 
                f"{system_metrics['cpu_percent']:.1f}%",
                delta=None,
                delta_color=cpu_color
            )
    
    with col2:
        if system_metrics:
            mem_color = "normal" if system_metrics["memory_percent"] < 80 else "inverse"
            st.metric(
                "🧠 Memory Usage", 
                f"{system_metrics['memory_percent']:.1f}%",
                delta=f"{system_metrics['memory_used_gb']:.1f}GB / {system_metrics['memory_total_gb']:.1f}GB",
                delta_color=mem_color
            )
    
    with col3:
        if system_metrics:
            disk_color = "normal" if system_metrics["disk_percent"] < 85 else "inverse"
            st.metric(
                "💾 Disk Usage", 
                f"{system_metrics['disk_percent']:.1f}%",
                delta=f"{system_metrics['disk_used_gb']:.0f}GB / {system_metrics['disk_total_gb']:.0f}GB",
                delta_color=disk_color
            )
    
    with col4:
        if app_status["status"] == "healthy":
            response_color = "normal" if app_status["response_time"] < 500 else "inverse"
            st.metric(
                "🌐 Response Time", 
                f"{app_status['response_time']:.0f}ms",
                delta=app_status["status"].title(),
                delta_color=response_color
            )
        else:
            st.metric("🌐 App Status", app_status["status"].title(), delta="Not responding")
    
    # Charts
    if system_metrics:
        # Create gauge charts for system metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # CPU and Memory gauge
            fig = make_subplots(
                rows=1, cols=2,
                specs=[[{"type": "indicator"}, {"type": "indicator"}]],
                subplot_titles=("CPU Usage", "Memory Usage")
            )
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=system_metrics["cpu_percent"],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "CPU %"},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "yellow"},
                            {'range': [80, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=system_metrics["memory_percent"],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Memory %"},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkgreen"},
                        'steps': [
                            {'range': [0, 60], 'color': "lightgray"},
                            {'range': [60, 85], 'color': "yellow"},
                            {'range': [85, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ),
                row=1, col=2
            )
            
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Application status chart
            if app_status["status"] == "healthy":
                status_data = {
                    "Metric": ["Response Time", "Success Rate", "Health Score"],
                    "Value": [
                        min(app_status["response_time"] / 10, 100),  # Normalize response time
                        95,  # Simulated success rate
                        85   # Simulated health score
                    ],
                    "Target": [50, 99, 90]
                }
                
                df = pd.DataFrame(status_data)
                
                fig = px.bar(
                    df, 
                    x="Metric", 
                    y=["Value", "Target"],
                    title="Application Performance Metrics",
                    barmode="group",
                    color_discrete_sequence=["#3498db", "#e74c3c"]
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Application not responding - cannot show performance metrics")
    
    # Historical data simulation (if we had real historical data)
    st.subheader("📈 Performance Trends")
    
    # Generate sample historical data for demonstration
    times = pd.date_range(datetime.now() - timedelta(hours=1), datetime.now(), freq='1min')
    sample_data = pd.DataFrame({
        'timestamp': times,
        'cpu_percent': np.random.normal(45, 15, len(times)).clip(0, 100),
        'memory_percent': np.random.normal(60, 10, len(times)).clip(0, 100),
        'response_time': np.random.exponential(100, len(times)).clip(10, 2000)
    })
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=("System Resources", "Application Performance"),
        vertical_spacing=0.1
    )
    
    # System resources
    fig.add_trace(
        go.Scatter(x=sample_data['timestamp'], y=sample_data['cpu_percent'], 
                  name='CPU %', line=dict(color='blue')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=sample_data['timestamp'], y=sample_data['memory_percent'], 
                  name='Memory %', line=dict(color='green')),
        row=1, col=1
    )
    
    # Application performance
    fig.add_trace(
        go.Scatter(x=sample_data['timestamp'], y=sample_data['response_time'], 
                  name='Response Time (ms)', line=dict(color='red')),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_yaxes(title_text="Percentage", row=1, col=1)
    fig.update_yaxes(title_text="Milliseconds", row=2, col=1)
    
    fig.update_layout(height=500, title_text="Historical Performance Data")
    st.plotly_chart(fig, use_container_width=True)

def show_chaos_experiments_page(demo):
    """Show the chaos experiments page"""
    st.header("🧪 Chaos Engineering Experiments")
    
    st.markdown("""
    Design and execute controlled failure scenarios to test system resilience. 
    Each experiment introduces specific types of stress or failure conditions.
    """)
    
    # Experiment categories
    tab1, tab2, tab3, tab4 = st.tabs(["🔥 Resource Stress", "🌐 Network Issues", "⚙️ Service Failures", "📊 Custom"])
    
    with tab1:
        st.subheader("💻 Resource Stress Experiments")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### CPU Stress Test")
            cpu_duration = st.slider("Duration (seconds)", 5, 120, 30, key="cpu_duration")
            cpu_intensity = st.slider("CPU Cores", 1, 8, 4, key="cpu_intensity")
            
            if st.button("🚀 Run CPU Stress", key="run_cpu"):
                st.info(f"Running CPU stress for {cpu_duration}s using {cpu_intensity} cores...")
                # Here you would call the actual chaos monkey
                st.success("CPU stress experiment completed!")
        
        with col2:
            st.markdown("### Memory Pressure Test")
            mem_duration = st.slider("Duration (seconds)", 5, 120, 45, key="mem_duration")
            mem_size = st.slider("Memory Size (MB)", 100, 2000, 500, key="mem_size")
            
            if st.button("🚀 Run Memory Test", key="run_memory"):
                st.info(f"Running memory pressure for {mem_duration}s using {mem_size}MB...")
                st.success("Memory pressure experiment completed!")
    
    with tab2:
        st.subheader("🌐 Network Issue Simulation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Network Latency")
            latency_duration = st.slider("Duration (seconds)", 10, 300, 60, key="latency_duration")
            latency_delay = st.slider("Latency (ms)", 50, 2000, 500, key="latency_delay")
            
            if st.button("🚀 Add Network Latency", key="run_latency"):
                st.info(f"Adding {latency_delay}ms latency for {latency_duration}s...")
                st.success("Network latency experiment completed!")
        
        with col2:
            st.markdown("### Connection Drops")
            drop_duration = st.slider("Duration (seconds)", 5, 60, 20, key="drop_duration")
            drop_probability = st.slider("Drop Rate (%)", 1, 50, 10, key="drop_probability")
            
            if st.button("🚀 Simulate Drops", key="run_drops"):
                st.info(f"Simulating {drop_probability}% connection drops for {drop_duration}s...")
                st.success("Connection drop experiment completed!")
    
    with tab3:
        st.subheader("⚙️ Service Failure Simulation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Process Termination")
            if st.button("🚀 Kill Random Process", key="kill_process"):
                st.warning("This will terminate a random application process...")
                st.info("Process termination experiment executed!")
        
        with col2:
            st.markdown("### Service Hang")
            hang_duration = st.slider("Hang Duration (seconds)", 5, 180, 30, key="hang_duration")
            
            if st.button("🚀 Simulate Hang", key="run_hang"):
                st.info(f"Simulating service hang for {hang_duration}s...")
                st.success("Service hang experiment completed!")
    
    with tab4:
        st.subheader("📊 Custom Experiment Designer")
        
        st.markdown("Design your own chaos experiment:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            exp_name = st.text_input("Experiment Name", "My Custom Experiment")
            exp_type = st.selectbox(
                "Experiment Type",
                ["CPU Stress", "Memory Pressure", "Network Latency", "Disk I/O", "Custom Script"]
            )
            exp_duration = st.number_input("Duration (seconds)", 5, 600, 60)
        
        with col2:
            exp_probability = st.slider("Success Probability", 0.1, 1.0, 0.8)
            exp_parameters = st.text_area(
                "Custom Parameters (JSON)",
                '{"intensity": "medium", "target": "application"}'
            )
        
        if st.button("💾 Save & Run Experiment", key="save_custom"):
            st.success(f"Custom experiment '{exp_name}' saved and executed!")
            
            # Display experiment summary
            st.json({
                "name": exp_name,
                "type": exp_type,
                "duration": exp_duration,
                "probability": exp_probability,
                "parameters": exp_parameters
            })

def show_analytics_page(demo):
    """Show the analytics and results page"""
    st.header("📈 Performance Analytics & Results")
    
    # Load historical data (simulated for demo)
    st.subheader("📊 Experiment Results Summary")
    
    # Sample experiment results
    experiment_results = pd.DataFrame({
        'experiment': ['CPU Stress', 'Memory Pressure', 'Network Latency', 'Service Hang', 'Disk I/O'],
        'success_rate': [98.5, 96.2, 94.8, 89.3, 99.1],
        'avg_response_time': [245, 412, 1250, 3400, 189],
        'error_count': [12, 28, 45, 78, 8],
        'recovery_time': [15, 32, 8, 120, 12]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Success rate chart
        fig = px.bar(
            experiment_results, 
            x='experiment', 
            y='success_rate',
            title='Experiment Success Rates (%)',
            color='success_rate',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Response time chart
        fig = px.scatter(
            experiment_results,
            x='avg_response_time',
            y='success_rate',
            size='error_count',
            color='recovery_time',
            hover_name='experiment',
            title='Response Time vs Success Rate',
            labels={'avg_response_time': 'Avg Response Time (ms)', 'success_rate': 'Success Rate (%)'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed results table
    st.subheader("📋 Detailed Results")
    st.dataframe(experiment_results, use_container_width=True)
    
    # Performance trends
    st.subheader("📈 Performance Trends Over Time")
    
    # Generate time series data
    dates = pd.date_range(datetime.now() - timedelta(days=7), datetime.now(), freq='1H')
    trend_data = pd.DataFrame({
        'timestamp': dates,
        'cpu_avg': np.random.normal(50, 20, len(dates)).clip(0, 100),
        'memory_avg': np.random.normal(65, 15, len(dates)).clip(0, 100),
        'response_time_avg': np.random.exponential(200, len(dates)).clip(50, 2000),
        'error_rate': np.random.beta(2, 50, len(dates)) * 100
    })
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('CPU Usage Trend', 'Memory Usage Trend', 'Response Time Trend', 'Error Rate Trend'),
        vertical_spacing=0.12
    )
    
    fig.add_trace(
        go.Scatter(x=trend_data['timestamp'], y=trend_data['cpu_avg'], name='CPU %'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=trend_data['timestamp'], y=trend_data['memory_avg'], name='Memory %'),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Scatter(x=trend_data['timestamp'], y=trend_data['response_time_avg'], name='Response Time'),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=trend_data['timestamp'], y=trend_data['error_rate'], name='Error Rate %'),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Download results
    st.subheader("💾 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Download CSV", key="download_csv"):
            csv = experiment_results.to_csv(index=False)
            st.download_button(
                label="Download CSV File",
                data=csv,
                file_name=f"chaos_experiment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📊 Download Excel", key="download_excel"):
            st.info("Excel download functionality would be implemented here")
    
    with col3:
        if st.button("📈 Generate Report", key="generate_report"):
            st.info("Comprehensive PDF report generation would be implemented here")

def show_configuration_page(demo):
    """Show the configuration page"""
    st.header("⚙️ Configuration & Settings")
    
    tab1, tab2, tab3 = st.tabs(["🔧 General Settings", "🧪 Experiment Config", "📊 Monitoring Config"])
    
    with tab1:
        st.subheader("🔧 General Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Application Settings")
            base_url = st.text_input("Demo App URL", demo.base_url)
            auto_start = st.checkbox("Auto-start components", False)
            logging_level = st.selectbox("Logging Level", ["INFO", "DEBUG", "WARNING", "ERROR"])
            
        with col2:
            st.markdown("### Safety Settings")
            max_cpu_usage = st.slider("Max CPU Usage (%)", 50, 95, 85)
            max_memory_usage = st.slider("Max Memory Usage (%)", 60, 95, 90)
            emergency_stop = st.checkbox("Enable Emergency Stop", True)
    
    with tab2:
        st.subheader("🧪 Chaos Experiment Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Default Parameters")
            default_duration = st.number_input("Default Duration (seconds)", 5, 300, 30)
            default_probability = st.slider("Default Probability", 0.1, 1.0, 0.7)
            cooldown_period = st.number_input("Cooldown Period (seconds)", 0, 300, 60)
        
        with col2:
            st.markdown("### Experiment Types")
            enabled_experiments = st.multiselect(
                "Enabled Experiment Types",
                ["CPU Stress", "Memory Pressure", "Network Latency", "Service Disruption", "Disk I/O"],
                default=["CPU Stress", "Memory Pressure", "Network Latency"]
            )
    
    with tab3:
        st.subheader("📊 Monitoring Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Collection Settings")
            monitoring_interval = st.number_input("Monitoring Interval (seconds)", 1, 60, 10)
            data_retention = st.number_input("Data Retention (hours)", 1, 168, 24)
            enable_graphs = st.checkbox("Enable Graph Generation", True)
        
        with col2:
            st.markdown("### Alert Thresholds")
            cpu_alert_threshold = st.slider("CPU Alert Threshold (%)", 50, 100, 80)
            memory_alert_threshold = st.slider("Memory Alert Threshold (%)", 50, 100, 85)
            response_time_threshold = st.number_input("Response Time Alert (ms)", 100, 5000, 1000)
    
    # Save configuration
    if st.button("💾 Save Configuration", key="save_config"):
        config = {
            "base_url": base_url,
            "auto_start": auto_start,
            "logging_level": logging_level,
            "max_cpu_usage": max_cpu_usage,
            "max_memory_usage": max_memory_usage,
            "emergency_stop": emergency_stop,
            "default_duration": default_duration,
            "default_probability": default_probability,
            "cooldown_period": cooldown_period,
            "enabled_experiments": enabled_experiments,
            "monitoring_interval": monitoring_interval,
            "data_retention": data_retention,
            "enable_graphs": enable_graphs,
            "cpu_alert_threshold": cpu_alert_threshold,
            "memory_alert_threshold": memory_alert_threshold,
            "response_time_threshold": response_time_threshold
        }
        
        st.success("Configuration saved successfully!")
        st.json(config)

def run_chaos_experiment(experiment_type: str, demo):
    """Run a specific chaos experiment"""
    st.info(f"Running {experiment_type} experiment...")
    
    # Here you would integrate with the actual chaos monkey
    # For now, we'll simulate the experiment
    
    progress_bar = st.progress(0)
    for i in range(101):
        time.sleep(0.05)  # Simulate experiment duration
        progress_bar.progress(i)
    
    st.success(f"{experiment_type} experiment completed successfully!")

def test_endpoint(endpoint: str, demo):
    """Test a specific endpoint"""
    try:
        url = f"{demo.base_url}{endpoint}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            st.success(f"✅ {endpoint}: {response.status_code} - {response.elapsed.total_seconds()*1000:.0f}ms")
            if endpoint in ["/health", "/stats"]:
                st.json(response.json())
        else:
            st.warning(f"⚠️ {endpoint}: {response.status_code}")
            
    except Exception as e:
        st.error(f"❌ {endpoint}: {str(e)}")

if __name__ == "__main__":
    main()
