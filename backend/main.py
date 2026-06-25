# backend/main.py

import logging
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import APP_TITLE, APP_VERSION, LOG_FILE, BACKEND_HOST, BACKEND_PORT
from llm_client import ask_llm
import json
from fastapi.security import APIKeyHeader
from fastapi import Security
from fastapi import File, UploadFile

#Logging Setup
# ── API Key Security ───────────────────────────────────────
from config import API_KEY

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key."
        )
    return key
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# FastAPI App 
app = FastAPI(title=APP_TITLE, version=APP_VERSION)

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Request Model
class QuestionRequest(BaseModel):
    question: str

# Endpoints 

@app.get("/")
def root():
    return {"message": f"Welcome to {APP_TITLE}"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "model": "llama3.2:1b"
    }


@app.post("/ask")
def ask_question(request: QuestionRequest, key: str = Security(api_key_header)):
    verify_api_key(key)
    
    # Handle empty question
    if not request.question:
        logging.warning("Empty question received.")
        raise HTTPException(status_code=400, detail="Please enter a question.")

    logging.info(f"Question received: {request.question}")

    try:
        answer = ask_llm(request.question)
        logging.info(f"Answer generated: {answer[:100]}...")  # Log first 100 chars
        return {
            "question": request.question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        }

    except ConnectionError as e:
        logging.error(f"Connection error: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))

    except TimeoutError as e:
        logging.error(f"Timeout error: {str(e)}")
        raise HTTPException(status_code=504, detail=str(e))

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


#  Run 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=BACKEND_HOST, port=BACKEND_PORT, reload=True)

    
    
# Feedback Model 
class FeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: str  # Good, Average, Poor

@app.post("/feedback")
def submit_feedback(feedback: FeedbackRequest, key: str = Security(api_key_header)):
    verify_api_key(key)
    # ... rest of the code stays the same
    # Save feedback to file
    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": feedback.question,
        "answer": feedback.answer[:100],
        "rating": feedback.rating
    }
    
    feedback_file = os.path.join(os.path.dirname(LOG_FILE), "feedback.json")
    
    # Load existing feedback
    if os.path.exists(feedback_file):
        with open(feedback_file, "r") as f:
            all_feedback = json.load(f)
    else:
        all_feedback = []
    
    all_feedback.append(feedback_entry)
    
    with open(feedback_file, "w") as f:
        json.dump(all_feedback, f, indent=2)
    
    logging.info(f"Feedback received: {feedback.rating} for question: {feedback.question[:50]}")
    
    return {"message": "Thank you for your feedback!"}

#  File Upload Endpoint 

@app.post("/ask-from-file")
async def ask_from_file(
    file: UploadFile = File(...),
    question: str = "",
    key: str = Security(api_key_header)
):
    verify_api_key(key)

    # Validate file type
    if not file.filename or not file.filename.endswith((".txt", ".md")):
        raise HTTPException(
            status_code=400,
            detail="Only .txt and .md files are supported."
        )

    # Validate question
    if not question.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a question about the file."
        )

    # Read file content
    content = await file.read()
    file_text = content.decode("utf-8")

    # Limit file size
    if len(file_text) > 5000:
        file_text = file_text[:5000] + "...[truncated]"

    logging.info(f"File uploaded: {file.filename}, Question: {question}")

    # Build prompt
    prompt = f"""
The following is the content of an uploaded document:

{file_text}

Based on the document above, please answer this question:
{question}

If the answer is not found in the document, say so clearly.
"""

    try:
        answer = ask_llm(prompt)
        logging.info(f"File-based answer generated for: {question[:50]}")
        return {
            "filename": file.filename,
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        }

    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))

    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")