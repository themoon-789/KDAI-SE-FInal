# 🎯 เริ่มต้นที่นี่!

## ✨ ระบบพร้อมใช้งานแล้ว!

ระบบ **Advance Agent for Cybersecurity** กำลังทำงานอยู่ที่:

### 🌐 เปิดเบราว์เซอร์และไปที่:

```
📊 Dashboard (Real-time)
👉 http://localhost:5001

📚 Knowledge Base (อัปโหลดเอกสาร)
👉 http://localhost:5001/knowledge

📝 Logs (ดู Syslog)
👉 http://localhost:5001/logs

🤖 Agents (ตั้งค่า Agents)
👉 http://localhost:5001/agents

🤖 AI Chat (ถามตอบกับ AI) ⭐ NEW!
👉 http://localhost:5001/chat
```

## 🎮 ทดลองใช้งานด่วน (3 นาที)

### 1️⃣ ดู Dashboard (30 วินาที)
1. เปิด http://localhost:5001
2. ดูสถิติที่อัปเดตแบบ Real-time
3. สังเกต Logs ใหม่ที่เพิ่มขึ้นทุก 5 วินาที

### 2️⃣ อัปโหลดเอกสาร (1 นาที)
1. ไปที่ http://localhost:5001/knowledge
2. คลิก "เลือกไฟล์เอกสาร"
3. เลือกไฟล์ใดๆ (หรือใช้ `sample_documents/threat_report_example.txt`)
4. คลิก "อัปโหลดเอกสาร"
5. ✅ เอกสารจะปรากฏในตาราง!

### 3️⃣ ตั้งค่า Agent (1 นาที)
1. ไปที่ http://localhost:5001/agents
2. คลิกที่ "Router-Agent-01" (สถานะ Inactive)
3. เลือก Protocol: UDP
4. พอร์ต: 514
5. คลิก "บันทึกการตั้งค่า"
6. ✅ Agent จะเปลี่ยนเป็น Active!

### 4️⃣ ดู Logs (30 วินาที)
1. ไปที่ http://localhost:5001/logs
2. ลองกรองตามระดับ: CRITICAL
3. ลองค้นหา: "firewall"
4. ✅ ดูสถิติที่อัปเดต!

## 📚 เอกสารเพิ่มเติม

- 📖 **QUICK_START.md** - คู่มือเริ่มต้นใช้งาน
- 📘 **DEMO_GUIDE.md** - คู่มือโดยละเอียด
- 📸 **SCREENSHOTS.md** - ภาพหน้าจอ
- ✅ **TEST_RESULTS.md** - ผลการทดสอบ
- 📋 **PROJECT_SUMMARY.md** - สรุปโครงการ

## 🎯 Use Cases ที่ Demo

### UC-ADM-01: นำเข้าเอกสาร ✅
- อัปโหลด PDF, DOCX
- แปลงเป็น Vector Embedding
- จัดเก็บใน Vector Database

### UC-ADM-02: ตั้งค่าการรับข้อมูล Log ✅
- ตั้งค่า Agents
- เลือก Protocol (UDP/TCP)
- กำหนดพอร์ต

### UC-ADM-03: ดู Dashboard แบบ Real-time ✅
- สถิติระบบ
- Real-time Logs
- สถานะ Agents
- System Health

## 🛑 หยุดระบบ

กด `Ctrl+C` ใน terminal

## 💡 Tips

- 🔄 Dashboard อัปเดตอัตโนมัติทุก 5 นาที
- 📝 Logs ใหม่จะปรากฏทุก 5 วินาที
- 🎨 UI รองรับ Dark/Light mode ตามระบบ
- 📱 ใช้งานได้บนมือถือ

## 🎓 สมาชิกโครงการ

1. นายภูวิศ จารุรัตน์กิจ (67056056)
2. นายสิรภพ กิจเจริญรุ่งโรจน์ (67056078)
3. นายสุทธิ ดิลกเลิศพลากร (67056082)

---

## 🎉 สนุกกับการทดสอบ!

มีคำถาม? อ่านเอกสารเพิ่มเติมใน `DEMO_GUIDE.md`
