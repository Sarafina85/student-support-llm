# frontend/app.py
API_KEY = "university-support-2026"
HEADERS = {"X-API-Key": API_KEY}
import streamlit as st
import requests

#  Config
BACKEND_URL = "http://localhost:8000"

#  Page Setup 
st.set_page_config(
    page_title="University Student Support Assistant",
    page_icon="🎓",
    layout="centered"
)

#  Header 
st.title("🎓 University Student Support Assistant")
st.markdown("Ask any question about university services and we'll help you.")
st.divider()
# File Upload Section 
st.subheader("📄 Ask a Question from a Document")
uploaded_file = st.file_uploader(
    "Upload a .txt or .md file",
    type=["txt", "md"]
)

if uploaded_file is not None:
    file_question = st.text_input(
        "What would you like to know from this document?",
        key="file_question"
    )

    if st.button("Ask from Document"):
        if not file_question.strip():
            st.warning("⚠️ Please enter a question about the document.")
        else:
            with st.spinner("Reading document and thinking..."):
                try:
                    file_response = requests.post(
                        f"{BACKEND_URL}/ask-from-file",
                        files={"file": (uploaded_file.name, uploaded_file, "text/plain")},
                        data={"question": file_question},
                        headers=HEADERS,
                        timeout=120
                    )

                    if file_response.status_code == 200:
                        file_data = file_response.json()
                        st.success("Answer from document:")
                        st.write(file_data["answer"])

                    elif file_response.status_code == 400:
                        st.warning("⚠️ " + file_response.json()["detail"])

                    elif file_response.status_code == 503:
                        st.error("❌ The AI model is not running.")

                    else:
                        st.error("❌ Something went wrong. Please try again.")

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to the backend.")

                except requests.exceptions.Timeout:
                    st.error("⏱️ The request took too long. Please try again.")

st.divider()
# Sidebar 
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

# Backend Status Check 
try:
    health = requests.get(f"{BACKEND_URL}/health", headers=HEADERS, timeout=5)
    if health.status_code == 200:
        st.sidebar.success("✅ System is online")
    else:
        st.sidebar.error("⚠️ Backend is not responding")
except requests.exceptions.RequestException:
    st.sidebar.error("❌ Cannot connect to backend")

# Chat History 
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display previous messages
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["question"])
    with st.chat_message("assistant"):
        st.write(chat["answer"])

# Input 
question = st.chat_input("Type your question here...")

if question:
    if not question.strip():
        st.warning("⚠️ Please enter a question before submitting.")
    else:
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = None
                status_code = None
                answer = None

                try:
                    response = requests.post(
                        f"{BACKEND_URL}/ask",
                        json={"question": question},
                        headers=HEADERS,
                        timeout=120,
                    )
                    status_code = response.status_code
                    response.raise_for_status()

                    data = response.json()
                    answer = data.get("answer", "Sorry, I could not generate a response.")
                    st.write(answer)

                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer,
                    })

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to the backend. Is it running?")

                except requests.exceptions.Timeout:
                    st.error("⏱️ The request took too long. Please try again.")

                except requests.exceptions.HTTPError:
                    if status_code == 400:
                        st.warning("⚠️ Please enter a valid question.")
                    elif status_code == 503:
                        st.error("❌ The AI model is not running. Please contact ICT support.")
                    elif status_code == 504:
                        st.error("⏱️ The request timed out. Please try again.")
                    else:
                        st.error("❌ Something went wrong. Please try again.")

                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")

        # ── Rating Buttons (only shown if answer was received) ──
        if answer:
            st.write("**Was this answer helpful?**")
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("👍 Good", key=f"good_{len(st.session_state.chat_history)}"):
                    requests.post(
                        f"{BACKEND_URL}/feedback",
                        json={
                            "question": question,
                            "answer": answer,
                            "rating": "Good"
                        },
                        headers=HEADERS,
                        timeout=10,
                    )
                    st.success("Thanks for your feedback!")

            with col2:
                if st.button("😐 Average", key=f"avg_{len(st.session_state.chat_history)}"):
                    requests.post(
                        f"{BACKEND_URL}/feedback",
                        json={
                            "question": question,
                            "answer": answer,
                            "rating": "Average"
                        },
                        headers=HEADERS,
                        timeout=10,
                    )
                    st.success("Thanks for your feedback!")

            with col3:
                if st.button("👎 Poor", key=f"poor_{len(st.session_state.chat_history)}"):
                    requests.post(
                        f"{BACKEND_URL}/feedback",
                        json={
                            "question": question,
                            "answer": answer,
                            "rating": "Poor"
                        },
                        headers=HEADERS,
                        timeout=10,
                    )
                    st.success("Thanks for your feedback!")