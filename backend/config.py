# backend/config.py

APP_TITLE = "University Student Support Assistant"
APP_VERSION = "1.0.0"

# Ollama settings
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"

# Backend settings
BACKEND_HOST = "0.0.0.0"
BACKEND_PORT = 8000

# Logging
LOG_FILE = "backend/logs/app.log"

# System prompt — tells the LLM how to behave
SYSTEM_PROMPT = """
You are a helpful University Student Support Assistant.
You help students with questions about:
- Course registration
- Examination rules
- Library services
- ICT support
- Hostel application
- Fee payment
- Academic calendar
- Student conduct

Always be polite, clear, and concise.
If you do not know the answer, advise the student to visit the relevant university office.
"""