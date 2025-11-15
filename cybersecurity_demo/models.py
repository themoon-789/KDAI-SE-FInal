"""
Database Models
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='analyst')  # admin, analyst, viewer
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Document(db.Model):
    """Document model for knowledge base"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    content_hash = db.Column(db.String(64), unique=True)  # SHA256
    status = db.Column(db.String(20), default='pending')  # pending, processing, processed, failed
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    processed_at = db.Column(db.DateTime)
    chunk_count = db.Column(db.Integer, default=0)
    metadata = db.Column(db.JSON)
    
    user = db.relationship('User', backref='documents')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'status': self.status,
            'uploaded_by': self.user.username if self.user else None,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'chunk_count': self.chunk_count,
            'metadata': self.metadata
        }

class SecurityLog(db.Model):
    """Security log model"""
    __tablename__ = 'security_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True, nullable=False)
    source_ip = db.Column(db.String(45), index=True)  # IPv4/IPv6
    source_host = db.Column(db.String(255), index=True)
    facility = db.Column(db.Integer)
    severity = db.Column(db.String(20), index=True)  # INFO, WARNING, ERROR, CRITICAL
    message = db.Column(db.Text, nullable=False)
    raw_log = db.Column(db.Text)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'))
    threat_level = db.Column(db.String(20))  # low, medium, high, critical
    is_analyzed = db.Column(db.Boolean, default=False)
    analysis_result = db.Column(db.JSON)
    
    agent = db.relationship('Agent', backref='logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'source_ip': self.source_ip,
            'source_host': self.source_host,
            'severity': self.severity,
            'message': self.message,
            'agent': self.agent.name if self.agent else None,
            'threat_level': self.threat_level,
            'is_analyzed': self.is_analyzed
        }

class Agent(db.Model):
    """Agent model for monitoring endpoints"""
    __tablename__ = 'agents'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    agent_type = db.Column(db.String(50))  # firewall, server, router, endpoint
    ip_address = db.Column(db.String(45))
    hostname = db.Column(db.String(255))
    status = db.Column(db.String(20), default='inactive', index=True)  # active, inactive, error
    protocol = db.Column(db.String(10), default='UDP')  # UDP, TCP
    port = db.Column(db.Integer, default=514)
    last_seen = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    config = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.agent_type,
            'ip': self.ip_address,
            'hostname': self.hostname,
            'status': self.status,
            'protocol': self.protocol,
            'port': self.port,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ChatHistory(db.Model):
    """Chat history with AI"""
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    model_used = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    context_used = db.Column(db.JSON)
    
    user = db.relationship('User', backref='chat_history')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.username if self.user else None,
            'message': self.message,
            'response': self.response,
            'model': self.model_used,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class ThreatIntelligence(db.Model):
    """Threat intelligence data"""
    __tablename__ = 'threat_intelligence'
    
    id = db.Column(db.Integer, primary_key=True)
    indicator_type = db.Column(db.String(50), index=True)  # ip, domain, hash, url
    indicator_value = db.Column(db.String(500), unique=True, nullable=False, index=True)
    threat_type = db.Column(db.String(100))  # malware, phishing, c2, etc.
    severity = db.Column(db.String(20))
    source = db.Column(db.String(100))
    description = db.Column(db.Text)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    metadata = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.indicator_type,
            'value': self.indicator_value,
            'threat_type': self.threat_type,
            'severity': self.severity,
            'source': self.source,
            'description': self.description,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'is_active': self.is_active
        }
