# 📝 Changelog

All notable changes to this project will be documented in this file.

---

## [2.0.0] - 2024-11-15

### 🎉 Major Features Added

#### 🤖 Graylog AI Integration
- **AI-powered log analysis** - LLM วิเคราะห์ logs จาก Graylog โดยตรง
- **Threat detection** - ตรวจจับภัยคุกคามอัตโนมัติ
- **Security recommendations** - ให้คำแนะนำด้านความปลอดภัย
- **Thai language support** - ผลการวิเคราะห์เป็นภาษาไทย

**New Files:**
- `cybersecurity_demo/graylog_client.py` - Graylog API client
- `cybersecurity_demo/test_graylog_ai.py` - Testing script
- `GRAYLOG_AI_INTEGRATION.md` - Documentation

**Modified Files:**
- `cybersecurity_demo/ai_chat_unified.py` - Added `analyze_graylog_logs()` method
- `cybersecurity_demo/app.py` - Added `/api/graylog/ai-analyze` endpoint
- `cybersecurity_demo/templates/logs.html` - Added AI analysis button and modal

**API Endpoints:**
- `GET /api/graylog/ai-analyze` - AI log analysis
- `GET /api/graylog/analyze` - Statistical analysis
- `GET /api/graylog/security-events` - Security events

### ✨ Improvements

- **Better error handling** - Improved error messages and logging
- **Performance optimization** - Faster log retrieval and processing
- **UI enhancements** - Better modal display for analysis results
- **Documentation** - Comprehensive guides and examples

### 🔧 Technical Changes

- Added `prepare_logs_for_llm()` method in GraylogClient
- Implemented specialized security analysis prompt
- Added modal-based result display
- Improved log formatting for LLM consumption

---

## [1.5.0] - 2024-11-10

### Added
- **Exploit-DB Integration** - 1,275+ security research papers
- **Unified Vector Store** - Combined search across multiple databases
- **Enhanced RAG** - Better context retrieval

### Changed
- Upgraded to ChromaDB for vector storage
- Improved document processing pipeline
- Better embedding model (sentence-transformers)

---

## [1.0.0] - 2024-11-01

### Initial Release

#### Core Features
- **AI Chat with RAG** - Question answering from documents
- **VirusTotal Scanner** - Malware detection
- **Security Dashboard** - System monitoring
- **Log Management** - Real-time log viewing

#### Components
- Flask web application
- OpenRouter API integration
- Vector database (ChromaDB)
- Bootstrap 5 UI

---

## Upcoming Features

### [2.1.0] - Planned
- [ ] Real-time log streaming analysis
- [ ] Custom analysis prompts
- [ ] Historical log comparison
- [ ] Automated response actions
- [ ] PDF report generation
- [ ] Multi-language support

### [3.0.0] - Future
- [ ] Machine learning models for anomaly detection
- [ ] Integration with SIEM systems
- [ ] Advanced threat intelligence
- [ ] Automated incident response
- [ ] Mobile application

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 2.0.0 | 2024-11-15 | Graylog AI Integration |
| 1.5.0 | 2024-11-10 | Exploit-DB Integration |
| 1.0.0 | 2024-11-01 | Initial Release |

---

## Breaking Changes

### 2.0.0
- None - Backward compatible

### 1.5.0
- Changed vector store structure
- Requires database migration

---

## Migration Guide

### From 1.5.0 to 2.0.0

No migration needed. New features are additive.

**Optional:** Add Graylog configuration to `.env`:
```bash
GRAYLOG_HOST=your_host
GRAYLOG_PORT=9000
GRAYLOG_API_TOKEN=your_token
GRAYLOG_STREAM_NAME=FortiGate Syslog
```

---

## Contributors

### KDAI Team
1. **นายภูวิศ จารุรัตน์กิจ** (67056056) - Lead Developer & System Architect
2. **นายสิรภพ กิจเจริญรุ่งโรจน์** (67056078) - Full-Stack Developer
3. **นายสุทธิ ดิลกเลิศพลากร** (67056082) - Security Specialist & DevOps

### Community
- Bug reports and feature requests
- Testing and feedback

---

**Last Updated:** 2024-11-15
