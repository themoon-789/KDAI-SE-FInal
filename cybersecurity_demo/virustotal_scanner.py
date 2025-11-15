"""
VirusTotal Scanner Module
ตรวจสอบไฟล์และ URL ด้วย VirusTotal API
"""

import os
import requests
import hashlib
import time
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class VirusTotalScanner:
    def __init__(self):
        self.api_key = os.getenv('VIRUSTOTAL_API_KEY')
        self.base_url = 'https://www.virustotal.com/api/v3'
        
        if not self.api_key:
            raise ValueError("VIRUSTOTAL_API_KEY not found in environment variables")
    
    def scan_url(self, url: str) -> Dict:
        """
        สแกน URL ด้วย VirusTotal
        
        Args:
            url: URL ที่ต้องการตรวจสอบ
        
        Returns:
            ผลการสแกน
        """
        try:
            # ส่ง URL ไปสแกน
            headers = {
                "x-apikey": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            response = requests.post(
                f"{self.base_url}/urls",
                headers=headers,
                data={"url": url},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_id = result['data']['id']
                
                # รอผลการวิเคราะห์
                time.sleep(2)
                return self.get_url_report(analysis_id)
            else:
                return {
                    "error": f"Failed to scan URL: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_url_report(self, analysis_id: str) -> Dict:
        """
        ดึงรายงานการสแกน URL
        """
        try:
            headers = {"x-apikey": self.api_key}
            
            response = requests.get(
                f"{self.base_url}/analyses/{analysis_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()['data']
                stats = data['attributes']['stats']
                
                return {
                    "status": "completed",
                    "malicious": stats.get('malicious', 0),
                    "suspicious": stats.get('suspicious', 0),
                    "harmless": stats.get('harmless', 0),
                    "undetected": stats.get('undetected', 0),
                    "total_scans": sum(stats.values()),
                    "threat_level": self._calculate_threat_level(stats),
                    "details": data
                }
            else:
                return {"error": f"Failed to get report: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def scan_file_hash(self, file_hash: str) -> Dict:
        """
        ตรวจสอบไฟล์จาก hash (MD5, SHA1, SHA256)
        
        Args:
            file_hash: Hash ของไฟล์
        
        Returns:
            ผลการตรวจสอบ
        """
        try:
            headers = {"x-apikey": self.api_key}
            
            response = requests.get(
                f"{self.base_url}/files/{file_hash}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()['data']
                stats = data['attributes']['last_analysis_stats']
                
                return {
                    "status": "found",
                    "file_name": data['attributes'].get('meaningful_name', 'Unknown'),
                    "file_type": data['attributes'].get('type_description', 'Unknown'),
                    "size": data['attributes'].get('size', 0),
                    "malicious": stats.get('malicious', 0),
                    "suspicious": stats.get('suspicious', 0),
                    "harmless": stats.get('harmless', 0),
                    "undetected": stats.get('undetected', 0),
                    "total_scans": sum(stats.values()),
                    "threat_level": self._calculate_threat_level(stats),
                    "sha256": data['attributes'].get('sha256', ''),
                    "md5": data['attributes'].get('md5', ''),
                    "details": data
                }
            elif response.status_code == 404:
                return {
                    "status": "not_found",
                    "message": "File hash not found in VirusTotal database"
                }
            else:
                return {"error": f"Failed to check hash: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_ip_report(self, ip_address: str) -> Dict:
        """
        ตรวจสอบ IP address
        
        Args:
            ip_address: IP address ที่ต้องการตรวจสอบ
        
        Returns:
            ผลการตรวจสอบ
        """
        try:
            headers = {"x-apikey": self.api_key}
            
            response = requests.get(
                f"{self.base_url}/ip_addresses/{ip_address}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()['data']
                stats = data['attributes'].get('last_analysis_stats', {})
                
                return {
                    "status": "found",
                    "ip": ip_address,
                    "country": data['attributes'].get('country', 'Unknown'),
                    "as_owner": data['attributes'].get('as_owner', 'Unknown'),
                    "malicious": stats.get('malicious', 0),
                    "suspicious": stats.get('suspicious', 0),
                    "harmless": stats.get('harmless', 0),
                    "undetected": stats.get('undetected', 0),
                    "threat_level": self._calculate_threat_level(stats),
                    "details": data
                }
            else:
                return {"error": f"Failed to check IP: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_threat_level(self, stats: Dict) -> str:
        """
        คำนวณระดับความเสี่ยง
        """
        malicious = stats.get('malicious', 0)
        suspicious = stats.get('suspicious', 0)
        
        if malicious > 5:
            return "Critical"
        elif malicious > 0 or suspicious > 10:
            return "High"
        elif suspicious > 0:
            return "Medium"
        else:
            return "Safe"
    
    def calculate_file_hash(self, file_path: str, hash_type: str = 'sha256') -> Optional[str]:
        """
        คำนวณ hash ของไฟล์
        
        Args:
            file_path: path ของไฟล์
            hash_type: ประเภท hash (md5, sha1, sha256)
        
        Returns:
            hash string
        """
        try:
            hash_func = getattr(hashlib, hash_type)()
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            
            return hash_func.hexdigest()
        except Exception as e:
            print(f"Error calculating hash: {e}")
            return None
