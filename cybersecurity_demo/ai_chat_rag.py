"""
AI Chat Module with Full RAG Implementation
ใช้ OpenRouter API + Vector Store สำหรับตอบคำถามจากเอกสารจริง
"""

import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv()

class AIChatRAG:
    def __init__(self, vector_store=None):
        """
        สร้าง AI Chat ที่รองรับ RAG
        
        Args:
            vector_store: VectorStore instance สำหรับค้นหาเอกสาร
        """
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.model = os.getenv('OPENROUTER_MODEL', 'meta-llama/llama-3.2-3b-instruct:free')
        self.api_url = 'https://openrouter.ai/api/v1/chat/completions'
        self.vector_store = vector_store
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    def chat_with_rag(self, user_message: str, use_rag: bool = True) -> Dict:
        """
        ถามตอบกับ AI พร้อม RAG
        
        Args:
            user_message: คำถามจากผู้ใช้
            use_rag: ใช้ RAG หรือไม่
            
        Returns:
            Dict ที่มี response, context, sources
        """
        context = ""
        sources = []
        
        # ถ้าเปิด RAG และมี Vector Store
        if use_rag and self.vector_store:
            print(f"🔍 Searching vector store for: {user_message}")
            
            # ค้นหาเอกสารที่เกี่ยวข้อง
            search_results = self.vector_store.search(user_message, n_results=3)
            
            if search_results['results']:
                print(f"✅ Found {len(search_results['results'])} relevant chunks")
                
                # สร้าง context จากผลการค้นหา
                context_parts = []
                for i, result in enumerate(search_results['results'], 1):
                    filename = result['metadata'].get('filename', 'Unknown')
                    text = result['text']
                    distance = result.get('distance', 0)
                    
                    context_parts.append(f"[Source {i}: {filename}]\n{text}")
                    sources.append({
                        'filename': filename,
                        'text_preview': text[:200] + '...' if len(text) > 200 else text,
                        'relevance_score': 1 - distance if distance else 1.0
                    })
                
                context = "\n\n".join(context_parts)
                print(f"📚 Context length: {len(context)} characters")
            else:
                print("⚠️  No relevant documents found")
        
        # สร้าง system prompt
        if context:
            system_prompt = f"""You are a cybersecurity expert assistant with access to a knowledge base.

Use the following information from the knowledge base to answer the user's question:

{context}

Instructions:
- Answer based on the provided information
- If the information is not in the knowledge base, say so and provide general guidance
- Be concise and accurate
- Cite sources when possible"""
        else:
            system_prompt = """You are a cybersecurity expert assistant.
Provide helpful, accurate, and concise answers about cybersecurity topics."""
        
        # สร้าง messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # เรียก LLM API
        try:
            print(f"🤖 Calling LLM: {self.model}")
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:5001",
                    "X-Title": "Cybersecurity Agent RAG"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 800
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # ดึงคำตอบ
            if 'choices' in result and len(result['choices']) > 0:
                ai_response = result['choices'][0]['message']['content']
                print(f"✅ Got response: {len(ai_response)} characters")
                
                return {
                    'success': True,
                    'response': ai_response,
                    'context_used': bool(context),
                    'sources': sources,
                    'model': self.model
                }
            else:
                return {
                    'success': False,
                    'error': 'No response from LLM',
                    'context_used': False,
                    'sources': []
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout. Please try again.',
                'context_used': bool(context),
                'sources': sources
            }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if '429' in error_msg:
                error_msg = 'Rate limit exceeded. Please wait a moment and try again.'
            return {
                'success': False,
                'error': error_msg,
                'context_used': bool(context),
                'sources': sources
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'context_used': False,
                'sources': []
            }
    
    def analyze_threat_with_context(self, threat_data: Dict) -> Dict:
        """
        วิเคราะห์ภัยคุกคามด้วย AI + ข้อมูลจาก Knowledge Base
        
        Args:
            threat_data: ข้อมูลภัยคุกคาม
            
        Returns:
            การวิเคราะห์จาก AI
        """
        # สร้างคำถามสำหรับค้นหา
        threat_type = threat_data.get('type', 'Unknown')
        query = f"How to handle {threat_type} attack? Security recommendations"
        
        # ใช้ RAG เพื่อหาข้อมูลที่เกี่ยวข้อง
        result = self.chat_with_rag(
            f"Analyze this security threat and provide recommendations:\n{threat_data}",
            use_rag=True
        )
        
        return result
    
    def get_model_info(self) -> Dict:
        """
        ดึงข้อมูลโมเดล LLM และ Vector Store
        
        Returns:
            ข้อมูลโมเดล
        """
        info = {
            "model": self.model,
            "provider": "OpenRouter",
            "type": "Free LLM with RAG",
            "status": "active" if self.api_key else "inactive",
            "rag_enabled": self.vector_store is not None
        }
        
        if self.vector_store:
            stats = self.vector_store.get_stats()
            info.update({
                "vector_store": "ChromaDB",
                "total_documents": stats['total_documents'],
                "total_chunks": stats['total_chunks'],
                "embedding_model": stats['embedding_model']
            })
        
        return info
