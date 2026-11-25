"""
Unstructured Document Specialist Agent.
Implements Vector Search over enterprise documents (Policies, CFO Memos, SOPs).
Simulates Oracle Database 23ai AI Vector Search and outputs the corresponding 23ai SQL syntax.
"""

from typing import Dict, Any
from src.agents.state import AgentState
from src.tools.doc_tools import search_enterprise_knowledge, get_oracle_23ai_vector_syntax

def doc_specialist_node(state: AgentState) -> Dict[str, Any]:
    trace = list(state.get("execution_trace", []))
    query = state["user_query"]

    # Perform Hybrid Semantic Vector Search
    search_query = f"{query} discount policy operating margin compliance threshold waiver"
    vector_results = search_enterprise_knowledge(search_query, top_k=3)
    
    # Generate the equivalent Oracle 23ai VECTOR_DISTANCE SQL syntax
    oracle_sql = get_oracle_23ai_vector_syntax("discount compliance threshold operating margin", top_k=3)

    trace.append({
        "agent": "Document Specialist",
        "action": "Vector Search Executed (Oracle 23ai Simulation)",
        "detail": f"Retrieved {len(vector_results)} relevant document chunks (Top match: '{vector_results[0]['title'] if vector_results else 'None'}' with score {vector_results[0]['similarity_score'] if vector_results else 0.0})."
    })

    trace.append({
        "agent": "Document Specialist",
        "action": "Oracle 23ai Vector Query Formulated",
        "detail": oracle_sql
    })

    return {
        "doc_results": vector_results,
        "oracle_23ai_vector_sql": oracle_sql,
        "execution_trace": trace
    }
