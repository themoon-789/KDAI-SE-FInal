# 🛡️ Cybersecurity System - Production Version

## ภาพรวม

ระบบ Cybersecurity แบบ Production-Ready ที่พร้อมใช้งานจริง พัฒนาจาก demo เป็นระบบที่มีความสามารถเต็มรูปแบบ

## ✨ ฟีเจอร์หลัก

### 🔐 Authentication & Authorization
- ระบบ Login/Logout ด้วย JWT
- Role-based access control (Admin, Analyst, Viewer)
- Password hashing ด้วย bcrypt
- Session management

### 📚 Knowledge Base (RAG)
- อัพโหลดเอกสาร: PDF, DOCX, TXT, JSON
- Document processing และ text extraction
- Vector embeddings ด้วย Sentence Transformers
- ChromaDB สำหรับ vector storage
- Semantic search สำหรับ AI

### 📝 Real-time Log Collection
- Syslog server (UDP/TCP)
- รับ logs จากอุปกรณ์เครือข่ายจริง
- Automatic log parsing (RFC 3164/5424)
- Threat level assessment
- Real-time dashboard updates

### 🤖 AI-Powered Analysis
- Chat with AI (OpenRouter API)
- RAG (Retrieval Augmented Generation)
- Automatic log analysis
- Threat assessment
- Security recommendations

### 🖥️ Agent Management
- จัดการ monitoring agents
- Track agent status
- Configure syslog endpoints
- Monitor last seen

### 📊 Dashboard & Analytics
- Real-time statistics
- Log visualization
- Agent status monitoring
- System health metrics

## 🏗️ สถาปัตยกรรม

```
cybersecurity_demo/
├── app_production.py          # Main application (Production)
├── models.py                  # Database models
├── config.py                  # Configuration
├── auth.py                    # Authentication
├── syslog_server.py          # Real syslog server
├── document_processor.py     # Document processing
├── vector_store.py           # Vector database (ChromaDB)
├── ai_chat_enhanced.py       # AI with RAG
├── init_db.py                # Database initialization
├── wsgi.py                   # WSGI entry point
├── gunicorn_config.py        # Gunicorn config
├── test_syslog.py            # Syslog testing tool
├── requirements.txt          # Dependencies
├── .env.production           # Production config template
└── templates/                # HTML templates
```

## 🚀 Quick Start

### 1. ติดตั้ง

```bash
# Clone หรือ cd เข้าโฟลเดอร์
cd cybersecurity_demo

# สร้าง virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# หรือ venv\Scripts\activate  # Windows

# ติดตั้ง dependencies
pip install -r requirements.txt
```

### 2. ตั้งค่า

```bash
# คัดลอก config
cp .env.production .env

# แก้ไข .env (ใส่ API key, database URL, etc.)
nano .env
```

### 3. สร้าง Database

```bash
python init_db.py
```

### 4. เริ่มระบบ

```bash
# Development
python app_production.py

# Production
gunicorn -c gunicorn_config.py wsgi:app
```

### 5. เข้าใช้งาน

เปิดเบราว์เซอร์: http://localhost:5001

**Default Login:**
- Username: `admin`
- Password: `admin123`

## 📖 การใช้งาน

### อัพโหลดเอกสาร
1. ไปที่ Knowledge Base
2. คลิก Upload
3. เลือกไฟล์ (PDF, DOCX, TXT)
4. ระบบจะประมวลผลและสร้าง embeddings อัตโนมัติ

### รับ Security Logs
```bash
# ทดสอบส่ง logs
python test_syslog.py

# หรือตั้งค่าอุปกรณ์ให้ส่ง syslog มาที่
# Host: <server-ip>
# Port: 514
# Protocol: UDP
```

### ใช้ AI Chat
1. ไปที่ AI Chat
2. พิมพ์คำถาม
3. AI จะตอบโดยใช้ข้อมูลจาก Knowledge Base

## 🔧 Configuration

### Database Options

**SQLite (Development):**
```env
DATABASE_URL=sqlite:///cybersecurity.db
```

**PostgreSQL (Production):**
```env
DATABASE_URL=postgresql://user:pass@localhost/cybersecurity
```

### AI Configuration

```env
OPENROUTER_API_KEY=your-key-here
OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
DEMO_MODE=false
```

### Syslog Server

```env
SYSLOG_HOST=0.0.0.0
SYSLOG_PORT=514
SYSLOG_PROTOCOL=UDP
```

## 🔒 Security Features

- JWT authentication
- Password hashing (bcrypt)
- Rate limiting
- CORS protection
- Input validation
- SQL injection prevention
- XSS protection
- File upload validation

## 📊 API Documentation

### Authentication
```bash
# Login
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get current user
curl http://localhost:5001/api/auth/me \
  -H "Authorization: Bearer <token>"
```

### Documents
```bash
# Upload document
curl -X POST http://localhost:5001/api/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf"

# List documents
curl http://localhost:5001/api/documents \
  -H "Authorization: Bearer <token>"
```

### AI Chat
```bash
# Chat
curl -X POST http://localhost:5001/api/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message":"What is DDoS attack?","use_rag":true}'
```

## 🚀 Production Deployment

### ใช้ Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /socket.io {
        proxy_pass http://127.0.0.1:5001/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### ใช้ Systemd

```ini
[Unit]
Description=Cybersecurity System
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/cybersecurity_demo
ExecStart=/path/to/venv/bin/gunicorn -c gunicorn_config.py wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📈 Monitoring

### Logs
- Access: `logs/access.log`
- Error: `logs/error.log`

### Health Check
```bash
curl http://localhost:5001/api/stats
```

## 🧪 Testing

```bash
# Test syslog server
python test_syslog.py

# Test API
curl http://localhost:5001/api/stats
```

## 🔄 Differences from Demo

| Feature | Demo Version | Production Version |
|---------|-------------|-------------------|
| Data Storage | In-memory | Database (SQLite/PostgreSQL) |
| Authentication | None | JWT-based |
| Syslog | Simulated | Real UDP/TCP server |
| Document Processing | Basic | Full extraction + embeddings |
| AI | Simple API calls | RAG with vector search |
| Security | Basic | Rate limiting, validation |
| Deployment | Flask dev server | Gunicorn + Nginx |

## 📚 Dependencies

- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **JWT**: Authentication
- **ChromaDB**: Vector database
- **Sentence Transformers**: Embeddings
- **PyPDF2**: PDF processing
- **python-docx**: DOCX processing
- **Gunicorn**: Production server

## 🆘 Troubleshooting

### Port 514 requires root
```bash
# Option 1: Run with sudo
sudo python app_production.py

# Option 2: Change port in .env
SYSLOG_PORT=5140
```

### Vector store error
```bash
rm -rf data/vector_db
python init_db.py
```

### Database locked (SQLite)
```bash
# Use PostgreSQL for production
# Or ensure only one process accesses SQLite
```

## 📝 TODO / Future Enhancements

- [ ] Threat intelligence feeds integration
- [ ] Automated incident response
- [ ] Email/Slack notifications
- [ ] Advanced analytics dashboard
- [ ] Machine learning for anomaly detection
- [ ] Multi-tenancy support
- [ ] API rate limiting per user
- [ ] Audit logging
- [ ] Export reports (PDF/CSV)

## 🤝 Contributing

ยินดีรับ contributions! สามารถ:
- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

MIT License - ใช้งานได้อย่างอิสระ

## 📞 Support

หากมีคำถามหรือปัญหา:
1. ตรวจสอบ logs
2. อ่าน PRODUCTION_GUIDE.md
3. ดู API documentation

---

**สร้างโดย:** Cybersecurity Team  
**Version:** 2.0.0 (Production)  
**Last Updated:** 2024
