"""
Test Syslog Server
Sends test logs to the syslog server
"""
import socket
import time
from datetime import datetime

def send_syslog(host='localhost', port=514, message='Test log message'):
    """Send a syslog message via UDP"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # RFC 3164 format: <PRI>TIMESTAMP HOSTNAME MESSAGE
    # PRI = Facility * 8 + Severity
    # Facility 16 (local0), Severity 6 (info) = 134
    timestamp = datetime.now().strftime('%b %d %H:%M:%S')
    hostname = socket.gethostname()
    
    syslog_message = f"<134>{timestamp} {hostname} {message}"
    
    sock.sendto(syslog_message.encode(), (host, port))
    sock.close()
    
    print(f"✅ Sent: {message}")

if __name__ == '__main__':
    print("🧪 Testing Syslog Server...")
    print("Sending test logs to localhost:514")
    print("-" * 60)
    
    # Send various test logs
    test_logs = [
        "INFO: System started successfully",
        "WARNING: High CPU usage detected",
        "ERROR: Failed login attempt from 192.168.1.100",
        "CRITICAL: Firewall blocked suspicious traffic from 10.0.0.50",
        "INFO: User admin logged in successfully",
        "WARNING: Port scan detected from 172.16.0.25",
        "ERROR: Malware signature detected in file transfer",
        "INFO: Backup completed successfully"
    ]
    
    for log in test_logs:
        send_syslog(message=log)
        time.sleep(1)
    
    print("-" * 60)
    print("✅ Test completed! Check the dashboard for logs.")
