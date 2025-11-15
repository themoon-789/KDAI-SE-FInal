# 🚀 Deployment Options

มี 3 วิธีในการ deploy ระบบ Cybersecurity นี้:

## 1. 🐍 Python Direct (แนะนำสำหรับ Development)

### ข้อดี
- ง่ายที่สุด
- เหมาะสำหรับทดสอบและพัฒนา
- ไม่ต้องติดตั้งอะไรเพิ่ม

### วิธีการ

```bash
# ติดตั้ง dependencies
pip install -r requirements.txt

# สร้าง database
python init_db.py

# เริ่มระบบ
python app_production.py
```

เข้าใช้งาน: http://localhost:5001

---

## 2. 🦄 Gunicorn + Nginx (แนะนำสำหรับ Production)

### ข้อดี
- Production-ready
- รองรับ concurrent requests
- มี reverse proxy (Nginx)
- SSL/TLS support

### วิธีการ

#### ติดตั้ง Nginx
```bash
# Ubuntu/Debian
sudo apt install nginx

# macOS
brew install nginx
```

#### ตั้งค่า Nginx
```bash
# คัดลอก config
sudo cp nginx.conf /etc/nginx/sites-available/cybersecurity
sudo ln -s /etc/nginx/sites-available/cybersecurity /etc/nginx/sites-enabled/

# ทดสอบ config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

#### เริ่มระบบ
```bash
# ใช้ startup script
./start_production.sh

# หรือรันด้วยตัวเอง
gunicorn -c gunicorn_config.py wsgi:app
```

#### ตั้งค่า Systemd (Auto-start)
```bash
# สร้างไฟล์ service
sudo nano /etc/systemd/system/cybersecurity.service
```

เพิ่มเนื้อหา:
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

---

## 3. 🐳 Docker (แนะนำสำหรับ Production + Scalability)

### ข้อดี
- Isolated environment
- Easy deployment
- Scalable
- รวม PostgreSQL
- รวม Nginx

### วิธีการ

#### ติดตั้ง Docker
```bash
# Ubuntu
sudo apt install docker.io docker-compose

# macOS
brew install docker docker-compose
```

#### ตั้งค่า Environment
```bash
# สร้างไฟล์ .env
cp .env.production .env

# แก้ไขค่าต่างๆ
nano .env
```

#### Build และ Run
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# ดู logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Services ที่รัน
- **app**: Web application (port 5001)
- **db**: PostgreSQL database
- **nginx**: Reverse proxy (port 80, 443)

#### จัดการ Container
```bash
# ดูสถานะ
docker-compose ps

# Restart service
docker-compose restart app

# เข้า shell ใน container
docker-compose exec app bash

# ดู logs
docker-compose logs app

# Backup database
docker-compose exec db pg_dump -U cyberuser cybersecurity > backup.sql
```

---

## 📊 เปรียบเทียบ

| Feature | Python Direct | Gunicorn + Nginx | Docker |
|---------|--------------|------------------|--------|
| ความง่าย | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Performance | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Scalability | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Production Ready | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Isolation | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Setup Time | 5 min | 20 min | 15 min |

---

## 🔒 SSL/TLS Configuration

### ใช้ Let's Encrypt (Free)

```bash
# ติดตั้ง Certbot
sudo apt install certbot python3-certbot-nginx

# สร้าง certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### ใช้ Self-signed Certificate (Testing)

```bash
# สร้าง certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# แก้ไข nginx.conf เพื่อเปิด HTTPS
```

---

## 🌐 Cloud Deployment

### AWS EC2
```bash
# Launch EC2 instance (Ubuntu)
# Install Docker
sudo apt update
sudo apt install docker.io docker-compose

# Clone repository
git clone <your-repo>
cd cybersecurity_demo

# Deploy
docker-compose up -d
```

### Google Cloud Run
```bash
# Build image
docker build -t gcr.io/PROJECT_ID/cybersecurity .

# Push to registry
docker push gcr.io/PROJECT_ID/cybersecurity

# Deploy
gcloud run deploy cybersecurity \
  --image gcr.io/PROJECT_ID/cybersecurity \
  --platform managed
```

### DigitalOcean Droplet
```bash
# Create droplet (Ubuntu)
# SSH to droplet
ssh root@your-droplet-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Deploy
git clone <your-repo>
cd cybersecurity_demo
docker-compose up -d
```

---

## 📈 Monitoring

### Application Monitoring
```bash
# ดู logs
tail -f logs/error.log
tail -f logs/access.log

# ดู system resources
htop
```

### Database Monitoring
```bash
# SQLite
sqlite3 cybersecurity.db "SELECT COUNT(*) FROM security_logs;"

# PostgreSQL
docker-compose exec db psql -U cyberuser -d cybersecurity -c "SELECT COUNT(*) FROM security_logs;"
```

### Health Check
```bash
# API health
curl http://localhost:5001/api/stats

# Nginx status
sudo systemctl status nginx

# Docker status
docker-compose ps
```

---

## 🔄 Updates & Maintenance

### Update Application
```bash
# Pull latest code
git pull

# Rebuild (Docker)
docker-compose down
docker-compose build
docker-compose up -d

# Restart (Systemd)
sudo systemctl restart cybersecurity
```

### Database Backup
```bash
# SQLite
cp cybersecurity.db backups/cybersecurity_$(date +%Y%m%d).db

# PostgreSQL (Docker)
docker-compose exec db pg_dump -U cyberuser cybersecurity > backup_$(date +%Y%m%d).sql
```

### Log Rotation
```bash
# Create logrotate config
sudo nano /etc/logrotate.d/cybersecurity
```

เพิ่ม:
```
/path/to/cybersecurity_demo/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
```

---

## 🆘 Troubleshooting

### Port Already in Use
```bash
# หา process ที่ใช้ port
sudo lsof -i :5001
sudo lsof -i :514

# Kill process
sudo kill -9 <PID>
```

### Permission Denied (Port 514)
```bash
# Option 1: Run with sudo
sudo python app_production.py

# Option 2: Change port
# Edit .env: SYSLOG_PORT=5140

# Option 3: Use setcap (Linux)
sudo setcap 'cap_net_bind_service=+ep' /path/to/python
```

### Database Connection Error
```bash
# Check database
sqlite3 cybersecurity.db ".tables"

# Reset database
rm cybersecurity.db
python init_db.py
```

### Docker Issues
```bash
# Remove all containers
docker-compose down -v

# Rebuild
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

---

## 📚 Additional Resources

- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Let's Encrypt](https://letsencrypt.org/)

---

**คำแนะนำ:**
- Development: ใช้ Python Direct
- Production (Small): ใช้ Gunicorn + Nginx
- Production (Large): ใช้ Docker + Load Balancer
