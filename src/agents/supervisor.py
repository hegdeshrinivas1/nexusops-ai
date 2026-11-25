"""
Supervisor / Orchestrator Agent.
Analyzes user intent, decomposes the prompt into sub-goals, and routes tasks to specialists.
"""

from typing import Dict, Any, List
from src.agents.state import AgentState
from src.agents.llm_client import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """Analyzes the user question and plans sub-tasks."""
    query = state["user_query"]
    trace = list(state.get("execution_trace", []))
    
    trace.append({
        "agent": "Supervisor Orchestrator",
        "action": "Decompose Query & Formulate Plan",
        "detail": f"Analyzing user intent: '{query}'"
    })

    llm = get_llm()
    plan: List[str] = []

    if llm:
        try:
            sys_msg = SystemMessage(content="""You are the Supervisor of an Enterprise Multi-Agent Data Analyst system.
Given a business question, break it down into 3 concise sub-tasks:
1. SQL Data Analysis (tables/metrics needed)
2. Policy/Document Vector Search (rules/guidelines needed)
3. Cross-domain Compliance Verification & Synthesis
Reply with the 3 numbered steps only.""")
            resp = llm.invoke([sys_msg, HumanMessage(content=query)])
            lines = [line.strip() for line in resp.content.split("\n") if line.strip() and line[0].isdigit()]
            plan = lines if len(lines) >= 2 else [
                "1. Query regional financial margins and sales contract discount distributions.",
                "2. Perform semantic vector search over enterprise discount policies and CFO memos.",
                "3. Reconcile contracts against discount policy thresholds and flag compliance violations."
            ]
        except Exception:
            plan = [
                "1. Query regional financials (Q3-2024) and inspect high-discount contracts.",
                "2. Perform vector search over corporate discount policy and Q3 CFO memorandum.",
                "3. Check for policy breaches (discounts > 20%), evaluate margin impact, and draft audit ticket."
            ]
    else:
        # High-precision deterministic planning
        plan = [
            "1. SQL Analysis: Retrieve Q3-2024 regional operating margins and sales contracts in North America.",
            "2. Vector Search: Retrieve Corporate Discount Policy (DOC-POL-2024-04) and Q3 CFO Memorandum.",
            "3. Compliance Verification: Check if contracts exceed 20% discount cap without Form EW-99 waiver, and draft audit ticket."
        ]

    trace.append({
        "agent": "Supervisor Orchestrator",
        "action": "Plan Finalized",
        "detail": " -> ".join(plan)
    })

    return {
        "plan": plan,
        "current_step": 1,
        "execution_trace": trace
    }
