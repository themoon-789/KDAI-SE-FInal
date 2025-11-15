"""
Graylog Client - ดึงและวิเคราะห์ logs จาก Graylog
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class GraylogClient:
    def __init__(self, 
                 host="10.10.89.6",
                 port=9000,
                 api_token=None,
                 stream_name="FortiGate Syslog"):
        """
        เชื่อมต่อกับ Graylog Server
        
        Args:
            host: Graylog server IP
            port: Graylog API port
            api_token: API token สำหรับ authentication
            stream_name: ชื่อ stream ที่ต้องการดึงข้อมูล
        """
        self.base_url = f"http://{host}:{port}/api"
        self.api_token = api_token
        self.stream_name = stream_name
        self.auth = (api_token, 'token')  # Graylog ใช้ Basic Auth กับ token
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        print(f"🔗 Graylog Client initialized")
        print(f"   Server: {host}:{port}")
        print(f"   Stream: {stream_name}")
    
    def test_connection(self) -> bool:
        """ทดสอบการเชื่อมต่อกับ Graylog"""
        try:
            response = requests.get(
                f"{self.base_url}/system",
                auth=self.auth,
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                print("✅ Connected to Graylog successfully")
                return True
            else:
                print(f"⚠️  Connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return False
    
    def get_streams(self) -> List[Dict]:
        """ดึงรายการ streams ทั้งหมด"""
        try:
            response = requests.get(
                f"{self.base_url}/streams",
                auth=self.auth,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                streams = data.get('streams', [])
                print(f"📊 Found {len(streams)} streams")
                return streams
            else:
                print(f"⚠️  Failed to get streams: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting streams: {str(e)}")
            return []
    
    def find_stream_id(self) -> Optional[str]:
        """หา stream ID จากชื่อ stream"""
        streams = self.get_streams()
        
        for stream in streams:
            if stream.get('title') == self.stream_name:
                stream_id = stream.get('id')
                print(f"✅ Found stream: {self.stream_name} (ID: {stream_id})")
                return stream_id
        
        print(f"⚠️  Stream '{self.stream_name}' not found")
        return None
    
    def search_logs(self, 
                   query: str = "*",
                   time_range: int = 300,
                   limit: int = 100,
                   stream_id: Optional[str] = None) -> List[Dict]:
        """
        ค้นหา logs จาก Graylog
        
        Args:
            query: Query string (Lucene syntax)
            time_range: ช่วงเวลาย้อนหลัง (วินาที)
            limit: จำนวน logs สูงสุด
            stream_id: Stream ID (ถ้าไม่ระบุจะหาจากชื่อ)
        
        Returns:
            List ของ log messages
        """
        if not stream_id:
            stream_id = self.find_stream_id()
            if not stream_id:
                return []
        
        try:
            # สร้าง search query
            search_params = {
                'query': query,
                'range': time_range,
                'limit': limit,
                'sort': 'timestamp:desc',
                'filter': f'streams:{stream_id}'
            }
            
            response = requests.get(
                f"{self.base_url}/search/universal/relative",
                auth=self.auth,
                headers=self.headers,
                params=search_params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get('messages', [])
                print(f"📝 Retrieved {len(messages)} logs")
                return messages
            else:
                print(f"⚠️  Search failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error searching logs: {str(e)}")
            return []
    
    def get_recent_logs(self, minutes: int = 5, limit: int = 50) -> List[Dict]:
        """
        ดึง logs ล่าสุด
        
        Args:
            minutes: จำนวนนาทีย้อนหลัง
            limit: จำนวน logs สูงสุด
        """
        time_range = minutes * 60  # แปลงเป็นวินาที
        return self.search_logs(query="*", time_range=time_range, limit=limit)
    
    def search_security_events(self, 
                              event_type: str = "attack",
                              time_range: int = 3600,
                              limit: int = 100) -> List[Dict]:
        """
        ค้นหา security events
        
        Args:
            event_type: ประเภทของ event (attack, intrusion, malware, etc.)
            time_range: ช่วงเวลาย้อนหลัง (วินาที)
            limit: จำนวน logs สูงสุด
        """
        query = f"*{event_type}* OR *threat* OR *malware* OR *intrusion*"
        return self.search_logs(query=query, time_range=time_range, limit=limit)
    
    def get_fortigate_logs(self, 
                          log_type: Optional[str] = None,
                          time_range: int = 3600,
                          limit: int = 100) -> List[Dict]:
        """
        ดึง FortiGate logs
        
        Args:
            log_type: ประเภท log (traffic, utm, event, etc.)
            time_range: ช่วงเวลาย้อนหลัง (วินาที)
            limit: จำนวน logs สูงสุด
        """
        if log_type:
            query = f"type:{log_type}"
        else:
            query = "*"
        
        return self.search_logs(query=query, time_range=time_range, limit=limit)
    
    def analyze_logs(self, logs: List[Dict]) -> Dict:
        """
        วิเคราะห์ logs และสรุปข้อมูล
        
        Args:
            logs: List ของ log messages
        
        Returns:
            Dict ที่มีข้อมูลสถิติ
        """
        if not logs:
            return {
                'total': 0,
                'severity_counts': {},
                'top_sources': [],
                'top_destinations': [],
                'event_types': {}
            }
        
        severity_counts = {}
        sources = {}
        destinations = {}
        event_types = {}
        
        for log in logs:
            message = log.get('message', {})
            
            # นับ severity
            severity = message.get('level', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # นับ source IPs
            src_ip = message.get('srcip', message.get('source', 'unknown'))
            sources[src_ip] = sources.get(src_ip, 0) + 1
            
            # นับ destination IPs
            dst_ip = message.get('dstip', message.get('destination', 'unknown'))
            destinations[dst_ip] = destinations.get(dst_ip, 0) + 1
            
            # นับ event types
            event_type = message.get('type', message.get('subtype', 'unknown'))
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # เรียง top sources และ destinations
        top_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10]
        top_destinations = sorted(destinations.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total': len(logs),
            'severity_counts': severity_counts,
            'top_sources': top_sources,
            'top_destinations': top_destinations,
            'event_types': event_types
        }
    
    def format_log_for_display(self, log: Dict) -> str:
        """
        จัดรูปแบบ log สำหรับแสดงผล
        
        Args:
            log: Log message
        
        Returns:
            String ที่จัดรูปแบบแล้ว
        """
        message = log.get('message', {})
        timestamp = message.get('timestamp', 'N/A')
        level = message.get('level', 'INFO')
        source = message.get('source', 'N/A')
        msg = message.get('message', message.get('full_message', 'N/A'))
        
        return f"[{timestamp}] [{level}] {source}: {msg}"
    
    def prepare_logs_for_llm(self, logs: List[Dict], max_logs: int = 50) -> str:
        """
        จัดรูปแบบ logs สำหรับส่งให้ LLM วิเคราะห์
        
        Args:
            logs: List ของ log messages
            max_logs: จำนวน logs สูงสุดที่จะส่งให้ LLM
        
        Returns:
            String ที่จัดรูปแบบแล้วพร้อมส่งให้ LLM
        """
        if not logs:
            return "No logs available for analysis."
        
        # จำกัดจำนวน logs
        logs_to_analyze = logs[:max_logs]
        
        # สร้าง summary header
        analysis = self.analyze_logs(logs)
        header = f"""=== Graylog Logs Summary ===
Total Logs: {analysis['total']}
Severity Distribution: {analysis['severity_counts']}
Event Types: {analysis['event_types']}

=== Detailed Logs ({len(logs_to_analyze)} most recent) ===
"""
        
        # จัดรูปแบบแต่ละ log
        formatted_logs = []
        for i, log in enumerate(logs_to_analyze, 1):
            message = log.get('message', {})
            
            # ดึงข้อมูลสำคัญ
            timestamp = message.get('timestamp', 'N/A')
            level = message.get('level', 'INFO')
            source_ip = message.get('srcip', message.get('source', 'N/A'))
            dest_ip = message.get('dstip', message.get('destination', 'N/A'))
            action = message.get('action', 'N/A')
            msg_text = message.get('message', message.get('full_message', 'N/A'))
            
            log_entry = f"""
Log #{i}:
  Time: {timestamp}
  Severity: {level}
  Source IP: {source_ip}
  Destination IP: {dest_ip}
  Action: {action}
  Message: {msg_text}
"""
            formatted_logs.append(log_entry)
        
        return header + "\n".join(formatted_logs)


def test_graylog():
    """ทดสอบการเชื่อมต่อ Graylog"""
    print("=" * 60)
    print("  Graylog Client Test")
    print("=" * 60)
    
    # สร้าง client
    client = GraylogClient()
    
    # ทดสอบการเชื่อมต่อ
    print("\n1. Testing connection...")
    if not client.test_connection():
        print("❌ Cannot connect to Graylog")
        return
    
    # ดึงรายการ streams
    print("\n2. Getting streams...")
    streams = client.get_streams()
    for stream in streams[:5]:
        print(f"   - {stream.get('title')} (ID: {stream.get('id')})")
    
    # หา stream ID
    print("\n3. Finding target stream...")
    stream_id = client.find_stream_id()
    
    if stream_id:
        # ดึง logs ล่าสุด
        print("\n4. Getting recent logs...")
        logs = client.get_recent_logs(minutes=5, limit=10)
        
        if logs:
            print(f"\n📝 Recent logs ({len(logs)}):")
            for i, log in enumerate(logs[:5], 1):
                print(f"\n{i}. {client.format_log_for_display(log)}")
            
            # วิเคราะห์ logs
            print("\n5. Analyzing logs...")
            analysis = client.analyze_logs(logs)
            print(f"\n📊 Analysis:")
            print(f"   Total logs: {analysis['total']}")
            print(f"   Severity: {analysis['severity_counts']}")
            print(f"   Event types: {analysis['event_types']}")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")


if __name__ == "__main__":
    test_graylog()
