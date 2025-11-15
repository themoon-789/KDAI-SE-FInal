# 🚀 Production Deployment Guide

## ระบบ Cybersecurity แบบจริง (Production-Ready)

ระบบนี้พร้อมใช้งานจริงด้วยฟีเจอร์:
- ✅ Database จริง (SQLite/PostgreSQL)
- ✅ Authentication & Authorization (JWT)
- ✅ Real Syslog Server (รับ log จากอุปกรณ์เครือข่าย)
- ✅ Vector Database (RAG) สำหรับ AI
- ✅ Document Processing (PDF, DOCX, TXT)
- ✅ Rate Limiting & Security
- ✅ Production Server (Gunicorn)

---

## 📋 ขั้นตอนการติดตั้ง

### 1. ติดตั้ง Dependencies

```bash
cd cybersecurity_demo
pip install -r requirements.txt
```

### 2. ตั้งค่า Environment Variables

สร้างไฟล์ `.env` หรือคัดลอกจาก `.env.production`:

```bash
cp .env.production .env
```

แก้ไขค่าต่อไปนี้:
- `SECRET_KEY`: สร้าง secret key ใหม่
- `JWT_SECRET_KEY`: สร้าง JWT secret key ใหม่
- `DATABASE_URL`: URL ของ database
- `OPENROUTER_API_KEY`: API key จาก OpenRouter (ถ้าต้องการใช้ AI)

### 3. สร้าง Database

```bash
python init_db.py
```

จะสร้าง:
- ตาราง database ทั้งหมด
- User: `admin` / `admin123` (role: admin)
- User: `analyst` / `analyst123` (role: analyst)
- Sample agents

### 4. เริ่มระบบ

#### Development Mode:
```bash
python app_production.py
```

#### Production Mode (Gunicorn):
```bash
# สร้างโฟลเดอร์ logs
mkdir -p logs

# เริ่ม Gunicorn
gunicorn -c gunicorn_config.py wsgi:app
```

---

## 🔧 การใช้งาน

### 1. เข้าสู่ระบบ

เปิดเบราว์เซอร์: `http://localhost:5001`

Login:
- Username: `admin`
- Password: `admin123`

### 2. อัพโหลดเอกสาร (Knowledge Base)

1. ไปที่ **Knowledge Base** (`/knowledge`)
2. คลิก Upload Document
3. เลือกไฟล์ (PDF, DOCX, TXT, JSON)
4. ระบบจะ:
   - แยกข้อความจากเอกสาร
   - สร้าง embeddings
   - เก็บใน Vector Database
   - พร้อมใช้กับ AI Chat (RAG)

### 3. รับ Security Logs

#### วิธีที่ 1: ส่ง Syslog จากอุปกรณ์จริง

ตั้งค่าอุปกรณ์ (Firewall, Router, Server) ให้ส่ง syslog มาที่:
- Host: `<server-ip>`
- Port: `514`
- Protocol: `UDP`

#### วิธีที่ 2: ทดสอบด้วย Script

```bash
python test_syslog.py
```

### 4. ใช้งาน AI Chat

1. ไปที่ **AI Chat** (`/chat`)
2. พิมพ์คำถาม เช่น:
   - "วิเคราะห์ DDoS attack"
   - "แนะนำวิธีป้องกัน SQL injection"
   - "อธิบายเกี่ยวกับ ransomware"
3. AI จะตอบโดยใช้ข้อมูลจาก Knowledge Base (RAG)

### 5. จัดการ Agents

1. ไปที่ **Agents** (`/agents`)
2. เพิ่ม/แก้ไข/ลบ agents
3. ดูสถานะและ last seen

---

## 🔐 Security Features

### Authentication
- JWT-based authentication
- Role-based access control (admin, analyst, viewer)
- Password hashing (bcrypt)

### Rate Limiting
- Login: 5 attempts per minute
- Document upload: 10 per hour
- AI chat: 30 per hour
- Log analysis: 20 per hour

### Input Validation
- File type checking
- File size limits (50MB)
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection

---

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Documents
- `GET /api/documents` - List documents
- `POST /api/documents/upload` - Upload document
- `DELETE /api/documents/<id>` - Delete document

### Logs
- `GET /api/logs` - Get logs (with pagination)
- `POST /api/logs/<id>/analyze` - Analyze log with AI

### Agents
- `GET /api/agents` - List agents
- `POST /api/agents` - Create agent
- `PUT /api/agents/<id>` - Update agent

### AI Chat
- `POST /api/chat` - Chat with AI
- `GET /api/chat/history` - Get chat history

### Stats
- `GET /api/stats` - System statistics

---

## 🗄️ Database Schema

### Users
- id, username, email, password_hash, role, is_active, created_at, last_login

### Documents
- id, filename, file_path, file_type, file_size, content_hash, status, uploaded_by, uploaded_at, processed_at, chunk_count, metadata

### SecurityLog
- id, timestamp, source_ip, source_host, facility, severity, message, raw_log, agent_id, threat_level, is_analyzed, analysis_result

### Agent
- id, name, agent_type, ip_address, hostname, status, protocol, port, last_seen, created_at, config

### ChatHistory
- id, user_id, message, response, model_used, timestamp, context_used

### ThreatIntelligence
- id, indicator_type, indicator_value, threat_type, severity, source, description, first_seen, last_seen, is_active, metadata

---

## 🚀 Production Deployment

### 1. ใช้ PostgreSQL แทน SQLite

```bash
# ติดตั้ง PostgreSQL
sudo apt install postgresql postgresql-contrib

# สร้าง database
sudo -u postgres createdb cybersecurity
sudo -u postgres createuser cyberuser -P

# แก้ไข .env
DATABASE_URL=postgresql://cyberuser:password@localhost/cybersecurity
```

### 2. ใช้ Nginx เป็น Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5001/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 3. ใช้ Systemd Service

สร้างไฟล์ `/etc/systemd/system/cybersecurity.service`:

```ini
[Unit]
Description=Cybersecurity System
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/cybersecurity_demo
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -c gunicorn_config.py wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

เริ่มใช้งาน:
```bash
sudo systemctl enable cybersecurity
sudo systemctl start cybersecurity
sudo systemctl status cybersecurity
```

### 4. SSL/TLS (HTTPS)

```bash
# ติดตั้ง Certbot
sudo apt install certbot python3-certbot-nginx

# สร้าง SSL certificate
sudo certbot --nginx -d yourdomain.com
```

---

## 📈 Monitoring & Logging

### Application Logs
- Access logs: `logs/access.log`
- Error logs: `logs/error.log`

### Database Backup
```bash
# SQLite
cp cybersecurity.db cybersecurity.db.backup

# PostgreSQL
pg_dump cybersecurity > backup.sql
```

### Health Check
```bash
curl http://localhost:5001/api/stats
```

---

## 🔧 Troubleshooting

### Syslog Server ไม่รับ logs
```bash
# ตรวจสอบว่า port 514 ถูกใช้งานหรือไม่
sudo netstat -tulpn | grep 514

# ถ้าใช้ port < 1024 ต้องรันด้วย sudo หรือเปลี่ยน port
```

### Vector Store Error
```bash
# ลบและสร้างใหม่
rm -rf data/vector_db
python init_db.py
```

### Database Migration
```bash
# ถ้าต้องการใช้ Alembic สำหรับ migration
pip install alembic
alembic init migrations
```

---

## 📚 Additional Resources

- [OpenRouter API](https://openrouter.ai/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

---

## 🆘 Support

หากมีปัญหาหรือคำถาม:
1. ตรวจสอบ logs ใน `logs/error.log`
2. ดู console output
3. ตรวจสอบ environment variables

---

## 📝 License

MIT License - ใช้งานได้อย่างอิสระ
