from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import os
import json
from datetime import datetime
import threading
import time
from ai_chat import AIChat
from simple_vector_store import SimpleVectorStore
from ai_chat_rag import AIChatRAG
from virustotal_scanner import VirusTotalScanner
from unified_vector_store import UnifiedVectorStore
from ai_chat_unified import UnifiedAIChat
from graylog_client import GraylogClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cybersecurity-demo-2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
socketio = SocketIO(app, cors_allowed_origins="*")

# สร้างโฟลเดอร์สำหรับเก็บไฟล์
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# จำลองข้อมูลระบบ
system_data = {
    'documents': [],
    'logs': [],
    'agents': [
        {'id': 1, 'name': 'Firewall-Agent-01', 'status': 'active', 'ip': '192.168.1.10'},
        {'id': 2, 'name': 'Windows-Server-01', 'status': 'active', 'ip': '192.168.1.20'},
        {'id': 3, 'name': 'Router-Agent-01', 'status': 'inactive', 'ip': '192.168.1.1'}
    ],
    'stats': {
        'total_documents': 0,
        'total_logs': 0,
        'active_agents': 2,
        'system_health': 95
    }
}

# ฟังก์ชันจำลองการรับ Log แบบ Real-time
def simulate_log_collection():
    """จำลองการรับ Syslog แบบ Real-time"""
    log_templates = [
        "Firewall blocked connection from {ip}",
        "Successful login from user {user}",
        "Failed authentication attempt from {ip}",
        "Port scan detected from {ip}",
        "Malware signature detected in file transfer"
    ]
    
    while True:
        time.sleep(5)  # รับ log ทุก 5 วินาที
        
        import random
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': random.choice(['Firewall-01', 'Windows-Server-01', 'Router-01']),
            'severity': random.choice(['INFO', 'WARNING', 'CRITICAL']),
            'message': random.choice(log_templates).format(
                ip=f"192.168.1.{random.randint(100, 200)}",
                user=f"user{random.randint(1, 10)}"
            )
        }
        
        system_data['logs'].append(log_entry)
        system_data['stats']['total_logs'] = len(system_data['logs'])
        
        # ส่งข้อมูลไปยัง Dashboard แบบ Real-time
        socketio.emit('new_log', log_entry)
        socketio.emit('stats_update', system_data['stats'])

# เริ่ม thread สำหรับจำลอง log collection
log_thread = threading.Thread(target=simulate_log_collection, daemon=True)
log_thread.start()

# สร้าง Simple Vector Store (ไม่ต้องใช้ ChromaDB)
try:
    print("🔧 Initializing Simple Vector Store...")
    vector_store = SimpleVectorStore(persist_file="./vector_data.json")
    print("✅ Simple Vector Store initialized successfully")
except Exception as e:
    print(f"⚠️  Vector Store initialization failed: {e}")
    vector_store = None

# สร้าง AI Chat instance (แบบเดิม - ไม่มี RAG)
try:
    ai_chat = AIChat()
    print("✅ AI Chat (basic) initialized successfully")
except Exception as e:
    print(f"⚠️  AI Chat initialization failed: {e}")
    ai_chat = None

# สร้าง AI Chat with RAG
try:
    ai_chat_rag = AIChatRAG(vector_store=vector_store)
    print("✅ AI Chat with RAG initialized successfully")
except Exception as e:
    print(f"⚠️  AI Chat RAG initialization failed: {e}")
    ai_chat_rag = None

# สร้าง Unified AI Chat (รวม Exploit-DB Papers)
try:
    ai_chat_unified = UnifiedAIChat()
    print("✅ Unified AI Chat (with Exploit-DB) initialized successfully")
except Exception as e:
    print(f"⚠️  Unified AI Chat initialization failed: {e}")
    ai_chat_unified = None

# สร้าง Graylog Client
try:
    graylog_client = GraylogClient(
        host=os.getenv('GRAYLOG_HOST', '10.10.89.6'),
        port=int(os.getenv('GRAYLOG_PORT', 9000)),
        api_token=os.getenv('GRAYLOG_API_TOKEN'),
        stream_name=os.getenv('GRAYLOG_STREAM_NAME', 'FortiGate Syslog')
    )
    print("✅ Graylog Client initialized successfully")
except Exception as e:
    print(f"⚠️  Graylog Client initialization failed: {e}")
    graylog_client = None

@app.route('/')
def index():
    """หน้าหลัก - Dashboard"""
    return render_template('dashboard.html')

@app.route('/knowledge')
def knowledge():
    """หน้าจัดการ Knowledge Base"""
    return render_template('knowledge.html')

@app.route('/logs')
def logs():
    """หน้าจัดการ Logs"""
    return render_template('logs.html')

@app.route('/agents')
def agents():
    """หน้าจัดการ Agents"""
    return render_template('agents.html')

@app.route('/chat')
def chat():
    """หน้า AI Chat"""
    return render_template('chat.html')

# API Endpoints
@app.route('/api/upload-document', methods=['POST'])
def upload_document():
    """UC-ADM-01: นำเข้าเอกสาร พร้อม Vector Embedding จริง"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # บันทึกไฟล์
    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # สร้าง Vector Embeddings จริง
    embedding_result = None
    if vector_store:
        try:
            print(f"📄 Processing document: {filename}")
            embedding_result = vector_store.add_document(
                filepath,
                metadata={'upload_time': datetime.now().isoformat()}
            )
            print(f"✅ Document processed: {embedding_result}")
        except Exception as e:
            print(f"⚠️  Embedding failed: {e}")
            embedding_result = {'success': False, 'error': str(e)}
    
    # บันทึกข้อมูลเอกสาร
    doc_entry = {
        'id': len(system_data['documents']) + 1,
        'filename': filename,
        'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'processed' if embedding_result and embedding_result.get('success') else 'error',
        'size': os.path.getsize(filepath),
        'chunks': embedding_result.get('chunks', 0) if embedding_result else 0,
        'embedding_status': 'success' if embedding_result and embedding_result.get('success') else 'failed'
    }
    
    system_data['documents'].append(doc_entry)
    system_data['stats']['total_documents'] = len(system_data['documents'])
    
    return jsonify({
        'success': True,
        'message': 'เอกสารถูกนำเข้าและสร้าง Vector Embeddings เรียบร้อย' if doc_entry['embedding_status'] == 'success' else 'เอกสารถูกนำเข้าแต่ไม่สามารถสร้าง Embeddings ได้',
        'document': doc_entry,
        'embedding_result': embedding_result
    })

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """ดึงรายการเอกสารทั้งหมด"""
    return jsonify(system_data['documents'])

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """ดึงข้อมูล Logs"""
    limit = request.args.get('limit', 50, type=int)
    source = request.args.get('source', 'local')  # 'local' หรือ 'graylog'
    
    if source == 'graylog' and graylog_client:
        try:
            minutes = request.args.get('minutes', 5, type=int)
            logs = graylog_client.get_recent_logs(minutes=minutes, limit=limit)
            
            # แปลงรูปแบบให้เหมาะกับ UI
            formatted_logs = []
            for log in logs:
                msg = log.get('message', {})
                formatted_logs.append({
                    'timestamp': msg.get('timestamp', datetime.now().isoformat()),
                    'level': msg.get('level', 'INFO'),
                    'source': msg.get('source', 'Graylog'),
                    'message': msg.get('message', msg.get('full_message', 'N/A')),
                    'ip': msg.get('srcip', msg.get('source_ip', 'N/A'))
                })
            
            return jsonify(formatted_logs)
        except Exception as e:
            return jsonify({'error': f'Failed to get Graylog logs: {str(e)}'}), 500
    
    # ส่ง logs จาก local
    return jsonify(system_data['logs'][-limit:])

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """UC-ADM-02: ดึงข้อมูล Agents"""
    return jsonify(system_data['agents'])

@app.route('/api/agents/<int:agent_id>/configure', methods=['POST'])
def configure_agent(agent_id):
    """UC-ADM-02: ตั้งค่า Agent"""
    data = request.json
    
    agent = next((a for a in system_data['agents'] if a['id'] == agent_id), None)
    if not agent:
        return jsonify({'error': 'Agent not found'}), 404
    
    agent['protocol'] = data.get('protocol', 'UDP')
    agent['port'] = data.get('port', 514)
    agent['status'] = 'active'
    
    return jsonify({
        'success': True,
        'message': f'Agent {agent["name"]} ถูกตั้งค่าเรียบร้อย',
        'agent': agent
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """UC-ADM-03: ดึงสถิติระบบสำหรับ Dashboard"""
    return jsonify(system_data['stats'])

@app.route('/api/graylog/analyze', methods=['GET'])
def analyze_graylog_logs():
    """วิเคราะห์ logs จาก Graylog"""
    if not graylog_client:
        return jsonify({'error': 'Graylog client not available'}), 503
    
    try:
        minutes = request.args.get('minutes', 60, type=int)
        logs = graylog_client.get_recent_logs(minutes=minutes, limit=1000)
        
        if not logs:
            return jsonify({
                'success': False,
                'message': 'No logs found'
            })
        
        # วิเคราะห์ logs
        analysis = graylog_client.analyze_logs(logs)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'time_range_minutes': minutes
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to analyze logs: {str(e)}'}), 500

@app.route('/api/graylog/security-events', methods=['GET'])
def get_security_events():
    """ดึง security events จาก Graylog"""
    if not graylog_client:
        return jsonify({'error': 'Graylog client not available'}), 503
    
    try:
        event_type = request.args.get('type', 'attack')
        hours = request.args.get('hours', 1, type=int)
        time_range = hours * 3600
        
        events = graylog_client.search_security_events(
            event_type=event_type,
            time_range=time_range,
            limit=100
        )
        
        # จัดรูปแบบ events
        formatted_events = []
        for event in events:
            msg = event.get('message', {})
            formatted_events.append({
                'timestamp': msg.get('timestamp', datetime.now().isoformat()),
                'level': msg.get('level', 'WARNING'),
                'source': msg.get('source', 'Unknown'),
                'message': msg.get('message', msg.get('full_message', 'N/A')),
                'srcip': msg.get('srcip', 'N/A'),
                'dstip': msg.get('dstip', 'N/A')
            })
        
        return jsonify({
            'success': True,
            'events': formatted_events,
            'count': len(formatted_events)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get security events: {str(e)}'}), 500

@app.route('/api/graylog/ai-analyze', methods=['GET'])
def ai_analyze_graylog_logs():
    """วิเคราะห์ logs จาก Graylog ด้วย AI/LLM"""
    if not graylog_client:
        return jsonify({'error': 'Graylog client not available'}), 503
    
    if not ai_chat_unified:
        return jsonify({'error': 'AI Chat not available'}), 503
    
    try:
        minutes = request.args.get('minutes', 30, type=int)
        max_logs = request.args.get('max_logs', 50, type=int)
        
        # ดึง logs จาก Graylog
        print(f"🔍 Fetching logs from Graylog (last {minutes} minutes)...")
        logs = graylog_client.get_recent_logs(minutes=minutes, limit=max_logs)
        
        if not logs:
            return jsonify({
                'success': False,
                'message': 'No logs found in the specified time range'
            })
        
        # จัดรูปแบบ logs สำหรับ LLM
        logs_text = graylog_client.prepare_logs_for_llm(logs, max_logs=max_logs)
        
        # ส่งให้ AI วิเคราะห์
        result = ai_chat_unified.analyze_graylog_logs(logs_text)
        
        if result['success']:
            return jsonify({
                'success': True,
                'analysis': result['analysis'],
                'logs_count': len(logs),
                'logs_analyzed': result['logs_analyzed'],
                'time_range_minutes': minutes,
                'model': result['model']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }), 500
        
    except Exception as e:
        return jsonify({'error': f'Failed to analyze logs with AI: {str(e)}'}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """UC-ADM-04: ถามตอบกับ AI พร้อม RAG"""
    data = request.json
    user_message = data.get('message', '')
    use_rag = data.get('use_rag', True)
    use_exploitdb = data.get('use_exploitdb', False)  # ใช้ Exploit-DB หรือไม่
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    try:
        print(f"💬 User message: {user_message}")
        print(f"🔍 RAG enabled: {use_rag}")
        print(f"📚 Exploit-DB enabled: {use_exploitdb}")
        
        # ถ้าเลือกใช้ Exploit-DB
        if use_exploitdb and ai_chat_unified:
            result = ai_chat_unified.chat(user_message, n_results=5)
            return jsonify({
                'success': True,
                'response': result['response'],
                'model': result['model'],
                'context_used': True,
                'sources': result['sources'],
                'rag_enabled': True,
                'exploitdb_enabled': True
            })
        
        # ใช้ RAG ปกติ
        elif ai_chat_rag:
            result = ai_chat_rag.chat_with_rag(user_message, use_rag=use_rag)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'response': result['response'],
                    'model': result['model'],
                    'context_used': result['context_used'],
                    'sources': result['sources'],
                    'rag_enabled': use_rag,
                    'exploitdb_enabled': False
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'context_used': result.get('context_used', False),
                    'sources': result.get('sources', [])
                }), 500
        else:
            return jsonify({
                'error': 'AI Chat is not available. Please check API key configuration.'
            }), 503
            
    except Exception as e:
        return jsonify({
            'error': f'Failed to get AI response: {str(e)}'
        }), 500

@app.route('/api/analyze-threat', methods=['POST'])
def analyze_threat():
    """วิเคราะห์ภัยคุกคามด้วย AI"""
    if not ai_chat:
        return jsonify({'error': 'AI Chat is not available'}), 503
    
    data = request.json
    threat_data = data.get('threat_data', {})
    
    try:
        analysis = ai_chat.analyze_threat(threat_data)
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-info', methods=['GET'])
def get_ai_info():
    """ดึงข้อมูล AI Model และ Vector Store"""
    if not ai_chat_rag:
        return jsonify({
            'status': 'inactive',
            'message': 'AI Chat is not configured'
        })
    
    return jsonify(ai_chat_rag.get_model_info())

@app.route('/api/vector-search', methods=['POST'])
def vector_search():
    """ค้นหาเอกสารด้วย Semantic Search"""
    if not vector_store:
        return jsonify({'error': 'Vector Store is not available'}), 503
    
    data = request.json
    query = data.get('query', '')
    n_results = data.get('n_results', 5)
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        results = vector_store.search(query, n_results=n_results)
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vector-stats', methods=['GET'])
def get_vector_stats():
    """ดึงสถิติ Vector Store"""
    if not vector_store:
        return jsonify({'error': 'Vector Store is not available'}), 503
    
    try:
        stats = vector_store.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# VirusTotal Scanner Routes
try:
    vt_scanner = VirusTotalScanner()
    print("✅ VirusTotal Scanner initialized")
except Exception as e:
    vt_scanner = None
    print(f"⚠️ VirusTotal Scanner not available: {e}")

@app.route('/virustotal')
def virustotal_page():
    """หน้า VirusTotal Scanner"""
    return render_template('virustotal.html')

@app.route('/api/vt/scan-url', methods=['POST'])
def scan_url():
    """สแกน URL ด้วย VirusTotal"""
    if not vt_scanner:
        return jsonify({'error': 'VirusTotal Scanner not configured'}), 503
    
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    result = vt_scanner.scan_url(url)
    return jsonify(result)

@app.route('/api/vt/scan-hash', methods=['POST'])
def scan_hash():
    """ตรวจสอบ file hash"""
    if not vt_scanner:
        return jsonify({'error': 'VirusTotal Scanner not configured'}), 503
    
    data = request.get_json()
    file_hash = data.get('hash')
    
    if not file_hash:
        return jsonify({'error': 'Hash is required'}), 400
    
    result = vt_scanner.scan_file_hash(file_hash)
    return jsonify(result)

@app.route('/api/vt/scan-ip', methods=['POST'])
def scan_ip():
    """ตรวจสอบ IP address"""
    if not vt_scanner:
        return jsonify({'error': 'VirusTotal Scanner not configured'}), 503
    
    data = request.get_json()
    ip_address = data.get('ip')
    
    if not ip_address:
        return jsonify({'error': 'IP address is required'}), 400
    
    result = vt_scanner.get_ip_report(ip_address)
    return jsonify(result)

@socketio.on('connect')
def handle_connect():
    """เมื่อ client เชื่อมต่อ WebSocket"""
    emit('stats_update', system_data['stats'])

if __name__ == '__main__':
    print("🚀 Starting Advance Agent for Cybersecurity Demo...")
    print("📊 Dashboard: http://localhost:5001")
    print("📚 Knowledge Base: http://localhost:5001/knowledge")
    print("📝 Logs: http://localhost:5001/logs")
    print("🤖 Agents: http://localhost:5001/agents")
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
