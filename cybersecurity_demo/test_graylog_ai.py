"""
ทดสอบการวิเคราะห์ Graylog logs ด้วย AI
"""

import os
import sys
from dotenv import load_dotenv

# เพิ่ม path
sys.path.insert(0, os.path.dirname(__file__))

from graylog_client import GraylogClient
from ai_chat_unified import UnifiedAIChat

# โหลด environment variables
load_dotenv()

def test_graylog_ai_analysis():
    """ทดสอบการวิเคราะห์ logs ด้วย AI"""
    print("=" * 70)
    print("  🤖 Testing Graylog AI Analysis")
    print("=" * 70)
    
    # 1. สร้าง Graylog Client
    print("\n1️⃣ Initializing Graylog Client...")
    try:
        graylog_client = GraylogClient(
            host=os.getenv('GRAYLOG_HOST', '10.10.89.6'),
            port=int(os.getenv('GRAYLOG_PORT', 9000)),
            api_token=os.getenv('GRAYLOG_API_TOKEN'),
            stream_name=os.getenv('GRAYLOG_STREAM_NAME', 'FortiGate Syslog')
        )
        print("✅ Graylog Client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Graylog Client: {e}")
        return
    
    # 2. ทดสอบการเชื่อมต่อ
    print("\n2️⃣ Testing Graylog connection...")
    if not graylog_client.test_connection():
        print("❌ Cannot connect to Graylog. Please check:")
        print("   - Graylog server is running")
        print("   - API token is correct")
        print("   - Network connectivity")
        return
    
    # 3. ดึง logs
    print("\n3️⃣ Fetching recent logs...")
    minutes = 30
    max_logs = 20
    
    logs = graylog_client.get_recent_logs(minutes=minutes, limit=max_logs)
    
    if not logs:
        print(f"⚠️  No logs found in the last {minutes} minutes")
        print("   Try increasing the time range or check if logs are being received")
        return
    
    print(f"✅ Retrieved {len(logs)} logs")
    
    # 4. จัดรูปแบบ logs สำหรับ LLM
    print("\n4️⃣ Preparing logs for AI analysis...")
    logs_text = graylog_client.prepare_logs_for_llm(logs, max_logs=max_logs)
    print(f"✅ Prepared {logs_text.count('Log #')} logs for analysis")
    
    # แสดงตัวอย่าง logs
    print("\n📝 Sample of prepared logs:")
    print("-" * 70)
    print(logs_text[:500] + "..." if len(logs_text) > 500 else logs_text)
    print("-" * 70)
    
    # 5. สร้าง AI Chat
    print("\n5️⃣ Initializing AI Chat...")
    try:
        ai_chat = UnifiedAIChat()
        print("✅ AI Chat initialized")
    except Exception as e:
        print(f"❌ Failed to initialize AI Chat: {e}")
        print("   Please check OPENROUTER_API_KEY in .env file")
        return
    
    # 6. วิเคราะห์ logs ด้วย AI
    print("\n6️⃣ Analyzing logs with AI...")
    print("   (This may take 10-30 seconds...)")
    
    result = ai_chat.analyze_graylog_logs(logs_text)
    
    if result['success']:
        print("\n" + "=" * 70)
        print("  ✅ AI ANALYSIS RESULTS")
        print("=" * 70)
        print(f"\n📊 Logs Analyzed: {result['logs_analyzed']}")
        print(f"🧠 Model: {result['model']}")
        print("\n" + "-" * 70)
        print(result['analysis'])
        print("-" * 70)
    else:
        print(f"\n❌ Analysis failed: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 70)
    print("  🎉 Test completed!")
    print("=" * 70)


if __name__ == "__main__":
    test_graylog_ai_analysis()
