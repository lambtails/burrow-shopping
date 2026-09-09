# Bind to Unix socket (more secure than TCP)
bind = 'unix:/run/burrow-shopping/gunicorn.sock'

# Number of worker processes
workers = 2

# Worker class (sync is default, good for most cases)
worker_class = 'sync'

# Timeout for workers (30 seconds)
timeout = 30

# Access log file
accesslog = '-'

# Error log file
errorlog = '-'

# Log level
loglevel = 'info'

# Daemonize (run in background)
daemon = False