"""
WSGI Entry Point for Production
Use with Gunicorn: gunicorn -w 4 -b 0.0.0.0:5001 wsgi:app
"""
from app_production import create_app
import os

# Get environment
env = os.getenv('FLASK_ENV', 'production')

# Create app
app, socketio = create_app(env)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001)
