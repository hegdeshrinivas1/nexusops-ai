"""
Document & Policy Tools for the Document Specialist Agent.
Implements Vector Search over unstructured corporate documents, policies, and executive memos.
"""

from typing import List, Dict, Any, Optional
from src.db.vector_store import VectorStore
from src.config import VECTOR_INDEX_PATH

_vector_store = VectorStore()
if VECTOR_INDEX_PATH.exists():
    _vector_store.load(VECTOR_INDEX_PATH)

def search_enterprise_knowledge(
    query: str, 
    top_k: int = 3, 
    doc_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Performs hybrid semantic search over corporate policies, CFO memos, and audit SOPs.
    Returns the most relevant chunks with similarity scores and document titles.
    """
    return _vector_store.hybrid_search(query=query, top_k=top_k, doc_type_filter=doc_type)

def get_oracle_23ai_vector_syntax(query: str, top_k: int = 3) -> str:
    """Returns the Oracle Database 23ai AI Vector Search SQL equivalent."""
    return _vector_store.generate_oracle_23ai_vector_sql(query, top_k=top_k)

def get_vector_store() -> VectorStore:
    return _vector_store
