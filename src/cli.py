"""
Interactive Rich Command Line Interface.
Demonstrates step-by-step multi-agent reasoning, tabular SQL inspection,
vector citations, and Human-in-the-Loop decision approval.
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from src.graph import enterprise_agent_app
from src.tools.ops_tools import approve_incident_action

console = Console()

def run_agent_workflow(query: str):
    console.print("\n[bold cyan]============================================================[/bold cyan]")
    console.print("[bold cyan]   ORACLE AGENTIC AI: ENTERPRISE ANALYST & OPS WORKFLOW     [/bold cyan]")
    console.print("[bold cyan]============================================================[/bold cyan]\n")
    console.print(f"[bold yellow]User Business Question:[/bold yellow] [white]{query}[/white]\n")

    initial_state = {
        "user_query": query,
        "plan": [],
        "current_step": 0,
        "sql_query": None,
        "sql_results": None,
        "sql_error_reflection": None,
        "doc_results": None,
        "oracle_23ai_vector_sql": None,
        "compliance_violations": None,
        "audit_ticket": None,
        "final_synthesis": None,
        "needs_human_approval": False,
        "human_approved": False,
        "execution_trace": []
    }

    # Execute LangGraph Multi-Agent Workflow
    with console.status("[bold green]Executing Multi-Agent Workflow...[/bold green]", spinner="dots"):
        final_state = enterprise_agent_app.invoke(initial_state)

    # 1. Print Execution Trace
    console.print(Panel("[bold green]Agent Reasoning & Execution Trace[/bold green]", expand=False))
    for step in final_state["execution_trace"]:
        agent = step["agent"]
        action = step["action"]
        detail = step["detail"]
        console.print(f"  • [bold blue][{agent}][/bold blue] [magenta]{action}[/magenta]: [dim]{detail}[/dim]")

    # 2. Display SQL Data Table
    sql_res = final_state.get("sql_results")
    if sql_res and sql_res.get("rows"):
        console.print("\n[bold green]Relational Query Results (SQL Execution):[/bold green]")
        table = Table(show_header=True, header_style="bold cyan")
        for col in sql_res["columns"]:
            table.add_column(col)
        for row in sql_res["rows"][:5]: # Show top 5 rows
            table.add_row(*[str(val) for val in row])
        console.print(table)

    # 3. Display Oracle 23ai Vector Query
    if final_state.get("oracle_23ai_vector_sql"):
        console.print(Panel(
            final_state["oracle_23ai_vector_sql"], 
            title="[bold blue]Oracle Database 23ai AI Vector Search SQL Equivalent[/bold blue]",
            border_style="blue"
        ))

    # 4. Display Final Executive Synthesis
    console.print("\n" + "="*80)
    console.print(Markdown(final_state["final_synthesis"]))
    console.print("="*80 + "\n")

    # 5. Human-in-the-Loop (HITL) Gate
    if final_state.get("needs_human_approval") and final_state.get("audit_ticket"):
        ticket = final_state["audit_ticket"]
        console.print(Panel(
            f"[bold red]CRITICAL ACTION REQUIRED (Human-in-the-Loop Gate)[/bold red]\n"
            f"Incident ID: [bold]{ticket.get('incident_id')}[/bold]\n"
            f"Recommended Action: {ticket.get('details', {}).get('recommended_action')}\n\n"
            "As Compliance Officer, do you authorize locking commission and formal audit submission? [Y/n]",
            border_style="red"
        ))
        
        choice = input("Enter decision (Y/n): ").strip().lower()
        if choice in ["y", "yes", ""]:
            res = approve_incident_action(ticket.get("incident_id"), "Compliance Officer (CLI)")
            console.print(f"[bold green][APPROVED][/bold green] {res['message']}")
        else:
            console.print("[bold yellow][REJECTED][/bold yellow] Remediation action held by human reviewer.")

if __name__ == "__main__":
    default_q = "Why did North America operating margin drop in Q3 2024, and did any sales contracts breach corporate discount guidelines?"
    user_input = sys.argv[1] if len(sys.argv) > 1 else default_q
    run_agent_workflow(user_input)
