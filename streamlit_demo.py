#!/usr/bin/env python3
"""
Streamlit Demo Dashboard for Chaos Monkey
Interactive web interface showcasing chaos engineering tools
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
import time
import subprocess
import os
import psutil
from datetime import datetime, timedelta
import numpy as np

# Configure page
st.set_page_config(
    page_title="🐒 Chaos Monkey Demo",
    page_icon="🐒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .experiment-card {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def check_demo_app():
    """Check if demo app is running"""
    try:
        response = requests.get("http://localhost:8080/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def get_system_metrics():
    """Get current system metrics"""
    try:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu,
            'memory_percent': memory.percent,
            'disk_percent': (disk.used / disk.total) * 100,
            'memory_used_gb': memory.used / (1024**3),
            'memory_total_gb': memory.total / (1024**3)
        }
    except:
        return None

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🐒 Chaos Monkey Demo Dashboard</h1>
        <p>Interactive Chaos Engineering Demonstration Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("🔧 Demo Controls")
        
        # App status
        app_running = check_demo_app()
        if app_running:
            st.success("✅ Demo App Running")
        else:
            st.error("❌ Demo App Not Running")
        
        st.markdown("---")
        
        # Navigation
        page = st.selectbox(
            "Choose Section:",
            ["🏠 Overview", "🎮 Interactive Demo", "📊 Monitoring", "🧪 Experiments", "📈 Analytics"]
        )
    
    # Main content based on selected page
    if page == "🏠 Overview":
        show_overview()
    elif page == "🎮 Interactive Demo":
        show_interactive_demo()
    elif page == "📊 Monitoring":
        show_monitoring()
    elif page == "🧪 Experiments":
        show_experiments()
    elif page == "📈 Analytics":
        show_analytics()

def show_overview():
    """Show overview page"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🌟 Welcome to Chaos Monkey Demo")
        
        st.markdown("""
        This interactive dashboard demonstrates chaos engineering principles through:
        
        ### 🎯 Core Features:
        - **🌐 Demo Application**: Flask web service with multiple endpoints
        - **🐒 Chaos Monkey**: Controlled failure injection tool
        - **📊 System Monitor**: Real-time resource and performance tracking
        - **🧪 Load Tester**: Traffic generation for realistic testing
        - **📈 Analytics**: Performance analysis and visualization
        
        ### 🚀 Quick Start:
        1. **Launch Demo App**: Start the target application
        2. **Monitor Resources**: Track system performance
        3. **Generate Load**: Create realistic traffic patterns
        4. **Inject Chaos**: Test resilience with controlled failures
        5. **Analyze Results**: Review performance impacts
        """)
    
    with col2:
        st.subheader("📊 System Status")
        
        # System metrics
        metrics = get_system_metrics()
        if metrics:
            st.metric("💻 CPU", f"{metrics['cpu_percent']:.1f}%")
            st.metric("🧠 Memory", f"{metrics['memory_percent']:.1f}%")
            st.metric("💾 Disk", f"{metrics['disk_percent']:.1f}%")
        
        # Demo app status
        if check_demo_app():
            st.success("🌐 Demo App: Healthy")
        else:
            st.error("🌐 Demo App: Offline")
        
        # Architecture diagram
        st.subheader("🏗️ Architecture")
        st.text("""
        🌐 Dashboard → Controls all components
        📱 Demo App → Provides test endpoints
        🐒 Chaos Monkey → Runs experiments
        📊 Load Tester → Generates traffic
        🔍 Monitor → Tracks performance
        """)

def show_interactive_demo():
    """Show interactive demo controls"""
    st.header("🎮 Interactive Demo Control Center")
    
    # Component controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🌐 Demo Application")
        app_running = check_demo_app()
        
        if app_running:
            st.success("✅ Running")
            if st.button("🔗 Open App"):
                st.markdown("[Open Demo App](http://localhost:8080)")
        else:
            st.error("❌ Not Running")
            if st.button("▶️ Start App"):
                st.info("Starting demo application...")
                st.code("python demo_app.py")
    
    with col2:
        st.subheader("📊 System Monitor")
        if st.button("▶️ Start Monitor"):
            st.info("Starting system monitor...")
            st.code("python system_monitor.py")
    
    with col3:
        st.subheader("🧪 Load Tester")
        if st.button("▶️ Start Load Test"):
            st.info("Starting load test...")
            st.code("python load_tester.py")
    
    # Quick experiments
    st.subheader("🚀 Quick Chaos Experiments")
    
    exp_col1, exp_col2, exp_col3 = st.columns(3)
    
    with exp_col1:
        st.markdown("""
        <div class="experiment-card">
            <h4>🔥 CPU Stress</h4>
            <p>High CPU load test</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Run CPU Test"):
            st.info("Running CPU stress experiment...")
            st.code("python chaos_monkey.py --experiment cpu_stress")
    
    with exp_col2:
        st.markdown("""
        <div class="experiment-card">
            <h4>🧠 Memory Test</h4>
            <p>Memory pressure simulation</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Run Memory Test"):
            st.info("Running memory pressure experiment...")
            st.code("python chaos_monkey.py --experiment memory_stress")
    
    with exp_col3:
        st.markdown("""
        <div class="experiment-card">
            <h4>🌐 Network Lag</h4>
            <p>Network latency injection</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Run Network Test"):
            st.info("Running network latency experiment...")
            st.code("python chaos_monkey.py --experiment network_latency")
    
    # Endpoint testing
    if check_demo_app():
        st.subheader("🔗 Test Application Endpoints")
        
        endpoint_col1, endpoint_col2, endpoint_col3, endpoint_col4 = st.columns(4)
        
        with endpoint_col1:
            if st.button("🏠 Home"):
                test_endpoint("/")
        with endpoint_col2:
            if st.button("❤️ Health"):
                test_endpoint("/health")
        with endpoint_col3:
            if st.button("📊 Stats"):
                test_endpoint("/stats")
        with endpoint_col4:
            if st.button("🐌 Slow API"):
                test_endpoint("/api/slow")

def show_monitoring():
    """Show monitoring dashboard"""
    st.header("📊 Real-time System Monitoring")
    
    # Auto-refresh
    auto_refresh = st.checkbox("🔄 Auto-refresh (5s)")
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    # Current metrics
    metrics = get_system_metrics()
    if metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💻 CPU Usage", f"{metrics['cpu_percent']:.1f}%")
        with col2:
            st.metric("🧠 Memory", f"{metrics['memory_percent']:.1f}%")
        with col3:
            st.metric("💾 Disk", f"{metrics['disk_percent']:.1f}%")
        with col4:
            if check_demo_app():
                st.metric("🌐 App Status", "Healthy")
            else:
                st.metric("🌐 App Status", "Offline")
        
        # Gauge charts
        col1, col2 = st.columns(2)
        
        with col1:
            # CPU gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=metrics['cpu_percent'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "CPU Usage (%)"},
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
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Memory gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=metrics['memory_percent'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Memory Usage (%)"},
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
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    # Historical trends (simulated)
    st.subheader("📈 Performance Trends")
    generate_sample_trends()

def show_experiments():
    """Show chaos experiments"""
    st.header("🧪 Chaos Engineering Experiments")
    
    tab1, tab2, tab3 = st.tabs(["🔥 Resource Tests", "🌐 Network Tests", "⚙️ Service Tests"])
    
    with tab1:
        st.subheader("💻 Resource Stress Tests")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### CPU Stress")
            duration = st.slider("Duration (seconds)", 5, 120, 30)
            cores = st.slider("CPU Cores", 1, 8, 4)
            
            if st.button("🚀 Run CPU Test", key="cpu"):
                run_experiment("CPU Stress", duration, {"cores": cores})
        
        with col2:
            st.markdown("### Memory Pressure")
            mem_duration = st.slider("Duration (seconds)", 5, 120, 45, key="mem_dur")
            mem_size = st.slider("Memory (MB)", 100, 2000, 500)
            
            if st.button("🚀 Run Memory Test", key="memory"):
                run_experiment("Memory Pressure", mem_duration, {"size_mb": mem_size})
    
    with tab2:
        st.subheader("🌐 Network Issue Simulation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Network Latency")
            latency_duration = st.slider("Duration (seconds)", 10, 300, 60, key="lat_dur")
            delay = st.slider("Latency (ms)", 50, 2000, 500)
            
            if st.button("🚀 Add Latency", key="latency"):
                run_experiment("Network Latency", latency_duration, {"delay_ms": delay})
        
        with col2:
            st.markdown("### Packet Loss")
            loss_duration = st.slider("Duration (seconds)", 5, 60, 20, key="loss_dur")
            loss_rate = st.slider("Loss Rate (%)", 1, 50, 10)
            
            if st.button("🚀 Simulate Loss", key="loss"):
                run_experiment("Packet Loss", loss_duration, {"loss_rate": loss_rate})
    
    with tab3:
        st.subheader("⚙️ Service Disruption")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Service Hang")
            hang_duration = st.slider("Hang Duration (seconds)", 5, 180, 30, key="hang_dur")
            
            if st.button("🚀 Simulate Hang", key="hang"):
                run_experiment("Service Hang", hang_duration, {})
        
        with col2:
            st.markdown("### Process Kill")
            if st.button("🚀 Kill Process", key="kill"):
                run_experiment("Process Kill", 0, {})

def show_analytics():
    """Show analytics and results"""
    st.header("📈 Performance Analytics")
    
    # Sample experiment results
    results_data = {
        'Experiment': ['CPU Stress', 'Memory Test', 'Network Lag', 'Service Hang'],
        'Success Rate (%)': [98.5, 96.2, 94.8, 89.3],
        'Avg Response (ms)': [245, 412, 1250, 3400],
        'Error Count': [12, 28, 45, 78],
        'Recovery Time (s)': [15, 32, 8, 120]
    }
    
    df = pd.DataFrame(results_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Success rate chart
        fig = px.bar(
            df, x='Experiment', y='Success Rate (%)',
            title='Experiment Success Rates',
            color='Success Rate (%)',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Response time vs success rate
        fig = px.scatter(
            df, x='Avg Response (ms)', y='Success Rate (%)',
            size='Error Count', color='Recovery Time (s)',
            hover_name='Experiment',
            title='Response Time vs Success Rate'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Results table
    st.subheader("📋 Detailed Results")
    st.dataframe(df, use_container_width=True)
    
    # Download results
    if st.button("📥 Download Results CSV"):
        csv = df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            f"chaos_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv"
        )

def test_endpoint(endpoint):
    """Test a demo app endpoint"""
    try:
        url = f"http://localhost:8080{endpoint}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            st.success(f"✅ {endpoint}: {response.status_code} - {response.elapsed.total_seconds()*1000:.0f}ms")
            if endpoint in ["/health", "/stats"]:
                st.json(response.json())
        else:
            st.warning(f"⚠️ {endpoint}: {response.status_code}")
    except Exception as e:
        st.error(f"❌ {endpoint}: {str(e)}")

def run_experiment(name, duration, params):
    """Simulate running an experiment"""
    st.info(f"🧪 Running {name} experiment...")
    
    progress = st.progress(0)
    for i in range(101):
        time.sleep(0.02)
        progress.progress(i)
    
    st.success(f"✅ {name} experiment completed!")
    st.json({
        "experiment": name,
        "duration": duration,
        "parameters": params,
        "timestamp": datetime.now().isoformat()
    })

def generate_sample_trends():
    """Generate sample performance trend charts"""
    # Create sample time series data
    times = pd.date_range(datetime.now() - timedelta(hours=1), datetime.now(), freq='5min')
    data = pd.DataFrame({
        'timestamp': times,
        'cpu': np.random.normal(50, 15, len(times)).clip(0, 100),
        'memory': np.random.normal(65, 10, len(times)).clip(0, 100),
        'response_time': np.random.exponential(200, len(times)).clip(50, 2000)
    })
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=('System Resources (%)', 'Response Time (ms)'),
        vertical_spacing=0.1
    )
    
    # System resources
    fig.add_trace(
        go.Scatter(x=data['timestamp'], y=data['cpu'], name='CPU %', line=dict(color='blue')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=data['timestamp'], y=data['memory'], name='Memory %', line=dict(color='green')),
        row=1, col=1
    )
    
    # Response time
    fig.add_trace(
        go.Scatter(x=data['timestamp'], y=data['response_time'], name='Response Time', line=dict(color='red')),
        row=2, col=1
    )
    
    fig.update_layout(height=500, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
