# backend/llm_client.py

import requests
import logging
from config import OLLAMA_URL, MODEL_NAME, SYSTEM_PROMPT

def ask_llm(question: str) -> str:
    """
    Sends a question to the local Ollama LLM and returns the response.
    """
    
    # Build the full prompt
    full_prompt = f"{SYSTEM_PROMPT}\n\nStudent Question: {question}"
    
    # Build the request payload
    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False  # We want the full response at once, not streamed
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()  # Raises error if status is not 200
        
        data = response.json()
        return data.get("response", "Sorry, I could not generate a response.")
    
    except requests.exceptions.ConnectionError:
        logging.error("Could not connect to Ollama. Is it running?")
        raise ConnectionError("The AI model is not running. Please contact ICT support.")
    
    except requests.exceptions.Timeout:
        logging.error("Ollama request timed out.")
        raise TimeoutError("The request took too long. Please try again.")
    
    except Exception as e:
        logging.error(f"Unexpected error when calling LLM: {str(e)}")
        raise RuntimeError(f"Unexpected error: {str(e)}")