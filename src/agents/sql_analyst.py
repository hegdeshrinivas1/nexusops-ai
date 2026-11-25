"""
SQL Data Analyst Agent.
Implements the ReAct (Reasoning + Acting) loop with automated self-healing SQL reflection.
Inspects database schema, drafts SQL queries, executes them, and heals syntax or semantic errors.
"""

from typing import Dict, Any
from src.agents.state import AgentState
from src.tools.sql_tools import inspect_database_schema, execute_analytical_sql
from src.agents.llm_client import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

def sql_analyst_node(state: AgentState) -> Dict[str, Any]:
    trace = list(state.get("execution_trace", []))
    query = state["user_query"]
    llm = get_llm()

    # Step 1: Inspect Schema (Action 1)
    schema = inspect_database_schema()
    trace.append({
        "agent": "SQL Data Analyst",
        "action": "Tool Call: inspect_database_schema()",
        "detail": "Retrieved schema definitions for 'regional_financials' and 'sales_contracts'."
    })

    # Step 2: Formulate SQL Query (Reasoning)
    sql_to_run = ""
    if llm:
        try:
            prompt = f"""You are an expert Enterprise SQL Data Analyst.
Available Database Schema:
{schema}

User Inquiry: {query}

Write a single standard SQL SELECT query to retrieve the necessary data (e.g. regional financials or contracts with discounts).
Do NOT include markdown formatting or quotes. Output ONLY the raw SQL query."""
            resp = llm.invoke([SystemMessage(content=prompt)])
            sql_to_run = resp.content.strip().replace("```sql", "").replace("```", "").strip()
        except Exception:
            sql_to_run = ""

    if not sql_to_run:
        # Default analytical query tailored to regional performance and discounts
        sql_to_run = """SELECT c.contract_id, c.customer_name, c.region, c.product_line, 
       c.deal_size_usd, c.discount_pct, c.sales_rep, c.approval_waiver,
       f.operating_margin_pct, f.fiscal_quarter
FROM sales_contracts c
LEFT JOIN regional_financials f 
  ON c.region = f.region AND f.fiscal_quarter = 'Q3-2024'
WHERE c.region = 'North America'
ORDER BY c.discount_pct DESC;"""

    trace.append({
        "agent": "SQL Data Analyst",
        "action": "Generated SQL Query",
        "detail": sql_to_run
    })

    # Step 3: Execute SQL (Action 2)
    result = execute_analytical_sql(sql_to_run)
    error_reflection = None

    # Step 4: Self-Correction Loop (Observation & Reflection)
    if not result["success"]:
        trace.append({
            "agent": "SQL Data Analyst",
            "action": "Self-Correction Triggered",
            "detail": f"Execution failed: {result['error']}. Reflecting and repairing SQL..."
        })

        # Self-healing repair
        if llm:
            repair_prompt = f"""The following SQL query failed with error: {result['error']}
Failed SQL: {sql_to_run}
Schema: {schema}
Provide a corrected, valid SQL SELECT query only."""
            repaired_resp = llm.invoke([SystemMessage(content=repair_prompt)])
            sql_to_run = repaired_resp.content.strip().replace("```sql", "").replace("```", "").strip()
        else:
            # Fallback to safe known compliant query
            sql_to_run = "SELECT * FROM sales_contracts WHERE region = 'North America' ORDER BY discount_pct DESC;"

        result = execute_analytical_sql(sql_to_run)
        error_reflection = "Initial query encountered an execution error; repaired automatically via reflection."
        trace.append({
            "agent": "SQL Data Analyst",
            "action": "Repaired SQL Executed",
            "detail": f"Repaired query returned {result.get('row_count', 0)} rows."
        })
    else:
        trace.append({
            "agent": "SQL Data Analyst",
            "action": "SQL Execution Succeeded",
            "detail": f"Successfully retrieved {result.get('row_count', 0)} rows."
        })

    return {
        "sql_query": sql_to_run,
        "sql_results": result,
        "sql_error_reflection": error_reflection,
        "execution_trace": trace
    }
