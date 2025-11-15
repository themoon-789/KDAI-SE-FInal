"""
Initialize Database
Creates tables and default data
"""
from app_production import create_app
from models import db, User, Agent
from datetime import datetime

def init_database():
    """Initialize database with default data"""
    app, _ = create_app('development')
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Create default users
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@cybersecurity.local',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✅ Created admin user")
        
        if not User.query.filter_by(username='analyst').first():
            analyst = User(
                username='analyst',
                email='analyst@cybersecurity.local',
                role='analyst',
                is_active=True
            )
            analyst.set_password('analyst123')
            db.session.add(analyst)
            print("✅ Created analyst user")
        
        # Create sample agents
        if Agent.query.count() == 0:
            agents = [
                Agent(
                    name='Firewall-01',
                    agent_type='firewall',
                    ip_address='192.168.1.10',
                    hostname='fw01.local',
                    status='active',
                    protocol='UDP',
                    port=514
                ),
                Agent(
                    name='Windows-Server-01',
                    agent_type='server',
                    ip_address='192.168.1.20',
                    hostname='win-srv01.local',
                    status='active',
                    protocol='UDP',
                    port=514
                ),
                Agent(
                    name='Router-01',
                    agent_type='router',
                    ip_address='192.168.1.1',
                    hostname='router01.local',
                    status='inactive',
                    protocol='UDP',
                    port=514
                )
            ]
            
            for agent in agents:
                db.session.add(agent)
            
            print(f"✅ Created {len(agents)} sample agents")
        
        db.session.commit()
        print("✅ Database initialized successfully!")

if __name__ == '__main__':
    init_database()
