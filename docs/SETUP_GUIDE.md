# 📖 Setup Guide - KDAI Cybersecurity Demo

คู่มือการติดตั้งและตั้งค่าระบบแบบละเอียด

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Configuration](#configuration)
4. [First Run](#first-run)
5. [Troubleshooting](#troubleshooting)

---

## 🖥️ System Requirements

### Minimum Requirements
- **OS:** Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Python:** 3.9 or higher
- **RAM:** 4 GB
- **Storage:** 2 GB free space
- **Internet:** Required for API calls

### Recommended Requirements
- **RAM:** 8 GB or more
- **Storage:** 5 GB free space
- **CPU:** Multi-core processor

---

## 🚀 Installation Steps

### 1. Install Python

#### Windows
```bash
# Download from python.org
# หรือใช้ Microsoft Store
winget install Python.Python.3.11
```

#### macOS
```bash
# ใช้ Homebrew
brew install python@3.11
```

#### Linux
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

### 2. Clone Repository

```bash
git clone https://github.com/themoon-789/KDAI-SE-FInal.git
cd KDAI-SE-FInal
```

### 3. Create Virtual Environment

```bash
# สร้าง virtual environment
python -m venv .venv

# Activate
# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
cd cybersecurity_demo
pip install --upgrade pip
pip install -r requirements.txt
```

**หมายเหตุ:** การติดตั้งอาจใช้เวลา 5-10 นาที

---

## ⚙️ Configuration

### 1. Setup Environment Variables

```bash
# Copy template
cp .env.example .env

# แก้ไขไฟล์ .env
nano .env  # หรือใช้ text editor ที่ชอบ
```

### 2. Get API Keys

#### OpenRouter API (Required)
1. ไปที่ https://openrouter.ai/
2. สมัครสมาชิก/Login
3. ไปที่ Settings → API Keys
4. สร้าง API key ใหม่
5. Copy key ใส่ใน `.env`:
   ```
   OPENROUTER_API_KEY=sk-or-v1-xxxxx
   ```

#### Graylog (Optional)
1. ติดตั้ง Graylog server หรือใช้ existing server
2. สร้าง API token:
   - System → Users → [Your User] → Edit Tokens
3. ใส่ข้อมูลใน `.env`:
   ```
   GRAYLOG_HOST=your_graylog_ip
   GRAYLOG_PORT=9000
   GRAYLOG_API_TOKEN=your_token
   GRAYLOG_STREAM_NAME=FortiGate Syslog
   ```

#### VirusTotal (Optional)
1. ไปที่ https://www.virustotal.com/
2. สมัครสมาชิก (Free tier)
3. ไปที่ Profile → API Key
4. Copy key ใส่ใน `.env`:
   ```
   VIRUSTOTAL_API_KEY=your_key
   ```

### 3. Initialize Database

```bash
# สร้าง database tables
python init_db.py

# ตรวจสอบระบบ
python check_system.py
```

---

## 🎬 First Run

### 1. Start Application

```bash
# Development mode
python app.py

# หรือใช้ production mode
python app_production.py
```

### 2. Access Web Interface

เปิดเบราว์เซอร์ไปที่:
- http://localhost:5001

### 3. Test Features

#### Test AI Chat
1. ไปที่ Knowledge Base
2. Upload เอกสารทดสอบ
3. ถามคำถาม

#### Test Graylog Integration
```bash
# ทดสอบการเชื่อมต่อ
python graylog_client.py

# ทดสอบ AI analysis
python test_graylog_ai.py
```

#### Test VirusTotal
1. ไปที่ VirusTotal Scanner
2. Upload ไฟล์ทดสอบ
3. ดูผลการสแกน

---

## 🐛 Troubleshooting

### ปัญหา: ModuleNotFoundError

**สาเหตุ:** ไม่ได้ activate virtual environment

**แก้ไข:**
```bash
# Activate venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### ปัญหา: "Graylog client not available"

**สาเหตุ:** API token ไม่ถูกต้องหรือ Graylog ไม่ทำงาน

**แก้ไข:**
1. ตรวจสอบ GRAYLOG_API_TOKEN ใน .env
2. ทดสอบการเชื่อมต่อ:
   ```bash
   python graylog_client.py
   ```
3. ตรวจสอบ Graylog server status

### ปัญหา: "AI Chat not available"

**สาเหตุ:** OpenRouter API key ไม่ถูกต้อง

**แก้ไข:**
1. ตรวจสอบ OPENROUTER_API_KEY ใน .env
2. ตรวจสอบ credit ใน OpenRouter account
3. ทดสอบ API key:
   ```bash
   curl https://openrouter.ai/api/v1/models \
     -H "Authorization: Bearer YOUR_KEY"
   ```

### ปัญหา: Port 5001 already in use

**แก้ไข:**
```bash
# หา process ที่ใช้ port
# macOS/Linux:
lsof -i :5001

# Windows:
netstat -ano | findstr :5001

# Kill process หรือเปลี่ยน port ใน app.py
```

### ปัญหา: ChromaDB errors

**แก้ไข:**
```bash
# ลบ database เดิม
rm -rf chroma_db/ chroma_db_exploitdb/

# Restart application
python app.py
```

### ปัญหา: Slow performance

**แก้ไข:**
1. ลด max_logs ใน AI analysis
2. ใช้ model ที่เร็วกว่า (เช่น gpt-3.5-turbo)
3. เพิ่ม RAM
4. ใช้ SSD

---

## 📚 Next Steps

1. อ่าน [GRAYLOG_AI_INTEGRATION.md](../GRAYLOG_AI_INTEGRATION.md) สำหรับ AI Log Analysis
2. อ่าน [API_EXAMPLES.md](../cybersecurity_demo/API_EXAMPLES.md) สำหรับ API usage
3. อ่าน [PRODUCTION_GUIDE.md](../cybersecurity_demo/PRODUCTION_GUIDE.md) สำหรับ production deployment

---

## 💡 Tips

1. **ใช้ .env.example เป็น template** - อย่าลืม copy เป็น .env
2. **เก็บ API keys ให้ปลอดภัย** - อย่า commit ขึ้น Git
3. **ทดสอบทีละส่วน** - ตรวจสอบว่าแต่ละ component ทำงาน
4. **อ่าน logs** - ดู console output เพื่อ debug
5. **Backup database** - สำรอง chroma_db/ เป็นประจำ

---

**Need Help?**
- 📖 [Documentation](../README.md)
- 🐛 [GitHub Issues](https://github.com/themoon-789/KDAI-SE-FInal/issues)
