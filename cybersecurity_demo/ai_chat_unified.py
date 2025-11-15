"""
AI Chat with Unified RAG - รวม Exploit-DB Papers
ระบบ AI Chat ที่ค้นหาจากทั้งเอกสารทั่วไปและ Exploit-DB Papers
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# เพิ่ม path
sys.path.insert(0, os.path.dirname(__file__))
from unified_vector_store import UnifiedVectorStore

# โหลด environment variables
load_dotenv()

class UnifiedAIChat:
    def __init__(self):
        """เริ่มต้น AI Chat พร้อม Unified Vector Store"""
        print("🤖 Initializing Unified AI Chat...")
        
        # ตรวจสอบ API key
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("❌ OPENROUTER_API_KEY not found in .env file")
        
        # สร้าง OpenAI client สำหรับ OpenRouter
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = os.getenv('OPENROUTER_MODEL', 'openai/gpt-4o-mini')
        
        # สร้าง Unified Vector Store
        self.vector_store = UnifiedVectorStore()
        
        # แสดงสถิติ
        self.vector_store.print_stats()
        
        print("✅ Unified AI Chat ready!\n")
    
    def chat(self, user_message: str, search_sources: list = None, n_results: int = 5) -> dict:
        """
        สนทนากับ AI พร้อม RAG จากหลาย sources
        
        Args:
            user_message: ข้อความจากผู้ใช้
            search_sources: ['main', 'exploitdb'] หรือ None (ค้นหาทุก source)
            n_results: จำนวนเอกสารที่จะดึงมาใช้
        
        Returns:
            dict ที่มี response และ context
        """
        print(f"💬 User: {user_message}")
        print("🔍 Searching knowledge base...")
        
        # ค้นหาเอกสารที่เกี่ยวข้อง
        search_results = self.vector_store.search_combined(
            user_message, 
            n_results=n_results
        )
        
        # สร้าง context จากผลลัพธ์
        context_parts = []
        sources_info = []
        
        for i, result in enumerate(search_results, 1):
            source = result['source']
            doc = result['document']
            metadata = result['metadata']
            score = result['relevance_score']
            
            # เพิ่ม context
            context_parts.append(f"[Document {i} from {source.upper()}]\n{doc}\n")
            
            # เก็บข้อมูล source
            source_info = {
                'source': source,
                'score': score,
                'metadata': metadata
            }
            sources_info.append(source_info)
        
        context = "\n".join(context_parts)
        
        print(f"📚 Found {len(search_results)} relevant documents")
        
        # สร้าง prompt
        system_prompt = """You are a cybersecurity expert assistant with access to a comprehensive knowledge base including:
1. General cybersecurity documents and reports
2. Exploit-DB security research papers

Your role:
- Provide accurate, detailed answers based on the provided context
- Cite sources when possible (mention if from general docs or Exploit-DB papers)
- If the context doesn't contain enough information, say so clearly
- Focus on practical, actionable security advice
- Explain technical concepts clearly

Always prioritize security best practices and ethical considerations."""

        user_prompt = f"""Context from knowledge base:

{context}

---

User question: {user_message}

Please provide a comprehensive answer based on the context above. If you reference specific information, mention which source it came from (general documents or Exploit-DB papers)."""

        # เรียก Groq API
        print("🤖 Generating response...")
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=2000
            )
            
            response = chat_completion.choices[0].message.content
            
            print("✅ Response generated\n")
            
            return {
                'response': response,
                'context': context,
                'sources': sources_info,
                'model': self.model
            }
            
        except Exception as e:
            error_msg = f"❌ Error calling Groq API: {str(e)}"
            print(error_msg)
            return {
                'response': error_msg,
                'context': context,
                'sources': sources_info,
                'model': self.model
            }
    
    def analyze_graylog_logs(self, logs_text: str) -> dict:
        """
        วิเคราะห์ logs จาก Graylog ด้วย LLM
        
        Args:
            logs_text: ข้อความ logs ที่จัดรูปแบบแล้ว
        
        Returns:
            dict ที่มี analysis และ recommendations
        """
        print("🔍 Analyzing Graylog logs with AI...")
        
        system_prompt = """You are a cybersecurity expert specializing in log analysis and threat detection.

Your role:
- Analyze security logs from Graylog/FortiGate firewall
- Identify potential security threats, anomalies, and suspicious patterns
- Provide severity assessment (Critical, High, Medium, Low)
- Give actionable recommendations for security team
- Explain technical findings in clear, concise language

Focus on:
- Attack patterns and intrusion attempts
- Unusual traffic patterns
- Policy violations
- Malware indicators
- Data exfiltration attempts
- Brute force attacks
- DDoS patterns"""

        user_prompt = f"""Please analyze the following security logs and provide:

1. **Executive Summary**: Brief overview of the security situation
2. **Key Findings**: Most important security events and patterns
3. **Threat Assessment**: Severity level and potential impact
4. **Suspicious Activities**: Detailed analysis of concerning events
5. **Recommendations**: Immediate actions and long-term improvements

Logs to analyze:

{logs_text}

Provide your analysis in Thai language for better understanding by the security team."""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.3,  # Lower temperature for more focused analysis
                max_tokens=3000
            )
            
            response = chat_completion.choices[0].message.content
            
            print("✅ Analysis completed\n")
            
            return {
                'success': True,
                'analysis': response,
                'model': self.model,
                'logs_analyzed': logs_text.count('Log #')
            }
            
        except Exception as e:
            error_msg = f"❌ Error analyzing logs: {str(e)}"
            print(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'model': self.model
            }
    
    def interactive_chat(self):
        """โหมดสนทนาแบบ interactive"""
        print("=" * 60)
        print("  🤖 Unified AI Chat - Interactive Mode")
        print("=" * 60)
        print("\nCommands:")
        print("  - Type your question to chat")
        print("  - 'stats' to show database statistics")
        print("  - 'sources' to toggle search sources")
        print("  - 'quit' or 'exit' to exit")
        print("\n" + "=" * 60 + "\n")
        
        search_sources = None  # None = ค้นหาทุก source
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if user_input.lower() == 'stats':
                    self.vector_store.print_stats()
                    continue
                
                if user_input.lower() == 'sources':
                    print("\nSelect sources to search:")
                    print("1. All sources (default)")
                    print("2. Main database only")
                    print("3. Exploit-DB papers only")
                    
                    choice = input("Choice (1-3): ").strip()
                    
                    if choice == '1':
                        search_sources = None
                        print("✅ Searching all sources\n")
                    elif choice == '2':
                        search_sources = ['main']
                        print("✅ Searching main database only\n")
                    elif choice == '3':
                        search_sources = ['exploitdb']
                        print("✅ Searching Exploit-DB papers only\n")
                    
                    continue
                
                # ส่งคำถามไปยัง AI
                result = self.chat(user_input, search_sources=search_sources)
                
                # แสดงผลลัพธ์
                print(f"\n🤖 AI: {result['response']}\n")
                
                # แสดง sources ที่ใช้
                print("📚 Sources used:")
                for i, source in enumerate(result['sources'][:3], 1):
                    source_name = source['source'].upper()
                    score = source['score']
                    metadata = source['metadata']
                    
                    print(f"   {i}. [{source_name}] Score: {score:.3f}")
                    
                    if source['source'] == 'exploitdb':
                        title = metadata.get('title', 'Untitled')
                        print(f"      Title: {title}")
                    else:
                        filename = metadata.get('filename', 'Unknown')
                        print(f"      File: {filename}")
                
                print("\n" + "-" * 60 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")


def demo():
    """ตัวอย่างการใช้งาน"""
    try:
        # สร้าง AI Chat
        chat = UnifiedAIChat()
        
        # ตัวอย่างคำถาม
        questions = [
            "What are common SQL injection techniques?",
            "How does buffer overflow work?",
            "Explain XSS attack and prevention methods"
        ]
        
        print("=" * 60)
        print("  Demo: Asking sample questions")
        print("=" * 60 + "\n")
        
        for question in questions:
            print(f"\n{'='*60}")
            result = chat.chat(question, n_results=3)
            print(f"\n🤖 Answer:\n{result['response']}\n")
            print(f"{'='*60}\n")
            
            input("Press Enter for next question...")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        demo()
    else:
        try:
            chat = UnifiedAIChat()
            chat.interactive_chat()
        except Exception as e:
            print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
