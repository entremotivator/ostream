# app.py
import streamlit as st
import requests
import json
from datetime import datetime
import time
from typing import List, Dict
import os
from utils import (
    initialize_session_state,
    save_chat_history,
    load_chat_history,
    format_message,
    generate_chat_id
)

# Configure Streamlit page
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
config = AppConfig()

def init_css():
    """Initialize custom CSS styles"""
    st.markdown("""
        <style>
        .chat-message {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
        }
        .user-message {
            background-color: #e6f3ff;
        }
        .assistant-message {
            background-color: #f0f2f6;
        }
        .message-timestamp {
            font-size: 0.8rem;
            color: #666;
        }
        .sidebar-content {
            padding: 1rem;
        }
        .export-button {
            margin-top: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

def call_n8n_webhook(message: str, chat_history: List[Dict], system_prompt: str = None) -> Dict:
    """
    Call n8n webhook with the user message and chat history
    """
    n8n_webhook_url = "https://agentonline-u29564.vm.elestio.app/webhook-test/chat"
    
    # Prepare the messages including system prompt and history
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # Add relevant chat history (last 10 messages)
    for msg in chat_history[-10:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add the current message
    messages.append({"role": "user", "content": message})
    
    payload = {
        "messages": messages,
        "temperature": st.session_state.temperature,
        "max_tokens": st.session_state.max_tokens,
        "top_p": st.session_state.top_p,
        "frequency_penalty": st.session_state.frequency_penalty,
        "presence_penalty": st.session_state.presence_penalty,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            n8n_webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling API: {str(e)}")
        return None

def display_messages():
    """Display chat messages with formatting"""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(format_message(msg["content"]))
            st.markdown(f"<div class='message-timestamp'>{msg['timestamp']}</div>",
                      unsafe_allow_html=True)

def handle_file_upload():
    """Handle file upload and context extraction"""
    uploaded_file = st.sidebar.file_uploader(
        "Upload a file for context",
        type=["txt", "pdf", "docx"]
    )
    if uploaded_file:
        try:
            # For simplicity, we'll just read text files
            # You can add PDF and DOCX support using appropriate libraries
            content = uploaded_file.read().decode()
            st.session_state.context = content
            st.sidebar.success("File uploaded and context extracted!")
        except Exception as e:
            st.sidebar.error(f"Error processing file: {str(e)}")

def create_sidebar():
    """Create sidebar with chat settings and controls"""
    with st.sidebar:
        st.header("📊 Chat Settings")
        
        # Model parameters
        st.subheader("Model Parameters")
        st.session_state.temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher values make output more random, lower values more deterministic"
        )
        
        st.session_state.max_tokens = st.slider(
            "Max Tokens",
            min_value=100,
            max_value=4000,
            value=2000,
            step=100,
            help="Maximum number of tokens in the response"
        )
        
        st.session_state.top_p = st.slider(
            "Top P",
            min_value=0.0,
            max_value=1.0,
            value=0.9,
            step=0.1,
            help="Nucleus sampling parameter"
        )
        
        st.session_state.frequency_penalty = st.slider(
            "Frequency Penalty",
            min_value=0.0,
            max_value=2.0,
            value=0.0,
            step=0.1,
            help="Penalize frequent tokens"
        )
        
        st.session_state.presence_penalty = st.slider(
            "Presence Penalty",
            min_value=0.0,
            max_value=2.0,
            value=0.0,
            step=0.1,
            help="Penalize tokens already present"
        )
        
        # System prompt
        st.subheader("System Prompt")
        st.session_state.system_prompt = st.text_area(
            "Custom system prompt",
            value=st.session_state.system_prompt,
            height=100
        )
        
        # Chat management
        st.subheader("Chat Management")
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.session_state.chat_id = generate_chat_id()
            st.success("Chat history cleared!")
        
        if st.button("Export Chat"):
            chat_data = {
                "chat_id": st.session_state.chat_id,
                "messages": st.session_state.messages,
                "settings": {
                    "temperature": st.session_state.temperature,
                    "max_tokens": st.session_state.max_tokens,
                    "top_p": st.session_state.top_p,
                    "system_prompt": st.session_state.system_prompt
                }
            }
            save_chat_history(chat_data)
            st.success("Chat exported successfully!")

def main():
    # Initialize session state and CSS
    initialize_session_state()
    init_css()
    
    # Create sidebar
    create_sidebar()
    
    # Main chat interface
    st.title("🤖 Advanced AI Chat Assistant")
    st.markdown("Powered by Llama 2 - Enhanced with advanced features and context awareness")
    
    # Handle file upload for context
    handle_file_upload()
    
    # Display chat messages
    display_messages()
    
    # Chat input
    if prompt := st.chat_input("What would you like to discuss?"):
        # Add user message
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🤔 Thinking...")
            
            # Include context if available
            full_prompt = prompt
            if st.session_state.context:
                full_prompt = f"Context: {st.session_state.context}\n\nQuestion: {prompt}"
            
            # Call API
            response = call_n8n_webhook(
                full_prompt,
                st.session_state.messages,
                st.session_state.system_prompt
            )
            
            if response and "response" in response:
                assistant_message = {
                    "role": "assistant",
                    "content": response["response"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                message_placeholder.markdown(format_message(response["response"]))
                st.session_state.messages.append(assistant_message)
            else:
                message_placeholder.markdown("❌ Sorry, I encountered an error. Please try again.")

if __name__ == "__main__":
    main()
