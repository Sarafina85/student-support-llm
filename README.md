# 🎓 University Student Support Assistant

A self-hosted LLM application built for IS 365 - Practical Assignment.
This system allows university students to ask questions about university 
services using a locally hosted AI model.

---

## 📋 Requirements

- Python 3.10 or above
- Ollama installed on your machine
- llama3.2:1b model pulled via Ollama

---

## 🚀 Setup Instructions

### 1. Clone or download the project
```bash
cd student-support-llm
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
pip install pytest-asyncio
```

### 4. Install and start Ollama
Download Ollama from https://ollama.com and run:
```bash
ollama run llama3.2:1b
```

---

## ▶️ Running the Application

### Step 1 — Start Ollama (new terminal)
```bash
ollama serve
```

### Step 2 — Start the backend (new terminal)
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Step 3 — Start the frontend (new terminal)
```bash
cd frontend
streamlit run app.py
```

---

## 🧪 Running Tests
```bash
cd tests
pytest test_api.py -v
```

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message |
| `/health` | GET | Backend health check |
| `/ask` | POST | Submit a question |
| `/docs` | GET | Swagger UI documentation |

---

## 📁 Project Structure
student-support-llm/

├── backend/

│   ├── main.py          
│   ├── llm_client.py    
│   ├── config.py       
│   └── logs/
│       └── app.log      
├── frontend/
│   └── app.py          
├── tests/
│   └── test_api.py      
├── docs/
│   ├── screenshots/    
│   └── report.md        
├── requirements.txt
└── README.md

---

## ⚠️ Error Handling

| Situation | Behaviour |
|-----------|-----------|
| Backend not running | Frontend shows connection error |
| Model not running | Backend returns 503 error |
| Empty question | Returns 400 with clear message |
| Slow response | Frontend shows loading spinner |

---

## 👥 Group Members

- Member 1 — Name
- Member 2 — Name
- Member 3 — Name
- Member 4 — Name
- Member 5 — Name

---

## 📚 Tools Used

- FastAPI — Backend framework
- Uvicorn — Web server
- Ollama — Local LLM serving
- llama3.2:1b — AI model
- Streamlit — Frontend UI
- Pytest — API testing