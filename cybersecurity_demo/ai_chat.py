"""
AI Chat Module using OpenRouter API
Supports free LLM models like Llama
"""

import os
import requests
import time
from typing import List, Dict
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv()

class AIChat:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.model = os.getenv('OPENROUTER_MODEL', 'meta-llama/llama-3.2-3b-instruct:free')
        self.api_url = 'https://openrouter.ai/api/v1/chat/completions'
        self.demo_mode = os.getenv('DEMO_MODE', 'false').lower() == 'true'
        
        if not self.api_key and not self.demo_mode:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    def chat(self, user_message: str, context: str = None, max_retries: int = 3) -> str:
        """
        ส่งข้อความไปยัง LLM และรับคำตอบ (พร้อม retry logic สำหรับ rate limits)
        
        Args:
            user_message: คำถามจากผู้ใช้
            context: ข้อมูลจาก Knowledge Base (ถ้ามี)
            max_retries: จำนวนครั้งที่จะลองใหม่เมื่อเจอ rate limit
        
        Returns:
            คำตอบจาก LLM
        """
        
        # Demo mode - ส่งคำตอบจำลอง
        if self.demo_mode:
            return self._get_demo_response(user_message)
        
        # สร้าง system prompt
        system_prompt = """You are a cybersecurity expert assistant. 
Your role is to help analyze security threats, provide recommendations, and answer questions about cybersecurity.
Be concise, accurate, and helpful. If you don't know something, say so."""

        if context:
            system_prompt += f"\n\nRelevant information from knowledge base:\n{context}"
        
        # สร้าง messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # เรียก API พร้อม retry logic
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:5001",
                        "X-Title": "Cybersecurity Agent"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 500
                    },
                    timeout=30
                )
                
                # ตรวจสอบ rate limit (429)
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        # Exponential backoff: รอ 2^attempt วินาที
                        wait_time = 2 ** attempt
                        print(f"Rate limit hit. Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return "⚠️ API rate limit exceeded. Please wait a moment and try again. You can check your limits at https://openrouter.ai/settings/limits"
                
                response.raise_for_status()
                result = response.json()
                
                # ดึงคำตอบ
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    return "ขอโทษครับ ไม่สามารถสร้างคำตอบได้"
                    
            except requests.exceptions.Timeout:
                return "ขอโทษครับ การเชื่อมต่อหมดเวลา กรุณาลองใหม่อีกครั้ง"
            except requests.exceptions.RequestException as e:
                # ตรวจสอบว่าเป็น rate limit error หรือไม่
                if "429" in str(e) or "Too Many Requests" in str(e):
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"Rate limit detected. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return "⚠️ API rate limit exceeded. Please wait a moment and try again. You can check your limits at https://openrouter.ai/settings/limits"
                return f"เกิดข้อผิดพลาด: {str(e)}"
            except Exception as e:
                return f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {str(e)}"
        
        return "⚠️ Unable to complete request after multiple retries. Please try again later."
    
    def analyze_threat(self, threat_data: Dict) -> str:
        """
        วิเคราะห์ภัยคุกคามด้วย AI
        
        Args:
            threat_data: ข้อมูลภัยคุกคาม (logs, indicators, etc.)
        
        Returns:
            การวิเคราะห์จาก AI
        """
        
        prompt = f"""Analyze this security threat:

Threat Data:
{threat_data}

Please provide:
1. Severity assessment (Low/Medium/High/Critical)
2. Potential impact
3. Recommended actions
4. Prevention measures

Keep the response concise and actionable."""

        return self.chat(prompt)
    
    def search_knowledge_base(self, query: str, documents: List[Dict]) -> str:
        """
        ค้นหาและตอบคำถามจาก Knowledge Base
        
        Args:
            query: คำถาม
            documents: รายการเอกสารใน Knowledge Base
        
        Returns:
            คำตอบจาก AI พร้อมอ้างอิงเอกสาร
        """
        
        # สร้าง context จากเอกสาร (จำลอง - ในระบบจริงใช้ Vector Search)
        context = ""
        if documents:
            context = "Available documents:\n"
            for doc in documents[:5]:  # เอาแค่ 5 เอกสารแรก
                context += f"- {doc.get('filename', 'Unknown')}\n"
        
        prompt = f"""Based on the available cybersecurity knowledge base, please answer this question:

Question: {query}

{context}

Provide a helpful and accurate answer. If the information is not available in the knowledge base, provide general cybersecurity guidance."""

        return self.chat(prompt, context)
    
    def _get_demo_response(self, user_message: str) -> str:
        """
        สร้างคำตอบจำลองสำหรับ Demo Mode
        """
        msg_lower = user_message.lower()
        
        # คำตอบตามหัวข้อ
        if 'ddos' in msg_lower:
            return """🔒 **DDoS Attack (Distributed Denial of Service)**

A DDoS attack overwhelms a target system with massive traffic from multiple sources, making it unavailable to legitimate users.

**How it works:**
- Attackers use botnets (networks of compromised devices)
- Flood the target with requests
- Exhaust server resources (bandwidth, CPU, memory)

**Prevention:**
- Use CDN and load balancers
- Implement rate limiting
- Deploy DDoS protection services (Cloudflare, AWS Shield)
- Monitor traffic patterns

**Severity:** High to Critical depending on scale

*[Demo Mode - Enable API for real-time responses]*"""
        
        elif 'sql injection' in msg_lower or 'sql' in msg_lower:
            return """🔒 **SQL Injection Attack**

SQL injection exploits vulnerabilities in database queries to execute malicious SQL commands.

**Prevention:**
- Use parameterized queries/prepared statements
- Input validation and sanitization
- Principle of least privilege for database accounts
- Use ORM frameworks
- Regular security audits

**Example vulnerable code:**
```sql
SELECT * FROM users WHERE username = '$input'
```

**Severity:** Critical - Can lead to data breach

*[Demo Mode - Enable API for real-time responses]*"""
        
        elif 'ransomware' in msg_lower:
            return """🔒 **Ransomware**

Malware that encrypts victim's files and demands payment for decryption.

**Protection:**
- Regular backups (offline/offsite)
- Keep systems updated
- Email security and user training
- Endpoint protection
- Network segmentation

**If infected:**
1. Isolate affected systems
2. Don't pay ransom (no guarantee)
3. Report to authorities
4. Restore from backups

**Severity:** Critical

*[Demo Mode - Enable API for real-time responses]*"""
        
        else:
            return f"""🤖 **Cybersecurity Assistant (Demo Mode)**

I received your question: "{user_message}"

In demo mode, I can provide general cybersecurity guidance. For detailed, AI-powered responses, please:

1. Wait for API rate limit to reset (~10-30 minutes)
2. Or get a new API key from https://openrouter.ai/keys

**Common topics I can help with:**
- DDoS attacks
- SQL injection
- Ransomware
- Phishing
- Network security
- Threat analysis

*[Demo Mode Active - Limited responses]*"""
    
    def get_model_info(self) -> Dict:
        """
        ดึงข้อมูลโมเดล LLM ที่ใช้งาน
        
        Returns:
            ข้อมูลโมเดล
        """
        if self.demo_mode:
            return {
                "model": "Demo Mode",
                "provider": "Local",
                "type": "Simulated Responses",
                "status": "active"
            }
        return {
            "model": self.model,
            "provider": "OpenRouter",
            "type": "Free LLM",
            "status": "active" if self.api_key else "inactive"
        }
