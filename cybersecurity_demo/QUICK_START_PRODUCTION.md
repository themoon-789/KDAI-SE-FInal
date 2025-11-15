# ⚡ Quick Start - Production System

## เริ่มใช้งานภายใน 5 นาที!

### 1️⃣ ติดตั้ง (1 นาที)

```bash
cd cybersecurity_demo
pip install -r requirements.txt
```

### 2️⃣ ตั้งค่า (1 นาที)

```bash
# คัดลอก config
cp .env.production .env

# (Optional) แก้ไข API key ถ้าต้องการใช้ AI จริง
# nano .env
```

### 3️⃣ สร้าง Database (30 วินาที)

```bash
python init_db.py
```

### 4️⃣ เริ่มระบบ (30 วินาที)

```bash
python app_production.py
```

### 5️⃣ เข้าใช้งาน (1 นาที)

เปิดเบราว์เซอร์: **http://localhost:5001**

**Login:**
- Username: `admin`
- Password: `admin123`

---

## 🎯 ทดสอบฟีเจอร์

### ทดสอบ Syslog (Terminal ใหม่)
```bash
python test_syslog.py
```
→ ดู logs ที่ Dashboard

### ทดสอบ Upload Document
1. ไปที่ Knowledge Base
2. Upload ไฟล์ PDF/DOCX/TXT
3. ดูสถานะการประมวลผล

### ทดสอบ AI Chat
1. ไปที่ AI Chat
2. ถาม: "What is DDoS attack?"
3. ดูคำตอบจาก AI

---

## 🚀 Production Deployment

### วิธีที่ 1: Gunicorn
```bash
./start_production.sh
```

### วิธีที่ 2: Docker
```bash
docker-compose up -d
```

---

## 📚 เอกสารเพิ่มเติม

- **PRODUCTION_GUIDE.md** - คู่มือฉบับเต็ม
- **DEPLOYMENT_OPTIONS.md** - วิธี deploy แบบต่างๆ
- **README_PRODUCTION.md** - Overview

---

## 🆘 เจอปัญหา?

### Port 514 ต้องใช้ sudo
```bash
# เปลี่ยน port ใน .env
SYSLOG_PORT=5140
```

### ติดตั้ง dependencies ไม่ได้
```bash
# ใช้ virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Database error
```bash
# ลบและสร้างใหม่
rm cybersecurity.db
python init_db.py
```

---

**เท่านี้ก็พร้อมใช้งานแล้ว!** 🎉
