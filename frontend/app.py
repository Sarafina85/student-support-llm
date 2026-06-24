# frontend/app.py

import streamlit as st
import requests

# ── Config ─────────────────────────────────────────────────
BACKEND_URL = "http://localhost:8000"

# ── Page Setup ─────────────────────────────────────────────
st.set_page_config(
    page_title="University Student Support Assistant",
    page_icon="🎓",
    layout="centered"
)

# ── Header ─────────────────────────────────────────────────
st.title("🎓 University Student Support Assistant")
st.markdown("Ask any question about university services and we'll help you.")
st.divider()

# ── Sidebar ────────────────────────────────────────────────
st.sidebar.title("📋 Topics I can help with")
st.sidebar.markdown("""
- 📚 Course Registration
- 📝 Examination Rules
- 📖 Library Services
- 💻 ICT Support
- 🏠 Hostel Application
- 💰 Fee Payment
- 📅 Academic Calendar
- 🎓 Student Conduct
""")

# ── Backend Status Check ────────────────────────────────────
try:
    health = requests.get(f"{BACKEND_URL}/health", timeout=5)
    if health.status_code == 200:
        st.sidebar.success("✅ System is online")
    else:
        st.sidebar.error("⚠️ Backend is not responding")
except:
    st.sidebar.error("❌ Cannot connect to backend")

# ── Chat History ────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display previous messages
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["question"])
    with st.chat_message("assistant"):
        st.write(chat["answer"])

# ── Input ───────────────────────────────────────────────────
question = st.chat_input("Type your question here...")

if question:
    # Validate input
    if not question.strip():
        st.warning("⚠️ Please enter a question before submitting.")
    else:
        # Show user question immediately
        with st.chat_message("user"):
            st.write(question)

        # Show loading spinner while waiting
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/ask",
                        json={"question": question},
                        timeout=60
                    )

                    if response.status_code == 200:
                        answer = response.json()["answer"]
                        st.write(answer)

                        # Save to chat history
                        st.session_state.chat_history.append({
                            "question": question,
                            "answer": answer
                        })

                    elif response.status_code == 400:
                        st.warning("⚠️ Please enter a valid question.")

                    elif response.status_code == 503:
                        st.error("❌ The AI model is not running. Please contact ICT support.")

                    elif response.status_code == 504:
                        st.error("⏱️ The request timed out. Please try again.")

                    else:
                        st.error("❌ Something went wrong. Please try again.")

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to the backend. Is it running?")

                except requests.exceptions.Timeout:
                    st.error("⏱️ The request took too long. Please try again.")

                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")