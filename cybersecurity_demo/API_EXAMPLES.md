# 🔌 API Examples

ตัวอย่างการใช้งาน API ทั้งหมด

---

## 🔐 Authentication

### Login
```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@cybersecurity.local",
    "role": "admin",
    "is_active": true
  }
}
```

### Get Current User
```bash
curl http://localhost:5001/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📚 Documents (Knowledge Base)

### List Documents
```bash
curl http://localhost:5001/api/documents \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "filename": "security_guide.pdf",
    "file_type": ".pdf",
    "file_size": 1024000,
    "status": "processed",
    "uploaded_by": "admin",
    "uploaded_at": "2024-01-15T10:30:00",
    "processed_at": "2024-01-15T10:30:15",
    "chunk_count": 45
  }
]
```

### Upload Document
```bash
curl -X POST http://localhost:5001/api/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/document.pdf"
```

**Response:**
```json
{
  "success": true,
  "message": "Document processed successfully",
  "document": {
    "id": 2,
    "filename": "document.pdf",
    "status": "processed",
    "chunk_count": 30
  }
}
```

### Delete Document
```bash
curl -X DELETE http://localhost:5001/api/documents/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📝 Security Logs

### Get Logs (Paginated)
```bash
# Get first page
curl "http://localhost:5001/api/logs?page=1&per_page=50" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by severity
curl "http://localhost:5001/api/logs?severity=CRITICAL" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "logs": [
    {
      "id": 1,
      "timestamp": "2024-01-15T10:30:00",
      "source_ip": "192.168.1.100",
      "source_host": "firewall-01",
      "severity": "CRITICAL",
      "message": "Firewall blocked suspicious traffic",
      "agent": "Firewall-01",
      "threat_level": "high",
      "is_analyzed": false
    }
  ],
  "total": 150,
  "pages": 3,
  "current_page": 1
}
```

### Analyze Log with AI
```bash
curl -X POST http://localhost:5001/api/logs/1/analyze \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "is_suspicious": true,
    "analysis": "This log indicates a potential DDoS attack...",
    "sources": [
      {
        "content": "DDoS attacks are...",
        "metadata": {
          "filename": "security_guide.pdf"
        }
      }
    ]
  }
}
```

---

## 🤖 Agents

### List Agents
```bash
curl http://localhost:5001/api/agents \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Firewall-01",
    "type": "firewall",
    "ip": "192.168.1.10",
    "hostname": "fw01.local",
    "status": "active",
    "protocol": "UDP",
    "port": 514,
    "last_seen": "2024-01-15T10:30:00"
  }
]
```

### Create Agent
```bash
curl -X POST http://localhost:5001/api/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Router-02",
    "type": "router",
    "ip": "192.168.1.2",
    "hostname": "router02.local",
    "protocol": "UDP",
    "port": 514
  }'
```

### Update Agent
```bash
curl -X PUT http://localhost:5001/api/agents/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Firewall-01-Updated",
    "status": "active"
  }'
```

---

## 💬 AI Chat

### Chat with AI (with RAG)
```bash
curl -X POST http://localhost:5001/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is a DDoS attack and how to prevent it?",
    "use_rag": true
  }'
```

**Response:**
```json
{
  "success": true,
  "response": "A DDoS (Distributed Denial of Service) attack is...",
  "sources": [
    {
      "content": "DDoS attacks overwhelm systems...",
      "metadata": {
        "filename": "security_guide.pdf",
        "chunk_index": 5
      },
      "distance": 0.23
    }
  ],
  "model": "google/gemini-2.0-flash-exp:free"
}
```

### Chat without RAG
```bash
curl -X POST http://localhost:5001/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain SQL injection",
    "use_rag": false
  }'
```

### Get Chat History
```bash
curl "http://localhost:5001/api/chat/history?limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "user": "admin",
    "message": "What is DDoS?",
    "response": "A DDoS attack is...",
    "model": "google/gemini-2.0-flash-exp:free",
    "timestamp": "2024-01-15T10:30:00"
  }
]
```

---

## 📊 Statistics

### Get System Stats
```bash
curl http://localhost:5001/api/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "total_documents": 5,
  "total_logs": 1523,
  "active_agents": 3,
  "total_agents": 5,
  "critical_logs": 12,
  "unanalyzed_logs": 45,
  "vector_store": {
    "total_chunks": 234,
    "collection_name": "cybersecurity_docs"
  }
}
```

---

## 🐍 Python Examples

### Using requests library

```python
import requests

BASE_URL = "http://localhost:5001"

# Login
def login(username, password):
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": username, "password": password}
    )
    return response.json()["access_token"]

# Get token
token = login("admin", "admin123")
headers = {"Authorization": f"Bearer {token}"}

# Upload document
def upload_document(filepath):
    with open(filepath, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            f"{BASE_URL}/api/documents/upload",
            headers=headers,
            files=files
        )
    return response.json()

# Chat with AI
def chat(message, use_rag=True):
    response = requests.post(
        f"{BASE_URL}/api/chat",
        headers=headers,
        json={"message": message, "use_rag": use_rag}
    )
    return response.json()

# Get logs
def get_logs(severity=None):
    params = {"severity": severity} if severity else {}
    response = requests.get(
        f"{BASE_URL}/api/logs",
        headers=headers,
        params=params
    )
    return response.json()

# Example usage
print("Uploading document...")
result = upload_document("security_guide.pdf")
print(f"Document uploaded: {result}")

print("\nChatting with AI...")
response = chat("What is ransomware?")
print(f"AI Response: {response['response']}")

print("\nGetting critical logs...")
logs = get_logs(severity="CRITICAL")
print(f"Found {len(logs['logs'])} critical logs")
```

---

## 🌐 JavaScript/Node.js Examples

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5001';
let token = '';

// Login
async function login(username, password) {
  const response = await axios.post(`${BASE_URL}/api/auth/login`, {
    username,
    password
  });
  token = response.data.access_token;
  return token;
}

// Upload document
async function uploadDocument(filepath) {
  const FormData = require('form-data');
  const fs = require('fs');
  
  const form = new FormData();
  form.append('file', fs.createReadStream(filepath));
  
  const response = await axios.post(
    `${BASE_URL}/api/documents/upload`,
    form,
    {
      headers: {
        ...form.getHeaders(),
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  return response.data;
}

// Chat with AI
async function chat(message, useRag = true) {
  const response = await axios.post(
    `${BASE_URL}/api/chat`,
    { message, use_rag: useRag },
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  return response.data;
}

// Get stats
async function getStats() {
  const response = await axios.get(
    `${BASE_URL}/api/stats`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  return response.data;
}

// Example usage
(async () => {
  await login('admin', 'admin123');
  
  const stats = await getStats();
  console.log('System stats:', stats);
  
  const chatResponse = await chat('What is phishing?');
  console.log('AI Response:', chatResponse.response);
})();
```

---

## 🔒 Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/api/auth/login` | 5 per minute |
| `/api/documents/upload` | 10 per hour |
| `/api/chat` | 30 per hour |
| `/api/logs/<id>/analyze` | 20 per hour |
| Other endpoints | 100 per hour |

---

## ⚠️ Error Responses

### 401 Unauthorized
```json
{
  "error": "Authentication required",
  "message": "Token has expired"
}
```

### 403 Forbidden
```json
{
  "error": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "error": "Document not found"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later."
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to process document",
  "message": "Error reading PDF: ..."
}
```

---

## 🧪 Testing with Postman

1. Import collection (create from examples above)
2. Set environment variable: `BASE_URL = http://localhost:5001`
3. Login to get token
4. Set token in Authorization header
5. Test all endpoints

---

## 📝 Notes

- All endpoints (except login) require JWT token
- Token expires after 1 hour
- Use refresh token to get new access token
- File uploads limited to 50MB
- Supported file types: PDF, DOCX, TXT, JSON

---

**Happy API Testing!** 🚀
