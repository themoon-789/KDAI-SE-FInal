# 🤖 AI Chat Guide - Cybersecurity Assistant

## ✨ ฟีเจอร์ใหม่: AI Security Assistant

ระบบได้เพิ่มฟีเจอร์ AI Chat ที่ใช้ **OpenRouter API** กับ **Llama 3.2 (Free Model)** เพื่อตอบคำถามเกี่ยวกับความมั่นคงปลอดภัยทางไซเบอร์

## 🌐 เข้าใช้งาน

```
http://localhost:5001/chat
```

หรือคลิกที่เมนู **AI Chat** ใน Navigation Bar

## 🎯 Use Case: UC-ADM-04

### ถามตอบกับ AI เกี่ยวกับความมั่นคงปลอดภัย

**คุณสมบัติ:**
- ถามคำถามเกี่ยวกับ Cybersecurity
- วิเคราะห์ภัยคุกคาม
- ให้คำแนะนำด้านความปลอดภัย
- ค้นหาข้อมูลจาก Knowledge Base

## 🔧 การตั้งค่า

### 1. API Key Configuration

ไฟล์ `.env` ในโฟลเดอร์ `cybersecurity_demo/`:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
```

### 2. Dependencies

ติดตั้งเพิ่มเติม:
```bash
pip install python-dotenv requests
```

หรือใช้:
```bash
pip install -r requirements.txt
```

## 💬 วิธีใช้งาน

### 1. เริ่มสนทนา

1. ไปที่ http://localhost:5001/chat
2. พิมพ์คำถามในช่อง input
3. กด Enter หรือคลิก "ส่ง"
4. รอ AI ตอบ (ประมาณ 2-5 วินาที)

### 2. ตัวอย่างคำถาม

คลิกปุ่มตัวอย่างคำถาม:
- "What is a DDoS attack?"
- "How to prevent ransomware?"
- "Explain SQL injection"
- "Best practices for password security"
- "What is zero-day vulnerability?"

### 3. วิเคราะห์ Logs

คลิกปุ่ม **"วิเคราะห์ Logs ล่าสุด"** เพื่อให้ AI วิเคราะห์ Security Logs ที่มีระดับ CRITICAL

### 4. ล้างประวัติ

คลิกปุ่ม **"ล้างประวัติการสนทนา"** เพื่อเริ่มสนทนาใหม่

## 🎨 UI Features

### Chat Interface
- 💬 แสดงประวัติการสนทนา
- 👤 แยกข้อความของผู้ใช้และ AI
- ⏰ แสดงเวลาของแต่ละข้อความ
- 📜 Auto-scroll ไปยังข้อความล่าสุด

### AI Model Info
- 🤖 แสดงชื่อโมเดล LLM
- 🏢 แสดง Provider (OpenRouter)
- 📊 แสดงสถานะ (Active/Inactive)
- 🆓 แสดงประเภท (Free LLM)

## 🔌 API Endpoints

### POST /api/chat
ถามตอบกับ AI

**Request:**
```json
{
  "message": "What is a firewall?"
}
```

**Response:**
```json
{
  "success": true,
  "response": "A firewall is a network security system...",
  "model": "meta-llama/llama-3.2-3b-instruct:free"
}
```

### POST /api/analyze-threat
วิเคราะห์ภัยคุกคาม

**Request:**
```json
{
  "threat_data": {
    "type": "Port Scan",
    "source_ip": "192.168.1.100",
    "severity": "CRITICAL"
  }
}
```

**Response:**
```json
{
  "success": true,
  "analysis": "This appears to be a port scanning attack..."
}
```

### GET /api/ai-info
ดึงข้อมูล AI Model

**Response:**
```json
{
  "model": "meta-llama/llama-3.2-3b-instruct:free",
  "provider": "OpenRouter",
  "type": "Free LLM",
  "status": "active"
}
```

## 🎓 ตัวอย่างการใช้งาน

### Scenario 1: ถามคำถามทั่วไป
```
User: What is phishing?
AI: Phishing is a type of social engineering attack where attackers 
    impersonate legitimate entities to steal sensitive information...
```

### Scenario 2: ขอคำแนะนำ
```
User: How can I protect my organization from ransomware?
AI: Here are key recommendations:
    1. Regular backups
    2. Employee training
    3. Email filtering
    4. Patch management
    5. Network segmentation
```

### Scenario 3: วิเคราะห์ภัยคุกคาม
```
User: I see multiple failed login attempts from IP 192.168.1.100
AI: This could indicate a brute force attack. Recommended actions:
    1. Block the IP address
    2. Enable account lockout policies
    3. Implement MFA
    4. Review logs for other suspicious activities
```

## 🚀 Advanced Features

### 1. Context-Aware Responses
AI จะใช้ข้อมูลจาก Knowledge Base เป็น context ในการตอบคำถาม

### 2. Real-time Analysis
สามารถวิเคราะห์ Logs แบบ Real-time และให้คำแนะนำทันที

### 3. Multi-turn Conversations
รองรับการสนทนาต่อเนื่องหลายรอบ

## ⚠️ ข้อจำกัด

### Free Model Limitations
- **Rate Limit:** จำกัดจำนวนคำขอต่อนาที
- **Response Time:** อาจช้ากว่า Paid models
- **Context Length:** จำกัดความยาวของ context
- **Accuracy:** อาจไม่แม่นยำเท่า GPT-4

### แก้ไข Rate Limit
ถ้าเจอ "429 Too Many Requests":
1. รอสักครู่ (30-60 วินาที)
2. ลองถามใหม่
3. หรือเปลี่ยนเป็น Paid model

## 🔄 เปลี่ยน LLM Model

### ใช้ Free Models อื่น

แก้ไขใน `.env`:
```env
# Llama 3.2 3B (Free)
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free

# Llama 3.1 8B (Free)
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free

# Mistral 7B (Free)
OPENROUTER_MODEL=mistralai/mistral-7b-instruct:free

# Gemma 2 9B (Free)
OPENROUTER_MODEL=google/gemma-2-9b-it:free
```

### ใช้ Paid Models (แม่นยำกว่า)

```env
# GPT-4 Turbo
OPENROUTER_MODEL=openai/gpt-4-turbo

# Claude 3 Sonnet
OPENROUTER_MODEL=anthropic/claude-3-sonnet

# GPT-3.5 Turbo (ถูกกว่า)
OPENROUTER_MODEL=openai/gpt-3.5-turbo
```

## 🧪 การทดสอบ

### ทดสอบด้วย curl

```bash
# ทดสอบ AI Info
curl http://localhost:5001/api/ai-info

# ทดสอบ Chat
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is a firewall?"}'

# ทดสอบ Threat Analysis
curl -X POST http://localhost:5001/api/analyze-threat \
  -H "Content-Type: application/json" \
  -d '{"threat_data": {"type": "Port Scan", "severity": "HIGH"}}'
```

### ทดสอบด้วย Python

```python
import requests

# Chat
response = requests.post('http://localhost:5001/api/chat', 
    json={'message': 'What is ransomware?'})
print(response.json())

# AI Info
info = requests.get('http://localhost:5001/api/ai-info')
print(info.json())
```

## 📊 สถิติการใช้งาน

ดูได้ที่ OpenRouter Dashboard:
- https://openrouter.ai/activity

## 🔐 Security Notes

- ⚠️ **อย่าแชร์ API Key** ในที่สาธารณะ
- ✅ ใช้ `.env` สำหรับเก็บ API Key
- ✅ เพิ่ม `.env` ใน `.gitignore`
- ✅ ใช้ Environment Variables ใน Production

## 🎉 สรุป

ฟีเจอร์ AI Chat เพิ่มความสามารถให้ระบบ:
- ✅ ตอบคำถามเกี่ยวกับ Cybersecurity
- ✅ วิเคราะห์ภัยคุกคามอัตโนมัติ
- ✅ ให้คำแนะนำด้านความปลอดภัย
- ✅ ช่วยในการตัดสินใจ

---

**Model:** Llama 3.2 3B Instruct (Free)  
**Provider:** OpenRouter  
**Status:** ✅ Active
