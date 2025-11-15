#!/bin/bash

# Production Startup Script
# ใช้สำหรับเริ่มระบบแบบ production

echo "🚀 Starting Cybersecurity System (Production Mode)"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if database exists
if [ ! -f "cybersecurity.db" ]; then
    echo "🗄️  Initializing database..."
    python init_db.py
fi

# Create logs directory
mkdir -p logs

# Check environment file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Copying from .env.production..."
    cp .env.production .env
    echo "⚠️  Please edit .env file with your configuration!"
    exit 1
fi

# Start the application
echo "✅ Starting application..."
echo "=================================================="

# Check if running as root (needed for port 514)
if [ "$EUID" -ne 0 ] && grep -q "SYSLOG_PORT=514" .env; then
    echo "⚠️  Warning: Port 514 requires root privileges"
    echo "Run with: sudo ./start_production.sh"
    echo "Or change SYSLOG_PORT in .env to > 1024"
fi

# Start with Gunicorn
gunicorn -c gunicorn_config.py wsgi:app
