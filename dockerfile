FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONIOENCODING=utf-8 \
    MALLOC_TRIM_THRESHOLD_=128000 \
    MALLOC_MMAP_THRESHOLD_=131072

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget git ca-certificates \
    supervisor psutil tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p /app/data /app/logs /var/log/supervisor

# Create ultra-stable supervisor config
RUN cat > /etc/supervisor/conf.d/ultra_bot.conf << 'EOF'
[program:ultra_bot]
directory=/app
command=python3 -u ultra_stable_bot_v2.py
autostart=true
autorestart=true
startsecs=20
stopasgroup=true
stopwaitsecs=15
stdout_logfile=/app/logs/bot.log
stdout_logfile_maxbytes=20MB
stdout_logfile_backups=5
stderr_logfile=/app/logs/bot_error.log
stderr_logfile_maxbytes=20MB
stderr_logfile_backups=5
priority=999
stopsignal=TERM
environment=PYTHONUNBUFFERED=1
retry=5
priority=999

[program:flask_ultra]
directory=/app
command=gunicorn --bind 0.0.0.0:8000 --workers 1 --worker-class sync --timeout 60 --keep-alive 30 app:app
autostart=true
autorestart=true
startsecs=10
stopasgroup=true
stopwaitsecs=15
stdout_logfile=/app/logs/flask.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
stderr_logfile=/app/logs/flask_error.log
stderr_logfile_maxbytes=10MB
stderr_logfile_backups=3
priority=998
stopsignal=TERM

[group:ultra_services]
programs=ultra_bot,flask_ultra
priority=999

[supervisord]
logfile=/app/logs/supervisord.log
pidfile=/var/run/supervisord.pid
nodaemon=true
user=root
loglevel=info
childlogdir=/app/logs

[unix_http_server]
file=/var/run/supervisor.sock
chmod=0700

[supervisorctl]
serverurl=unix:///var/run/supervisor.sock

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

EOF

# Create entrypoint script
RUN cat > /app/entrypoint.sh << 'EOF'
#!/bin/bash
set -e

echo "=========================================="
echo "🚀 ULTRA-STABLE BOT v2.0"
echo "=========================================="
echo "Time: $(date)"
echo "Python: $(python3 --version)"
echo "=========================================="

# Verify credentials
if [ -z "$BOT_TOKEN" ] || [ -z "$API_ID" ] || [ -z "$API_HASH" ] || [ -z "$ADMIN_ID" ]; then
    echo "❌ Missing credentials!"
    exit 1
fi

echo "✅ All credentials present"
echo "✅ Starting supervisor..."

mkdir -p /app/data /app/logs
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf

EOF

RUN chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/app/entrypoint.sh"]
