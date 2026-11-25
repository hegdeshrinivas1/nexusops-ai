"""
Agent State Definition for LangGraph.
Tracks inputs, plans, intermediate agent findings, execution traces, and human-in-the-loop flags.
"""

from typing import List, Dict, Any, Optional, TypedDict

class AgentState(TypedDict):
    user_query: str
    plan: List[str]
    current_step: int
    sql_query: Optional[str]
    sql_results: Optional[Dict[str, Any]]
    sql_error_reflection: Optional[str]
    doc_results: Optional[List[Dict[str, Any]]]
    oracle_23ai_vector_sql: Optional[str]
    compliance_violations: Optional[List[Dict[str, Any]]]
    audit_ticket: Optional[Dict[str, Any]]
    final_synthesis: Optional[str]
    needs_human_approval: bool
    human_approved: bool
    execution_trace: List[Dict[str, str]] # List of {"agent": str, "action": str, "detail": str}
