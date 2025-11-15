# 🛡️ KDAI Cybersecurity Demo - Advanced Agent System

ระบบ AI Agent สำหรับงาน Cybersecurity ที่รวม RAG, Exploit-DB Integration, และ Graylog Log Analysis

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🌟 Features

### 1. **AI Chat with RAG (Retrieval-Augmented Generation)**
- ค้นหาและตอบคำถามจากเอกสาร Cybersecurity
- รองรับ PDF, TXT, DOCX
- Vector search ด้วย ChromaDB
- ใช้ OpenRouter API (GPT-4o-mini)

### 2. **Exploit-DB Papers Integration**
- ฐานข้อมูล security research papers จาก Exploit-DB
- 1,275+ PDF papers
- 96 documents embedded (expandable)
- ค้นหาข้อมูล exploits และ vulnerabilities

### 3. **🤖 Graylog Log Analysis with AI**
- **ใหม่!** วิเคราะห์ logs จาก Graylog ด้วย LLM
- ตรวจจับภัยคุกคามอัตโนมัติ
- วิเคราะห์รูปแบบการโจมตี
- ให้คำแนะนำด้านความปลอดภัย
- รองรับ FortiGate Syslog

### 4. **VirusTotal Scanner**
- สแกนไฟล์ด้วย VirusTotal API
- ตรวจสอบ malware และ threats
- แสดงผลแบบ real-time

### 5. **Security Dashboard**
- แสดงสถิติระบบ
- Monitor logs แบบ real-time
- Security events tracking

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip
- Git

### Installation

```bash
# 1. Clone repository
git clone https://github.com/themoon-789/KDAI-SE-FInal.git
cd KDAI-SE-FInal

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
cd cybersecurity_demo
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# แก้ไข .env ใส่ API keys

# 5. Run application
python app.py
```

### Access Application
- 🌐 **Main:** http://localhost:5001
- 📊 **Dashboard:** http://localhost:5001
- 📝 **Logs:** http://localhost:5001/logs
- 📚 **Knowledge Base:** http://localhost:5001/knowledge
- 🤖 **Agents:** http://localhost:5001/agents

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# OpenRouter API (สำหรับ LLM)
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini

# Graylog Configuration
GRAYLOG_HOST=10.10.89.6
GRAYLOG_PORT=9000
GRAYLOG_API_TOKEN=your_token_here
GRAYLOG_STREAM_NAME=FortiGate Syslog

# VirusTotal API
VIRUSTOTAL_API_KEY=your_key_here

# Application Settings
FLASK_ENV=development
FLASK_DEBUG=True
DEMO_MODE=false
```

---

## 📚 Documentation

### Main Guides
- **[START_HERE.md](START_HERE.md)** - เริ่มต้นใช้งาน
- **[GRAYLOG_AI_INTEGRATION.md](GRAYLOG_AI_INTEGRATION.md)** - 🆕 AI Log Analysis
- **[PRODUCTION_GUIDE.md](cybersecurity_demo/PRODUCTION_GUIDE.md)** - Production deployment
- **[API_EXAMPLES.md](cybersecurity_demo/API_EXAMPLES.md)** - API documentation

### Feature Guides
- **[RAG_SYSTEM_COMPLETE.md](RAG_SYSTEM_COMPLETE.md)** - RAG system details
- **[EXPLOITDB_INTEGRATION_GUIDE.md](cybersecurity_demo/EXPLOITDB_INTEGRATION_GUIDE.md)** - Exploit-DB setup
- **[AI_CHAT_GUIDE.md](cybersecurity_demo/AI_CHAT_GUIDE.md)** - AI Chat usage

---

## 🎯 Use Cases

### 1. Security Research
- ค้นหาข้อมูล exploits และ vulnerabilities
- วิเคราะห์ security papers
- ศึกษา attack patterns

### 2. Log Analysis
- วิเคราะห์ logs จาก Graylog/FortiGate
- ตรวจจับภัยคุกคามด้วย AI
- สร้างรายงานความปลอดภัย

### 3. Threat Intelligence
- สแกนไฟล์ด้วย VirusTotal
- ตรวจสอบ malware
- Track security events

### 4. Knowledge Management
- จัดเก็บเอกสาร security
- ค้นหาข้อมูลด้วย AI
- สร้าง knowledge base

---

## 🤖 AI Log Analysis - New Feature!

### วิธีใช้งาน

1. เปิดหน้า **Logs** (http://localhost:5001/logs)
2. คลิกปุ่ม **"🤖 AI วิเคราะห์ Logs"**
3. รอผลการวิเคราะห์ (10-30 วินาที)
4. ดูผลลัพธ์ใน modal

### การวิเคราะห์ครอบคลุม:
- ✅ Executive Summary - สรุปสถานการณ์
- ✅ Key Findings - ประเด็นสำคัญ
- ✅ Threat Assessment - ประเมินความรุนแรง
- ✅ Suspicious Activities - กิจกรรมน่าสงสัย
- ✅ Recommendations - คำแนะนำ

### API Endpoint
```bash
GET /api/graylog/ai-analyze?minutes=30&max_logs=50
```

ดูรายละเอียดเพิ่มเติมที่ [GRAYLOG_AI_INTEGRATION.md](GRAYLOG_AI_INTEGRATION.md)

---

## 📊 Project Structure

```
KDAI-SE-FInal/
├── cybersecurity_demo/          # Main application
│   ├── app.py                   # Flask application
│   ├── ai_chat_unified.py       # AI Chat with RAG
│   ├── graylog_client.py        # Graylog integration
│   ├── unified_vector_store.py  # Vector database
│   ├── virustotal_scanner.py    # VirusTotal integration
│   ├── templates/               # HTML templates
│   ├── requirements.txt         # Python dependencies
│   └── .env.example            # Environment template
├── docs/                        # Documentation
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

## 🧪 Testing

### Test Graylog Connection
```bash
cd cybersecurity_demo
python graylog_client.py
```

### Test AI Log Analysis
```bash
cd cybersecurity_demo
python test_graylog_ai.py
```

### Test Unified Vector Store
```bash
cd cybersecurity_demo
python test_unified.py
```

---

## 🔐 Security Notes

1. **API Keys:** เก็บใน `.env` และไม่ commit ขึ้น Git
2. **Graylog Token:** ใช้ token ที่มีสิทธิ์จำกัด
3. **Production:** ใช้ HTTPS และ proper authentication
4. **Rate Limiting:** พิจารณาเพิ่ม rate limit สำหรับ AI analysis

---

## 🛠️ Tech Stack

- **Backend:** Flask, Python 3.9+
- **AI/LLM:** OpenRouter API (GPT-4o-mini)
- **Vector DB:** ChromaDB
- **Embeddings:** sentence-transformers
- **Log Management:** Graylog API
- **Security:** VirusTotal API
- **Frontend:** Bootstrap 5, JavaScript

---

## 📈 Performance

- **Log Analysis:** ~15-35 วินาที
- **Vector Search:** <1 วินาที
- **Document Upload:** ~2-5 วินาที/document
- **VirusTotal Scan:** ~5-10 วินาที

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Authors

**KDAI Team** - Software Engineering Final Project

1. **นายภูวิศ จารุรัตน์กิจ** - รหัสนักศึกษา 67056056
2. **นายสิรภพ กิจเจริญรุ่งโรจน์** - รหัสนักศึกษา 67056078
3. **นายสุทธิ ดิลกเลิศพลากร** - รหัสนักศึกษา 67056082

- GitHub: [@themoon-789](https://github.com/themoon-789)

---

## 🙏 Acknowledgments

- [Exploit-DB](https://www.exploit-db.com/) - Security research papers
- [OpenRouter](https://openrouter.ai/) - LLM API
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [VirusTotal](https://www.virustotal.com/) - Malware scanning

---

## 📞 Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/themoon-789/KDAI-SE-FInal/issues)
- 📖 Docs: [Documentation](docs/)

---

**Version:** 2.0.0  
**Last Updated:** 2024-11-15  
**Status:** ✅ Production Ready
