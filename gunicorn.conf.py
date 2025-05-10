import multiprocessing
import os

# Server socket
bind = "0.0.0.0:" + str(os.getenv("PORT", "5000"))
backlog = 2048

# Worker processes
workers = 2  # Reduced from CPU count * 2 + 1 to prevent memory issues
worker_class = "sync"
worker_connections = 1000
timeout = 120  # Increased timeout
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "task-manager"

# SSL
keyfile = None
certfile = None

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Memory settings
max_requests = 1000
max_requests_jitter = 50
worker_tmp_dir = "/dev/shm"  # Use RAM for temporary files

# Server hooks
def on_starting(server):
    pass

def on_reload(server):
    pass

def on_exit(server):
    pass 