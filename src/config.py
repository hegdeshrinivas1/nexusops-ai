"""
Configuration settings for the Autonomous Enterprise Data Analyst & Operations Agent.
Supports OCI Generative AI, OpenAI, Groq, Ollama, and an intelligent offline mock mode.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "documents"
DB_PATH = DATA_DIR / "enterprise_data.db"
VECTOR_INDEX_PATH = DATA_DIR / "vector_index.json"

# LLM Provider Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Oracle Cloud Infrastructure (OCI) GenAI Configuration
OCI_CONFIG_PROFILE = os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")
OCI_COMPARTMENT_ID = os.getenv("OCI_COMPARTMENT_ID", "")
OCI_GENAI_ENDPOINT = os.getenv("OCI_GENAI_ENDPOINT", "")

# Oracle Database 23ai Configuration
ORACLE_23AI_ENABLED = os.getenv("ORACLE_23AI_ENABLED", "false").lower() == "true"
ORACLE_USER = os.getenv("ORACLE_USER", "admin")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "")
ORACLE_DSN = os.getenv("ORACLE_DSN", "localhost:1521/FREEPDB1")

# Guardrail & Compliance Thresholds
MAX_DISCOUNT_THRESHOLD_PCT = 20.0
MIN_OPERATING_MARGIN_PCT = 15.0
