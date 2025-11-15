#!/usr/bin/env python3
"""
System Readiness Check
ตรวจสอบว่าระบบพร้อมใช้งานหรือไม่
"""
import sys
import os
import importlib.util

def check_python_version():
    """ตรวจสอบ Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Required: 3.8+)")
        return False

def check_dependencies():
    """ตรวจสอบ dependencies"""
    print("\n📦 Checking dependencies...")
    
    required = {
        'flask': 'Flask',
        'flask_sqlalchemy': 'Flask-SQLAlchemy',
        'flask_jwt_extended': 'Flask-JWT-Extended',
        'flask_cors': 'Flask-CORS',
        'flask_limiter': 'Flask-Limiter',
        'flask_socketio': 'Flask-SocketIO',
        'sqlalchemy': 'SQLAlchemy',
        'chromadb': 'ChromaDB',
        'sentence_transformers': 'Sentence Transformers',
        'PyPDF2': 'PyPDF2',
        'docx': 'python-docx',
        'requests': 'requests',
        'dotenv': 'python-dotenv',
        'werkzeug': 'Werkzeug',
        'gunicorn': 'Gunicorn'
    }
    
    all_ok = True
    for module, name in required.items():
        spec = importlib.util.find_spec(module)
        if spec is not None:
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name} (Not installed)")
            all_ok = False
    
    return all_ok

def check_files():
    """ตรวจสอบไฟล์ที่จำเป็น"""
    print("\n📁 Checking required files...")
    
    required_files = [
        'app_production.py',
        'models.py',
        'config.py',
        'auth.py',
        'syslog_server.py',
        'document_processor.py',
        'vector_store.py',
        'ai_chat_enhanced.py',
        'init_db.py',
        'wsgi.py',
        'gunicorn_config.py',
        'requirements.txt'
    ]
    
    all_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (Missing)")
            all_ok = False
    
    return all_ok

def check_directories():
    """ตรวจสอบ directories"""
    print("\n📂 Checking directories...")
    
    required_dirs = [
        'uploads',
        'data',
        'templates'
    ]
    
    all_ok = True
    for dir in required_dirs:
        if os.path.exists(dir):
            print(f"   ✅ {dir}/")
        else:
            print(f"   ⚠️  {dir}/ (Will be created)")
            try:
                os.makedirs(dir, exist_ok=True)
                print(f"      ✅ Created {dir}/")
            except Exception as e:
                print(f"      ❌ Failed to create: {e}")
                all_ok = False
    
    return all_ok

def check_env_file():
    """ตรวจสอบ .env file"""
    print("\n⚙️  Checking configuration...")
    
    if os.path.exists('.env'):
        print("   ✅ .env file exists")
        
        # Check important variables
        from dotenv import load_dotenv
        load_dotenv()
        
        important_vars = [
            'SECRET_KEY',
            'DATABASE_URL',
            'SYSLOG_PORT'
        ]
        
        for var in important_vars:
            value = os.getenv(var)
            if value:
                print(f"   ✅ {var} is set")
            else:
                print(f"   ⚠️  {var} not set (using default)")
        
        return True
    else:
        print("   ⚠️  .env file not found")
        print("      Copy from .env.production:")
        print("      cp .env.production .env")
        return False

def check_database():
    """ตรวจสอบ database"""
    print("\n🗄️  Checking database...")
    
    if os.path.exists('cybersecurity.db'):
        print("   ✅ Database exists (cybersecurity.db)")
        return True
    else:
        print("   ⚠️  Database not found")
        print("      Initialize with: python init_db.py")
        return False

def check_port_availability():
    """ตรวจสอบ port availability"""
    print("\n🔌 Checking port availability...")
    
    import socket
    
    ports = {
        5001: 'Web Application',
        514: 'Syslog Server (requires root/sudo)'
    }
    
    all_ok = True
    for port, name in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result != 0:
            print(f"   ✅ Port {port} available ({name})")
        else:
            print(f"   ⚠️  Port {port} in use ({name})")
            if port == 514:
                print(f"      Note: Port 514 requires root privileges")
                print(f"      Or change SYSLOG_PORT in .env to > 1024")
    
    return all_ok

def print_summary(checks):
    """แสดงสรุป"""
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    total = len(checks)
    passed = sum(checks.values())
    
    for name, status in checks.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name}")
    
    print("="*60)
    print(f"Result: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 System is ready!")
        print("\nNext steps:")
        print("1. python init_db.py (if database not exists)")
        print("2. python app_production.py")
        print("3. Open http://localhost:5001")
        print("4. Login: admin / admin123")
        return True
    else:
        print("\n⚠️  System needs attention!")
        print("\nPlease fix the issues above before starting.")
        return False

def main():
    """Main check function"""
    print("="*60)
    print("🔍 CYBERSECURITY SYSTEM - READINESS CHECK")
    print("="*60)
    
    checks = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Required Files': check_files(),
        'Directories': check_directories(),
        'Configuration': check_env_file(),
        'Database': check_database(),
        'Port Availability': check_port_availability()
    }
    
    ready = print_summary(checks)
    
    return 0 if ready else 1

if __name__ == '__main__':
    sys.exit(main())
