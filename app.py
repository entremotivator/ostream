# app.py
import streamlit as st
import requests
import json
from datetime import datetime

# Configure page settings
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")

# Initialize session state for chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

def call_n8n_webhook(message):
    """Call n8n webhook with the user message"""
    n8n_webhook_url = "YOUR_N8N_WEBHOOK_URL"  # Replace with your n8n webhook URL
    
    payload = {
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(n8n_webhook_url, json=payload)
        return response.json()
    except Exception as e:
        st.error(f"Error calling n8n webhook: {str(e)}")
        return None

# UI Elements
st.title("🤖 AI Chatbot")
st.markdown("Chat with an AI powered by Llama 2")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Show assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        # Call n8n webhook and get response
        response = call_n8n_webhook(prompt)
        
        if response:
            message_placeholder.markdown(response["response"])
            st.session_state.messages.append({"role": "assistant", "content": response["response"]})
        else:
            message_placeholder.markdown("Sorry, I encountered an error. Please try again.")

# Add sidebar with chat settings
with st.sidebar:
    st.header("Chat Settings")
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    max_length = st.slider("Max Response Length", min_value=100, max_value=2000, value=500, step=100)
