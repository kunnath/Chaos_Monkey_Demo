# Chaos Monkey Demo 🐒


A comprehensive chaos engineering demonstration tool that tests system resilience by introducing controlled failures and monitoring system behavior.

## Overview

This Chaos Monkey implementation helps you understand how your applications behave under stress and failure conditions. It includes a complete demo ecosystem with:

- **Demo Web Application**: A Flask-based web service that simulates real application behavior
- **Chaos Monkey**: The core chaos engineering tool that introduces various failure scenarios
- **Load Tester**: Generates realistic traffic to stress-test the application
- **System Monitor**: Real-time monitoring of system resources and application health
- **Demo Runner**: Orchestrates the complete demonstration
- **Interactive Dashboard**: Web-based Streamlit interface for real-time control and monitoring

## Features

### 🐒 Chaos Monkey Experiments
- **CPU Stress**: High CPU utilization to test performance under load
- **Memory Stress**: Memory pressure testing with controlled allocation
- **Network Latency**: Simulated network delays and connectivity issues
- **Service Disruption**: Process termination and service restart scenarios
- **Disk Pressure**: Temporary disk space consumption
- **Process Hanging**: Simulated application freezing

### 🌐 Demo Application
- Multiple API endpoints with different characteristics
- Health monitoring and metrics collection
- Realistic error simulation and recovery
- Resource-intensive operations for testing

### 📊 Monitoring & Analytics
- Real-time system resource monitoring
- Application performance metrics
- Alert system for anomaly detection
- Historical data collection and export

### 🌐 Interactive Web Dashboard
- **Real-time Monitoring**: Live system metrics with gauge charts and graphs
- **Experiment Control**: Start/stop chaos experiments with custom configurations
- **Performance Analytics**: Historical data visualization and trend analysis
- **Component Management**: Interactive control of all demo components
- **Live Logs**: Real-time log streaming and filtering
- **Responsive Design**: Modern web interface accessible from any browser

## Quick Start

### 1. Run the Complete Demo

```bash
python demo_runner.py
```

Select option 1 for the full automatic demo, which will:
1. Start the demo web application
2. Begin system monitoring
3. Start load testing
4. Launch the chaos monkey
5. Run for several minutes demonstrating various failure scenarios

### 2. Launch Interactive Dashboard

```bash
python demo_runner.py
```

Select option 8 to launch the interactive Streamlit dashboard, or run directly:

```bash
streamlit run streamlit_demo.py
```

The dashboard provides:
- **Real-time System Monitoring**: Live CPU, memory, disk, and network metrics
- **Interactive Experiment Control**: Start/stop chaos experiments with custom settings
- **Performance Analytics**: Historical data visualization and trend analysis
- **Component Management**: Control all demo components from one interface

Access the dashboard at: http://localhost:8501

### 3. Manual Component Testing

You can also run individual components:

#### Start the Demo Application
```bash
python demo_app.py
```
Access at: http://localhost:8080

#### Run System Monitoring
```bash
python system_monitor.py
```

#### Execute Load Testing
```bash
python load_tester.py
```

#### Launch Chaos Monkey
```bash
python chaos_monkey.py
```

#### Start Streamlit Dashboard
```bash
streamlit run dashboard.py
```
Access at: http://localhost:8501

## API Endpoints

The demo application provides several endpoints for testing:

- `GET /` - Home page
- `GET /health` - Health check endpoint
- `GET /api/data` - Sample data retrieval
- `GET /api/slow` - Slow processing endpoint (2-5s)
- `GET /api/memory-intensive` - Memory-heavy operations
- `GET /api/cpu-intensive` - CPU-heavy computations
- `GET /api/database` - Database simulation
- `GET /stats` - Application statistics

## Configuration

### Chaos Experiments

You can customize chaos experiments by modifying the `create_sample_experiments()` function in `chaos_monkey.py`:

```python
ChaosExperiment(
    name="Custom CPU Test",
    chaos_type=ChaosType.CPU_STRESS,
    duration=15,  # seconds
    probability=0.3,  # 30% chance
    parameters={"cores": 4}
)
```

### Load Testing

Adjust load testing parameters in `load_tester.py`:

```python
tester.start_load_test(
    requests_per_second=5.0,  # Requests per second
    duration=300,             # Test duration in seconds
    num_threads=6            # Number of concurrent threads
)
```

### Monitoring

Configure monitoring intervals in `system_monitor.py`:

```python
monitor.start_monitoring(interval=5)  # Check every 5 seconds
```

## Understanding the Output

### System Monitor Output
```
🔍 SYSTEM MONITOR - 14:30:15
================================================================================
💻 SYSTEM RESOURCES:
   CPU Usage: 45.2% (8 cores)
   Memory: 62.1% (4.8GB / 8.0GB)
   Disk: 71.3% (285.2GB / 400.0GB)
   Load Average: 2.15, 1.89, 1.67

🌐 APPLICATION STATUS:
   Status: HEALTHY
   Response Time: 45ms
   Uptime: 0:05:32.123456
   Total Requests: 1,234
   Error Count: 12
   Error Rate: 1.0%

🚨 ALERTS:
   ⚠️ High CPU usage: 85.3%
```

### Chaos Monkey Logs
```
2025-06-02 14:30:20 - INFO - 🐒 Chaos Monkey started!
2025-06-02 14:30:45 - INFO - 🔥 Executing chaos experiment: Light CPU Stress
2025-06-02 14:30:45 - INFO - 🔥 Starting CPU stress for 10 seconds
2025-06-02 14:30:55 - INFO - ✅ CPU stress experiment completed
```

### Load Tester Results
```
📈 FINAL LOAD TEST RESULTS
==================================================
Total Requests: 1,847
Successful Requests: 1,791
Failed Requests: 56
Success Rate: 97.0%
Average Response Time: 0.234s
95th Percentile: 0.567s
99th Percentile: 1.234s
```

## Safety Considerations

This demo is designed to be safe for development and testing environments:

- **Resource Limits**: Chaos experiments use controlled resource consumption
- **Temporary Effects**: All chaos effects are temporary and self-cleaning
- **Safe Defaults**: Conservative default parameters prevent system damage
- **Easy Termination**: Ctrl+C stops all components gracefully

⚠️ **Warning**: Do not run this on production systems without proper safeguards and approval.

## Educational Use Cases

### Learning Chaos Engineering
- Understand how applications respond to failures
- Learn to identify system bottlenecks
- Practice incident response procedures
- Develop resilience testing strategies

### Testing Scenarios
- **Service Discovery**: How does your system handle service outages?
- **Resource Constraints**: What happens under CPU/memory pressure?
- **Network Issues**: How resilient is your application to connectivity problems?
- **Recovery Patterns**: How quickly does your system recover from failures?

## Extending the Demo

### Adding New Chaos Experiments

1. Define a new `ChaosType` in the enum
2. Implement the experiment logic in `ChaosMonkey` class
3. Add it to the experiment list

Example:
```python
class ChaosType(Enum):
    CUSTOM_FAILURE = "custom_failure"

def _custom_failure(self, experiment: ChaosExperiment):
    """Your custom chaos experiment"""
    self.logger.info("🔥 Running custom failure scenario")
    # Your implementation here
```

### Creating Custom Applications

Replace `demo_app.py` with your own application and use the same monitoring and chaos testing infrastructure.

### Advanced Monitoring

Extend `system_monitor.py` to include:
- Custom application metrics
- External service health checks
- Database performance monitoring
- Custom alert rules

## Troubleshooting

### Application Won't Start
- Check if port 8080 is available (or 5000 if you're using the original port)
- On macOS: Disable AirPlay Receiver in System Preferences → General → AirDrop & Handoff
- Verify Python environment is activated
- Ensure all dependencies are installed

### Chaos Monkey Not Working
- Verify the application is running and accessible
- Check for permission issues (especially on macOS/Linux)
- Review chaos_monkey.log for error messages

### High Resource Usage
- Reduce chaos experiment frequency
- Lower the intensity of resource-intensive experiments
- Decrease load testing parameters

## Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

Key dependencies:
- **Flask**: Web application framework
- **psutil**: System and process monitoring
- **matplotlib**: Data visualization and plotting
- **streamlit**: Interactive web dashboard
- **plotly**: Interactive charts and graphs
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing

## Dashboard Features

The Streamlit dashboard includes multiple pages:

### 📊 Overview Page
- Real-time system metrics dashboard
- Live performance indicators
- Component status monitoring
- Quick action buttons

### 🎮 Interactive Demo Page
- Start/stop individual components
- Configure chaos experiments
- Real-time experiment monitoring
- Custom parameter settings

### 📈 Monitoring Page
- Historical performance data
- System resource trends
- Application health metrics
- Alert management

### ⚗️ Experiments Page
- Design custom chaos experiments
- Schedule automated tests
- Experiment history and results
- Advanced configuration options

### 📊 Analytics Page
- Performance trend analysis
- Failure pattern recognition
- Statistical summaries
- Export data functionality

## License

This is an educational demonstration tool. Use responsibly and at your own risk.

## Contributing

Feel free to extend this demo with:
- New chaos experiment types
- Additional monitoring capabilities
- Enhanced visualization
- More realistic application scenarios

---

**Remember**: The goal of chaos engineering is to build confidence in your system's resilience by identifying weaknesses before they cause real outages. Use this tool to learn, experiment, and improve your applications! 🐒
# Chaos_Monkey_Demo
