"""
LLM Client Adapter.
Seamlessly routes prompt requests to:
1. OpenAI (gpt-4o-mini / gpt-4o)
2. Groq (llama-3.3-70b)
3. OCI Generative AI Service (Cohere / Llama)
4. Offline Heuristic Engine (allows zero-config immediate execution for offline evaluation)
"""

import os
from typing import Optional
from src.config import (
    LLM_PROVIDER, 
    OPENAI_API_KEY, 
    OPENAI_MODEL, 
    GROQ_API_KEY, 
    GROQ_MODEL
)

def get_llm():
    """Returns a LangChain Chat Model or None if offline fallback is preferred."""
    provider = LLM_PROVIDER.lower()

    if provider == "openai" and OPENAI_API_KEY and not OPENAI_API_KEY.startswith("your_"):
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0.1)
        except Exception as e:
            print(f"[WARN] Failed to initialize OpenAI model: {e}")

    if provider == "groq" and GROQ_API_KEY and not GROQ_API_KEY.startswith("your_"):
        try:
            from langchain_groq import ChatGroq
            return ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY, temperature=0.1)
        except Exception as e:
            print(f"[WARN] Failed to initialize Groq model: {e}")

    return None
