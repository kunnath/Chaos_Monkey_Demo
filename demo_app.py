#!/usr/bin/env python3
"""
Sample Web Application for Chaos Monkey Testing
This is a simple Flask application that demonstrates resilience patterns.
"""

from flask import Flask, jsonify, request
import time
import random
import threading
import logging
from datetime import datetime
import psutil


app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Application state
app_state = {
    'start_time': datetime.now(),
    'request_count': 0,
    'error_count': 0,
    'health_status': 'healthy'
}


@app.route('/')
def home():
    """Home endpoint"""
    app_state['request_count'] += 1
    return jsonify({
        'message': 'Welcome to Chaos Monkey Demo App',
        'status': 'running',
        'uptime': str(datetime.now() - app_state['start_time']),
        'requests_served': app_state['request_count']
    })


@app.route('/health')
def health_check():
    """Health check endpoint"""
    app_state['request_count'] += 1
    
    # Simulate occasional health issues
    if random.random() < 0.1:  # 10% chance of health issue
        app_state['health_status'] = 'degraded'
        return jsonify({
            'status': 'degraded',
            'timestamp': datetime.now().isoformat(),
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent
        }), 503
    
    app_state['health_status'] = 'healthy'
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': str(datetime.now() - app_state['start_time']),
        'cpu_usage': psutil.cpu_percent(),
        'memory_usage': psutil.virtual_memory().percent,
        'requests_served': app_state['request_count'],
        'error_count': app_state['error_count']
    })


@app.route('/api/data')
def get_data():
    """API endpoint that simulates data retrieval"""
    app_state['request_count'] += 1
    
    # Simulate processing time
    processing_time = random.uniform(0.1, 0.5)
    time.sleep(processing_time)
    
    # Simulate occasional errors
    if random.random() < 0.05:  # 5% error rate
        app_state['error_count'] += 1
        return jsonify({'error': 'Service temporarily unavailable'}), 500
    
    # Return mock data
    data = {
        'id': random.randint(1, 1000),
        'timestamp': datetime.now().isoformat(),
        'processing_time': processing_time,
        'data': [random.randint(1, 100) for _ in range(10)]
    }
    
    return jsonify(data)


@app.route('/api/slow')
def slow_endpoint():
    """Endpoint that simulates slow processing"""
    app_state['request_count'] += 1
    
    # Simulate slow processing (2-5 seconds)
    delay = random.uniform(2, 5)
    logger.info(f"Processing slow request with {delay:.2f}s delay")
    time.sleep(delay)
    
    return jsonify({
        'message': 'Slow operation completed',
        'processing_time': delay,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/memory-intensive')
def memory_intensive():
    """Endpoint that uses significant memory"""
    app_state['request_count'] += 1
    
    # Allocate some memory temporarily
    large_data = []
    try:
        for i in range(1000):
            large_data.append([random.random() for _ in range(1000)])
        
        # Process the data
        result = sum(sum(row) for row in large_data)
        
        return jsonify({
            'message': 'Memory intensive operation completed',
            'result': result,
            'memory_allocated': '~8MB',
            'timestamp': datetime.now().isoformat()
        })
    
    finally:
        # Clean up memory
        large_data.clear()


@app.route('/api/cpu-intensive')
def cpu_intensive():
    """Endpoint that performs CPU-intensive operations"""
    app_state['request_count'] += 1
    
    # Perform CPU-intensive calculation
    start_time = time.time()
    result = 0
    
    for i in range(1000000):
        result += i ** 2
    
    processing_time = time.time() - start_time
    
    return jsonify({
        'message': 'CPU intensive operation completed',
        'result': result,
        'processing_time': processing_time,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/database')
def database_simulation():
    """Simulate database operations"""
    app_state['request_count'] += 1
    
    # Simulate database query time
    query_time = random.uniform(0.1, 1.0)
    time.sleep(query_time)
    
    # Simulate occasional database connection issues
    if random.random() < 0.08:  # 8% chance of DB issue
        app_state['error_count'] += 1
        return jsonify({'error': 'Database connection timeout'}), 504
    
    return jsonify({
        'message': 'Database query completed',
        'query_time': query_time,
        'records_found': random.randint(1, 100),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/stats')
def get_stats():
    """Get application statistics"""
    return jsonify({
        'uptime': str(datetime.now() - app_state['start_time']),
        'total_requests': app_state['request_count'],
        'error_count': app_state['error_count'],
        'error_rate': app_state['error_count'] / max(app_state['request_count'], 1),
        'health_status': app_state['health_status'],
        'system_info': {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        }
    })


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    app_state['error_count'] += 1
    return jsonify({
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500


@app.errorhandler(503)
def service_unavailable(error):
    """Handle service unavailable errors"""
    app_state['error_count'] += 1
    return jsonify({
        'error': 'Service temporarily unavailable',
        'timestamp': datetime.now().isoformat()
    }), 503


def background_task():
    """Background task that runs periodically"""
    while True:
        try:
            # Simulate background processing
            time.sleep(30)
            logger.info(f"Background task executed. Requests served: {app_state['request_count']}")
            
            # Reset health status periodically
            if app_state['health_status'] == 'degraded' and random.random() < 0.7:
                app_state['health_status'] = 'healthy'
                logger.info("Health status recovered to healthy")
                
        except Exception as e:
            logger.error(f"Background task error: {e}")


if __name__ == '__main__':
    # Start background task
    background_thread = threading.Thread(target=background_task, daemon=True)
    background_thread.start()
    
    print("🌐 Starting Demo Web Application")
    print("Available endpoints:")
    print("  GET /                    - Home page")
    print("  GET /health             - Health check")
    print("  GET /api/data           - Get sample data")
    print("  GET /api/slow           - Slow processing endpoint")
    print("  GET /api/memory-intensive - Memory intensive operation")
    print("  GET /api/cpu-intensive  - CPU intensive operation")
    print("  GET /api/database       - Database simulation")
    print("  GET /stats              - Application statistics")
    print("\nStarting server on http://localhost:8080")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
