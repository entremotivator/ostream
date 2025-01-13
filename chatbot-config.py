# config.py
import os
from dataclasses import dataclass

@dataclass
class AppConfig:
    """Application configuration"""
    N8N_WEBHOOK_URL: str = "https://agentonline-u29564.vm.elestio.app/webhook-test/chat"
    DEFAULT_SYSTEM_PROMPT: str = """You are a helpful AI assistant. Please provide clear, 
    accurate, and engaging responses while maintaining a professional and friendly tone."""
    MAX_HISTORY_LENGTH: int = 100
    CHAT_EXPORT_PATH: str = "chat_exports"

# utils.py
import streamlit as st
import json
import uuid
from datetime import datetime
import os
from typing import Dict
import re

def generate_chat_id() -> str:
    """Generate a unique chat ID"""
    return str(uuid.uuid4())

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'chat_id' not in st.session_state:
        st.session_state.chat_id = generate_chat_id()
    if 'context' not in st.session_state:
        st.session_state.context = None
    if 'system_prompt' not in st.session_state:
        st.session_state.system_prompt = AppConfig.DEFAULT_SYSTEM_PROMPT

def format_message(content: str) -> str:
    """Format message content with markdown and syntax highlighting"""
    # Convert code blocks
    content = re.sub(
        r'```(\w+)?\n(.*?)\n```',
        lambda m: f'```{m.group(1) or ""}\n{m.group(2)}\n```',
        content,
        flags=re.DOTALL
    )
    
    # Convert inline code
    content = re.sub(r'`(.*?)`', r'`\1`', content)
    
    return content

def save_chat_history(chat_data: Dict):
    """Save chat history to file"""
    os.makedirs(AppConfig.CHAT_EXPORT_PATH, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_{chat_data['chat_id']}_{timestamp}.json"
    filepath = os.path.join(AppConfig.CHAT_EXPORT_PATH, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(chat_data, f, indent=2, ensure_ascii=False)

def load_chat_history(filepath: str) -> Dict:
    """Load chat history from file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
