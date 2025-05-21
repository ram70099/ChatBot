import streamlit as st
import google.generativeai as genai
import json
import os
from datetime import datetime

HISTORY_FILE = "chat_history.json"

# Load API key
@st.cache_resource
def load_api_key(filename="gemini_api_key.txt"):
    if not os.path.exists(filename):
        st.error(f"API key file '{filename}' not found.")
        st.stop()
    with open(filename, "r") as f:
        return f.read().strip()

# Load and save history
def load_chat_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_chat_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

# Build conversation context for Gemini
def build_prompt_from_history(history, new_user_input):
    context = ""
    for entry in history:
        context += f"User: {entry['user']}\nAI: {entry['ai']}\n"
    context += f"User: {new_user_input}\nAI:"
    return context

# Generate Gemini response
def generate_gemini_response(prompt, model):
    try:
        response = model.generate_content(prompt)
        return response.text if hasattr(response, 'text') else str(response)
    except Exception as e:
        return f"❌ Error generating response: {str(e)}"

# Main Streamlit app
def main():
    st.set_page_config(page_title="Gemini Terminal Chat", layout="centered")
    st.markdown("""
    <style>
        .main {
            background-color: #1a1a2e;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .stTextInput>div>div>input {
            font-size: 18px;
            border-radius: 8px;
            padding: 10px;
            background-color: #262626;
            color: white;
        }
        .stButton>button {
            font-size: 18px;
            background-color: #6c63ff;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #4e4bd1;
        }
        .chat-container {
            max-height: 500px;
            overflow-y: auto;
            padding-right: 10px;
        }
        .chat-bubble-user {
            background-color: #2e2e2e;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 10px;
            color: white;
        }
        .chat-bubble-ai {
            background-color: #4040a1;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 20px;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("🌟 Gemini Terminal Chat (with Memory)")
    api_key = load_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-1.5-flash")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = load_chat_history()

    with st.container():
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        for entry in st.session_state.chat_history:
            st.markdown(f"<div class='chat-bubble-user'>👤 You: {entry['user']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='chat-bubble-ai'>🤖 Gemini: {entry['ai']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.form("chat_form"):
        user_input = st.text_input("💬 Type your message:", placeholder="Ask me anything...", key="user_input")
        submitted = st.form_submit_button("Send")

        if submitted and user_input.strip():
            prompt = build_prompt_from_history(st.session_state.chat_history, user_input)
            ai_response = generate_gemini_response(prompt, model)

            st.session_state.chat_history.append({"user": user_input, "ai": ai_response})
            save_chat_history(st.session_state.chat_history)
            st.rerun()

if __name__ == "__main__":
    main()
