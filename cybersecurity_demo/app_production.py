"""
Production Cybersecurity System
Real implementation with database, authentication, syslog server, and RAG
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from datetime import datetime
from werkzeug.utils import secure_filename

# Import models and utilities
from models import db, User, Document, SecurityLog, Agent, ChatHistory, ThreatIntelligence
from config import config
from auth import init_auth, authenticate_user, login_required, role_required, get_current_user
from syslog_server import SyslogServer
from document_processor import DocumentProcessor
from vector_store import VectorStore
from ai_chat_enhanced import AIChat

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    init_auth(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per hour"]
    )
    
    # SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Create folders
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Initialize components
    document_processor = DocumentProcessor()
    vector_store = VectorStore(app.config['VECTOR_DB_PATH'])
    ai_chat = AIChat(vector_store=vector_store)
    
    # Syslog server
    syslog_server = SyslogServer(
        host=app.config['SYSLOG_HOST'],
        port=app.config['SYSLOG_PORT'],
        protocol=app.config['SYSLOG_PROTOCOL'],
        socketio=socketio
    )
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@cybersecurity.local',
                role='admin'
            )
            admin.set_password('admin123')  # Change in production!
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin user created (username: admin, password: admin123)")
    
    # Start syslog server
    syslog_server.start()
    
    # ==================== Routes ====================
    
    @app.route('/')
    def index():
        """Dashboard"""
        return render_template('dashboard.html')
    
    @app.route('/knowledge')
    def knowledge():
        """Knowledge base management"""
        return render_template('knowledge.html')
    
    @app.route('/logs')
    def logs():
        """Security logs"""
        return render_template('logs.html')
    
    @app.route('/agents')
    def agents():
        """Agent management"""
        return render_template('agents.html')
    
    @app.route('/chat')
    def chat():
        """AI Chat"""
        return render_template('chat.html')
    
    # ==================== Authentication API ====================
    
    @app.route('/api/auth/login', methods=['POST'])
    @limiter.limit("5 per minute")
    def login():
        """User login"""
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        access_token, refresh_token = authenticate_user(username, password)
        
        if not access_token:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user = User.query.filter_by(username=username).first()
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        })
    
    @app.route('/api/auth/me', methods=['GET'])
    @jwt_required()
    def get_current_user_info():
        """Get current user info"""
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict())
    
    # ==================== Document API ====================
    
    @app.route('/api/documents', methods=['GET'])
    @jwt_required()
    def get_documents():
        """Get all documents"""
        documents = Document.query.order_by(Document.uploaded_at.desc()).all()
        return jsonify([doc.to_dict() for doc in documents])
    
    @app.route('/api/documents/upload', methods=['POST'])
    @jwt_required()
    @limiter.limit("10 per hour")
    def upload_document():
        """Upload and process document"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext.replace('.', '') not in app.config['ALLOWED_EXTENSIONS']:
            return jsonify({'error': 'File type not allowed'}), 400
        
        try:
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # Process document
            full_text, chunks, content_hash = document_processor.process_file(filepath)
            metadata = document_processor.extract_metadata(filepath)
            
            # Check if document already exists
            existing = Document.query.filter_by(content_hash=content_hash).first()
            if existing:
                os.remove(filepath)
                return jsonify({'error': 'Document already exists', 'document': existing.to_dict()}), 409
            
            # Create database entry
            user = get_current_user()
            doc = Document(
                filename=unique_filename,
                original_filename=filename,
                file_path=filepath,
                file_type=ext,
                file_size=os.path.getsize(filepath),
                content_hash=content_hash,
                status='processing',
                uploaded_by=user.id,
                metadata=metadata
            )
            db.session.add(doc)
            db.session.commit()
            
            # Add to vector store
            chunk_count = vector_store.add_document(doc.id, filename, chunks, metadata)
            
            # Update document status
            doc.status = 'processed'
            doc.processed_at = datetime.utcnow()
            doc.chunk_count = chunk_count
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Document processed successfully',
                'document': doc.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to process document: {str(e)}'}), 500
    
    @app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
    @jwt_required()
    @role_required('admin', 'analyst')
    def delete_document(doc_id):
        """Delete document"""
        doc = Document.query.get(doc_id)
        if not doc:
            return jsonify({'error': 'Document not found'}), 404
        
        try:
            # Delete from vector store
            vector_store.delete_document(doc_id)
            
            # Delete file
            if os.path.exists(doc.file_path):
                os.remove(doc.file_path)
            
            # Delete from database
            db.session.delete(doc)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Document deleted'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    # ==================== Logs API ====================
    
    @app.route('/api/logs', methods=['GET'])
    @jwt_required()
    def get_logs():
        """Get security logs"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        severity = request.args.get('severity')
        
        query = SecurityLog.query
        
        if severity:
            query = query.filter_by(severity=severity)
        
        logs = query.order_by(SecurityLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'total': logs.total,
            'pages': logs.pages,
            'current_page': page
        })
    
    @app.route('/api/logs/<int:log_id>/analyze', methods=['POST'])
    @jwt_required()
    @limiter.limit("20 per hour")
    def analyze_log(log_id):
        """Analyze log with AI"""
        log = SecurityLog.query.get(log_id)
        if not log:
            return jsonify({'error': 'Log not found'}), 404
        
        try:
            analysis = ai_chat.analyze_log(log.message, {'source': log.source_host})
            
            # Update log
            log.is_analyzed = True
            log.analysis_result = analysis
            db.session.commit()
            
            return jsonify({
                'success': True,
                'analysis': analysis
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== Agents API ====================
    
    @app.route('/api/agents', methods=['GET'])
    @jwt_required()
    def get_agents():
        """Get all agents"""
        agents = Agent.query.all()
        return jsonify([agent.to_dict() for agent in agents])
    
    @app.route('/api/agents', methods=['POST'])
    @jwt_required()
    @role_required('admin')
    def create_agent():
        """Create new agent"""
        data = request.json
        
        agent = Agent(
            name=data.get('name'),
            agent_type=data.get('type'),
            ip_address=data.get('ip'),
            hostname=data.get('hostname'),
            protocol=data.get('protocol', 'UDP'),
            port=data.get('port', 514)
        )
        
        db.session.add(agent)
        db.session.commit()
        
        return jsonify({'success': True, 'agent': agent.to_dict()})
    
    @app.route('/api/agents/<int:agent_id>', methods=['PUT'])
    @jwt_required()
    @role_required('admin')
    def update_agent(agent_id):
        """Update agent"""
        agent = Agent.query.get(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        data = request.json
        agent.name = data.get('name', agent.name)
        agent.agent_type = data.get('type', agent.agent_type)
        agent.ip_address = data.get('ip', agent.ip_address)
        agent.hostname = data.get('hostname', agent.hostname)
        agent.protocol = data.get('protocol', agent.protocol)
        agent.port = data.get('port', agent.port)
        
        db.session.commit()
        
        return jsonify({'success': True, 'agent': agent.to_dict()})
    
    # ==================== AI Chat API ====================
    
    @app.route('/api/chat', methods=['POST'])
    @jwt_required()
    @limiter.limit("30 per hour")
    def chat_with_ai():
        """Chat with AI"""
        data = request.json
        message = data.get('message')
        use_rag = data.get('use_rag', True)
        
        if not message:
            return jsonify({'error': 'Message required'}), 400
        
        try:
            user = get_current_user()
            result = ai_chat.chat(message, use_rag=use_rag)
            
            # Save to history
            chat_entry = ChatHistory(
                user_id=user.id,
                message=message,
                response=result['response'],
                model_used=result['model'],
                context_used={'sources': [s['metadata'] for s in result['sources']]}
            )
            db.session.add(chat_entry)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'response': result['response'],
                'sources': result['sources'],
                'model': result['model']
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/chat/history', methods=['GET'])
    @jwt_required()
    def get_chat_history():
        """Get chat history"""
        user = get_current_user()
        limit = request.args.get('limit', 20, type=int)
        
        history = ChatHistory.query.filter_by(user_id=user.id)\
            .order_by(ChatHistory.timestamp.desc())\
            .limit(limit).all()
        
        return jsonify([h.to_dict() for h in history])
    
    # ==================== Stats API ====================
    
    @app.route('/api/stats', methods=['GET'])
    @jwt_required()
    def get_stats():
        """Get system statistics"""
        stats = {
            'total_documents': Document.query.count(),
            'total_logs': SecurityLog.query.count(),
            'active_agents': Agent.query.filter_by(status='active').count(),
            'total_agents': Agent.query.count(),
            'critical_logs': SecurityLog.query.filter_by(severity='CRITICAL').count(),
            'unanalyzed_logs': SecurityLog.query.filter_by(is_analyzed=False).count(),
            'vector_store': vector_store.get_stats()
        }
        
        return jsonify(stats)
    
    # ==================== WebSocket Events ====================
    
    @socketio.on('connect')
    def handle_connect():
        """Client connected"""
        print("Client connected")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Client disconnected"""
        print("Client disconnected")
    
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app('development')
    
    print("=" * 60)
    print("🚀 Production Cybersecurity System Starting...")
    print("=" * 60)
    print(f"📊 Dashboard: http://localhost:5001")
    print(f"📚 Knowledge Base: http://localhost:5001/knowledge")
    print(f"📝 Logs: http://localhost:5001/logs")
    print(f"🤖 Agents: http://localhost:5001/agents")
    print(f"💬 AI Chat: http://localhost:5001/chat")
    print("=" * 60)
    print(f"🔐 Default Login: admin / admin123")
    print("=" * 60)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
