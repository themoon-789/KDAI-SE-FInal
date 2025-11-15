"""
Enhanced AI Chat with RAG (Retrieval Augmented Generation)
"""
import os
import requests
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv
from vector_store import VectorStore

load_dotenv()

class AIChat:
    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.model = os.getenv('OPENROUTER_MODEL', 'google/gemini-2.0-flash-exp:free')
        self.api_url = 'https://openrouter.ai/api/v1/chat/completions'
        self.demo_mode = os.getenv('DEMO_MODE', 'false').lower() == 'true'
        self.vector_store = vector_store
        
        if not self.api_key and not self.demo_mode:
            print("⚠️  OPENROUTER_API_KEY not found. Running in demo mode.")
            self.demo_mode = True
    
    def chat(self, user_message: str, use_rag: bool = True, max_retries: int = 3) -> Dict:
        """
        Chat with AI using RAG if enabled
        
        Returns:
            {
                'response': str,
                'sources': List[Dict],
                'model': str
            }
        """
        sources = []
        context = ""
        
        # Use RAG if enabled and vector store is available
        if use_rag and self.vector_store:
            search_results = self.vector_store.search(user_message, n_results=3)
            if search_results:
                sources = search_results
                context = "\n\n".join([
                    f"[Source: {r['metadata']['filename']}]\n{r['content']}"
                    for r in search_results
                ])
        
        # Get AI response
        if self.demo_mode:
            response = self._get_demo_response(user_message, context)
        else:
            response = self._call_api(user_message, context, max_retries)
        
        return {
            'response': response,
            'sources': sources,
            'model': self.model if not self.demo_mode else 'Demo Mode'
        }
    
    def analyze_threat(self, threat_data: Dict) -> Dict:
        """Analyze security threat"""
        prompt = f"""Analyze this security threat and provide assessment:

Threat Data:
{threat_data}

Provide:
1. Severity Level (Low/Medium/High/Critical)
2. Threat Type
3. Potential Impact
4. Recommended Actions
5. Prevention Measures

Format as JSON."""

        response = self.chat(prompt, use_rag=False)
        
        return {
            'analysis': response['response'],
            'model': response['model']
        }
    
    def analyze_log(self, log_message: str, log_metadata: Dict = None) -> Dict:
        """Analyze security log"""
        prompt = f"""Analyze this security log:

Log: {log_message}

Metadata: {log_metadata if log_metadata else 'None'}

Determine:
1. Is this suspicious? (Yes/No)
2. Threat level (Low/Medium/High/Critical)
3. Threat type (if applicable)
4. Recommended action

Be concise."""

        response = self.chat(prompt, use_rag=True)
        
        return {
            'is_suspicious': 'yes' in response['response'].lower()[:100],
            'analysis': response['response'],
            'sources': response['sources']
        }
    
    def _call_api(self, user_message: str, context: str, max_retries: int) -> str:
        """Call OpenRouter API with retry logic"""
        system_prompt = """You are a cybersecurity expert assistant.
Analyze threats, provide recommendations, and answer questions about security.
Be concise, accurate, and actionable."""

        if context:
            system_prompt += f"\n\nRelevant information from knowledge base:\n{context}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
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
                        "max_tokens": 1000
                    },
                    timeout=30
                )
                
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        time.sleep(wait_time)
                        continue
                    return "⚠️ API rate limit exceeded. Please try again later."
                
                response.raise_for_status()
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                
                return "Unable to generate response"
                
            except requests.exceptions.Timeout:
                return "Request timeout. Please try again."
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return f"Error: {str(e)}"
        
        return "Unable to complete request after retries"
    
    def _get_demo_response(self, user_message: str, context: str = "") -> str:
        """Generate demo response"""
        msg_lower = user_message.lower()
        
        response = f"🤖 **Demo Mode Response**\n\n"
        
        if context:
            response += f"📚 Found relevant information in knowledge base.\n\n"
        
        if 'ddos' in msg_lower:
            response += """**DDoS Attack Analysis**

A Distributed Denial of Service attack overwhelms systems with traffic.

**Mitigation:**
- Use CDN and load balancers
- Implement rate limiting
- Deploy DDoS protection (Cloudflare, AWS Shield)
- Monitor traffic patterns

**Severity:** High to Critical"""
        
        elif 'sql' in msg_lower or 'injection' in msg_lower:
            response += """**SQL Injection Prevention**

**Best Practices:**
- Use parameterized queries
- Input validation
- Least privilege database accounts
- Regular security audits

**Severity:** Critical"""
        
        elif 'malware' in msg_lower or 'ransomware' in msg_lower:
            response += """**Malware/Ransomware Protection**

**Defense:**
- Regular backups (offline)
- Keep systems updated
- Email security training
- Endpoint protection
- Network segmentation

**Severity:** Critical"""
        
        else:
            response += f"""I received your question about: "{user_message}"

**General Cybersecurity Guidance:**
- Keep systems updated
- Use strong authentication
- Monitor logs regularly
- Implement defense in depth
- Train users on security

For detailed AI-powered analysis, configure OPENROUTER_API_KEY."""
        
        response += "\n\n*[Demo Mode - Configure API key for full AI capabilities]*"
        
        return response
    
    def get_model_info(self) -> Dict:
        """Get AI model information"""
        return {
            "model": self.model if not self.demo_mode else "Demo Mode",
            "provider": "OpenRouter" if not self.demo_mode else "Local",
            "rag_enabled": self.vector_store is not None,
            "status": "active"
        }
