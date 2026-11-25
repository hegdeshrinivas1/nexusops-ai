"""
LangGraph Multi-Agent Workflow Definition.
Wires the Supervisor, SQL Analyst (ReAct), Document Specialist (Vector Search), 
and Compliance Critic (HITL) into a compiled state graph.
"""

from langgraph.graph import StateGraph, START, END
from src.agents.state import AgentState
from src.agents.supervisor import supervisor_node
from src.agents.sql_analyst import sql_analyst_node
from src.agents.doc_specialist import doc_specialist_node
from src.agents.critic import critic_node

def build_enterprise_agent_graph():
    """Builds and compiles the multi-agent execution graph."""
    builder = StateGraph(AgentState)

    # 1. Register Agent Nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("sql_analyst", sql_analyst_node)
    builder.add_node("doc_specialist", doc_specialist_node)
    builder.add_node("critic", critic_node)

    # 2. Define Execution Edges
    builder.add_edge(START, "supervisor")
    builder.add_edge("supervisor", "sql_analyst")
    builder.add_edge("sql_analyst", "doc_specialist")
    builder.add_edge("doc_specialist", "critic")
    builder.add_edge("critic", END)

    # 3. Compile Graph
    return builder.compile()

# Global compiled instance
enterprise_agent_app = build_enterprise_agent_graph()
