import sys
import os
from flask import request
from app import create_app
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram
from app.config import Config
from app.database import db
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = create_app()
metrics = PrometheusMetrics(app)

# Initialize metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_latency = Histogram('http_request_duration_seconds', 'HTTP request latency')

# Add default metrics
metrics.info('app_info', 'Application info', version='1.0.0')

# Add custom metrics
task_counter = metrics.counter(
    'task_operations_total',
    'Total number of task operations',
    labels={'operation': lambda: 'create' if request.method == 'POST' else 'update' if request.method == 'PUT' else 'delete' if request.method == 'DELETE' else 'read'}
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add metrics endpoint
@app.route('/metrics')
def metrics_endpoint():
    return metrics.generate_latest(), 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    logger.info("Starting application...")
    app.run(debug=True, host='0.0.0.0', port=5000)
