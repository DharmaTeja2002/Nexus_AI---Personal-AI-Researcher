import streamlit as st
import requests
import os

# Configure the API URL (Localhost by default, but configurable for Render)
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Setup the page layout and title
st.set_page_config(page_title="Nexus AI", page_icon="🧠", layout="wide")

st.title("🧠 Nexus AI: Developer Copilot")
st.markdown("Your autonomous AI assistant for navigating the engineering ecosystem.")

# --- SIDEBAR: File Uploads ---
with st.sidebar:
    st.header("📂 Ingest Knowledge")
    st.markdown("Upload architecture PDFs, meeting audio, or code files to the Vector Memory Bank.")
    
    uploaded_file = st.file_uploader("Upload a file", type=["pdf", "png", "jpg", "jpeg", "txt", "mp3", "wav", "mp4"])
    
    if st.button("Upload to Nexus AI"):
        if uploaded_file is not None:
            with st.spinner("Processing and vectorizing..."):
                try:
                    # We send the file to our FastAPI backend using requests
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{API_URL}/upload", files=files)
                    
                    if response.status_code == 200:
                        st.success(f"✅ Successfully ingested {uploaded_file.name}!")
                    else:
                        st.error(f"❌ Error: {response.text}")
                except Exception as e:
                    st.error(f"❌ Failed to connect to backend: {e}")
        else:
            st.warning("Please select a file first.")

# --- MAIN AREA: Chat Interface ---
# Initialize the chat history in Streamlit's Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("Ask a technical question about the codebase..."):
    # 1. Display the user's question
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Add the question to the session state memory
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. Ask the FastAPI backend
    with st.chat_message("assistant"):
        with st.spinner("Searching the vector database..."):
            try:
                # Send the question to our FastAPI /ask endpoint
                payload = {"question": prompt}
                response = requests.post(f"{API_URL}/ask", json=payload)
                
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer found.")
                    st.markdown(answer)
                    # Add the AI's response to the session state memory
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Error from server: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
