# tests/test_api.py

import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

# Make sure Python can find the backend folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from main import app

# ── Tests ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_root():
    """Test the root endpoint returns a welcome message."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_health_check():
    """Test the /health endpoint returns ok status."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert "model" in data


@pytest.mark.asyncio
async def test_ask_empty_question():
    """Test that empty question returns 400 error."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/ask", json={"question": ""})
    assert response.status_code == 400
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_ask_valid_question():
    """Test that a valid question returns an answer."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/ask", json={"question": "How do I register for courses?"})
    
    # Either works (200) or model not running (503)
    assert response.status_code in [200, 503, 504]
    
    if response.status_code == 200:
        data = response.json()
        assert "question" in data
        assert "answer" in data
        assert "timestamp" in data


@pytest.mark.asyncio
async def test_ask_whitespace_question():
    """Test that whitespace-only question returns 400 error."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/ask", json={"question": "   "})
    assert response.status_code == 400
   