"""
Real Syslog Server
Receives logs from network devices via UDP/TCP
"""
import socket
import threading
import re
from datetime import datetime
from models import SecurityLog, Agent, db
from flask_socketio import SocketIO

class SyslogServer:
    def __init__(self, host='0.0.0.0', port=514, protocol='UDP', socketio=None):
        self.host = host
        self.port = port
        self.protocol = protocol.upper()
        self.socketio = socketio
        self.running = False
        self.socket = None
        
    def start(self):
        """Start syslog server"""
        if self.running:
            return
        
        self.running = True
        
        if self.protocol == 'UDP':
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind((self.host, self.port))
            print(f"✅ Syslog server started on {self.host}:{self.port} ({self.protocol})")
            
            if self.protocol == 'TCP':
                self.socket.listen(5)
                thread = threading.Thread(target=self._tcp_listener, daemon=True)
            else:
                thread = threading.Thread(target=self._udp_listener, daemon=True)
            
            thread.start()
        except Exception as e:
            print(f"❌ Failed to start syslog server: {e}")
            self.running = False
    
    def stop(self):
        """Stop syslog server"""
        self.running = False
        if self.socket:
            self.socket.close()
        print("🛑 Syslog server stopped")
    
    def _udp_listener(self):
        """Listen for UDP syslog messages"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(4096)
                message = data.decode('utf-8', errors='ignore')
                self._process_log(message, addr[0])
            except Exception as e:
                if self.running:
                    print(f"Error receiving UDP log: {e}")
    
    def _tcp_listener(self):
        """Listen for TCP syslog messages"""
        while self.running:
            try:
                conn, addr = self.socket.accept()
                thread = threading.Thread(
                    target=self._handle_tcp_connection,
                    args=(conn, addr),
                    daemon=True
                )
                thread.start()
            except Exception as e:
                if self.running:
                    print(f"Error accepting TCP connection: {e}")
    
    def _handle_tcp_connection(self, conn, addr):
        """Handle TCP connection"""
        try:
            while self.running:
                data = conn.recv(4096)
                if not data:
                    break
                message = data.decode('utf-8', errors='ignore')
                self._process_log(message, addr[0])
        except Exception as e:
            print(f"Error handling TCP connection: {e}")
        finally:
            conn.close()
    
    def _process_log(self, message, source_ip):
        """Process and store syslog message"""
        try:
            # Parse syslog message (RFC 3164 / RFC 5424)
            parsed = self._parse_syslog(message)
            
            # Find or create agent
            agent = Agent.query.filter_by(ip_address=source_ip).first()
            if not agent:
                agent = Agent(
                    name=f"Agent-{source_ip}",
                    ip_address=source_ip,
                    status='active',
                    last_seen=datetime.utcnow()
                )
                db.session.add(agent)
            else:
                agent.last_seen = datetime.utcnow()
                agent.status = 'active'
            
            # Create log entry
            log = SecurityLog(
                timestamp=parsed.get('timestamp', datetime.utcnow()),
                source_ip=source_ip,
                source_host=parsed.get('hostname'),
                facility=parsed.get('facility'),
                severity=parsed.get('severity', 'INFO'),
                message=parsed.get('message', message),
                raw_log=message,
                agent_id=agent.id,
                threat_level=self._assess_threat_level(parsed.get('message', ''))
            )
            
            db.session.add(log)
            db.session.commit()
            
            # Emit to dashboard via WebSocket
            if self.socketio:
                self.socketio.emit('new_log', log.to_dict())
            
            print(f"📝 Log received from {source_ip}: {parsed.get('message', message)[:100]}")
            
        except Exception as e:
            print(f"Error processing log: {e}")
            db.session.rollback()
    
    def _parse_syslog(self, message):
        """Parse syslog message"""
        result = {
            'timestamp': datetime.utcnow(),
            'hostname': None,
            'facility': None,
            'severity': 'INFO',
            'message': message
        }
        
        # RFC 3164 format: <PRI>TIMESTAMP HOSTNAME MESSAGE
        pri_match = re.match(r'^<(\d+)>', message)
        if pri_match:
            pri = int(pri_match.group(1))
            result['facility'] = pri >> 3
            severity_num = pri & 0x07
            
            # Map severity number to string
            severity_map = {
                0: 'CRITICAL', 1: 'CRITICAL', 2: 'CRITICAL',
                3: 'ERROR', 4: 'WARNING', 5: 'WARNING',
                6: 'INFO', 7: 'INFO'
            }
            result['severity'] = severity_map.get(severity_num, 'INFO')
            
            # Remove PRI from message
            message = message[pri_match.end():]
        
        # Extract hostname
        parts = message.split(None, 2)
        if len(parts) >= 2:
            result['hostname'] = parts[0]
            result['message'] = parts[1] if len(parts) == 2 else parts[2]
        
        return result
    
    def _assess_threat_level(self, message):
        """Assess threat level based on message content"""
        message_lower = message.lower()
        
        critical_keywords = ['attack', 'breach', 'malware', 'ransomware', 'exploit']
        high_keywords = ['failed login', 'unauthorized', 'denied', 'blocked', 'suspicious']
        medium_keywords = ['warning', 'error', 'timeout', 'retry']
        
        for keyword in critical_keywords:
            if keyword in message_lower:
                return 'critical'
        
        for keyword in high_keywords:
            if keyword in message_lower:
                return 'high'
        
        for keyword in medium_keywords:
            if keyword in message_lower:
                return 'medium'
        
        return 'low'
