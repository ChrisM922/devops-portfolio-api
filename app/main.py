import os
import sys
from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics
import logging

def create_app(registry=None):
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s'
    )
    logger = logging.getLogger('app')
    
    # Initialize metrics with optional registry
    metrics = PrometheusMetrics(app, path='/metrics', registry=registry)
    
    # Add default metrics
    metrics.info('app_info', 'Application info', version='1.0.0')
    
    # Add custom metrics
    request_count = metrics.counter(
        'http_requests_total',
        'Total HTTP requests',
        labels={'method': lambda: request.method, 'endpoint': lambda: request.endpoint}
    )
    
    request_latency = metrics.histogram(
        'http_request_duration_seconds',
        'HTTP request duration in seconds',
        labels={'method': lambda: request.method, 'endpoint': lambda: request.endpoint}
    )
    
    task_counter = metrics.counter(
        'task_operations_total',
        'Total task operations',
        labels={'operation': lambda: request.view_args.get('operation', 'unknown')}
    )
    
    # Application configuration
    app.config['HOST'] = '0.0.0.0'
    app.config['PORT'] = 5000
    app.debug = True
    
    return app, metrics, request_count, request_latency, task_counter

# Only create the global app instance if not being imported for testing
if not any(arg in sys.argv[0].lower() for arg in ['pytest', 'test']):
    app, metrics, request_count, request_latency, task_counter = create_app()

if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
