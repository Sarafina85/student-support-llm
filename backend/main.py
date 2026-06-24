# backend/main.py

import logging
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import APP_TITLE, APP_VERSION, LOG_FILE, BACKEND_HOST, BACKEND_PORT
from llm_client import ask_llm

#Logging Setup
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
def ask_question(request: QuestionRequest):
    question = request.question.strip()

    # Handle empty question
    if not question:
        logging.warning("Empty question received.")
        raise HTTPException(status_code=400, detail="Please enter a question.")

    logging.info(f"Question received: {question}")

    try:
        answer = ask_llm(question)
        logging.info(f"Answer generated: {answer[:100]}...")  # Log first 100 chars
        return {
            "question": question,
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