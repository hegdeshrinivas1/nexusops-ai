"""
NexusOps AI Web Server (Starlette + Uvicorn).
Serves the monochrome Black & White single-page web application and exposes
REST endpoints for multi-agent workflow execution, SQL/Vector data exploration,
and Human-in-the-Loop (HITL) incident approvals.
"""

from pathlib import Path
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route
from starlette.requests import Request
import uvicorn

from src.graph import enterprise_agent_app
from src.tools.sql_tools import inspect_database_schema, execute_analytical_sql
from src.tools.ops_tools import (
    approve_incident_action,
    reject_incident_action,
    clear_audit_incidents,
    get_relational_db,
)
from src.config import DOCS_DIR, DATA_DIR, ORACLE_23AI_ENABLED

FRONTEND_HTML = Path(__file__).resolve().parent / "frontend" / "index.html"


def _get_margin_series():
    res = execute_analytical_sql(
        "SELECT fiscal_quarter, region, operating_margin_pct FROM regional_financials ORDER BY fiscal_quarter, region;"
    )
    if not res.get("success"):
        return []
    cols = res["columns"]
    return [dict(zip(cols, row)) for row in res["rows"]]


async def homepage(request: Request):
    return HTMLResponse(FRONTEND_HTML.read_text(encoding="utf-8"))


async def api_status(request: Request):
    db = get_relational_db()
    incidents = db.get_pending_incidents()
    pending_count = sum(1 for i in incidents if i["status"] == "PENDING_APPROVAL")
    return JSONResponse({
        "db_engine": "Oracle 23ai" if ORACLE_23AI_ENABLED else "SQLite + Vector",
        "pending_incidents": pending_count,
        "margin_series": _get_margin_series(),
    })


async def api_analyze(request: Request):
    body = await request.json()
    query = (body.get("query") or "").strip()
    if not query:
        return JSONResponse({"error": "Query cannot be empty."}, status_code=400)

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
        "execution_trace": [],
    }

    result = enterprise_agent_app.invoke(initial_state)
    result["schema_ddl"] = inspect_database_schema()
    result["margin_series"] = _get_margin_series()
    return JSONResponse(result)


async def api_data(request: Request):
    fin = execute_analytical_sql("SELECT * FROM regional_financials ORDER BY fiscal_quarter, region;")
    ctr = execute_analytical_sql("SELECT * FROM sales_contracts ORDER BY discount_pct DESC;")

    docs = []
    for doc_file in sorted(DOCS_DIR.glob("*.txt")):
        docs.append({
            "filename": doc_file.name,
            "title": doc_file.stem.replace("_", " ").title(),
            "content": doc_file.read_text(encoding="utf-8"),
        })

    ddl_path = DATA_DIR / "oracle_23ai_schema.sql"
    ddl_text = ddl_path.read_text(encoding="utf-8") if ddl_path.exists() else ""

    return JSONResponse({
        "financials": {"columns": fin.get("columns", []), "rows": fin.get("rows", [])},
        "contracts": {"columns": ctr.get("columns", []), "rows": ctr.get("rows", [])},
        "documents": docs,
        "ddl": ddl_text,
    })


async def api_incidents(request: Request):
    db = get_relational_db()
    return JSONResponse({"incidents": db.get_pending_incidents()})


async def api_approve_incident(request: Request):
    incident_id = request.path_params["incident_id"]
    res = approve_incident_action(incident_id, "Compliance Officer (Web Console)")
    return JSONResponse(res)


async def api_reject_incident(request: Request):
    incident_id = request.path_params["incident_id"]
    res = reject_incident_action(incident_id, "Compliance Officer (Web Console)")
    return JSONResponse(res)


async def api_reset_incidents(request: Request):
    clear_audit_incidents()
    return JSONResponse({"success": True})


routes = [
    Route("/", homepage),
    Route("/api/status", api_status),
    Route("/api/analyze", api_analyze, methods=["POST"]),
    Route("/api/data", api_data),
    Route("/api/incidents", api_incidents),
    Route("/api/incidents/{incident_id}/approve", api_approve_incident, methods=["POST"]),
    Route("/api/incidents/{incident_id}/reject", api_reject_incident, methods=["POST"]),
    Route("/api/incidents/reset", api_reset_incidents, methods=["POST"]),
]

app = Starlette(debug=False, routes=routes)

if __name__ == "__main__":
    print("NexusOps AI Web Console running at http://localhost:8501")
    uvicorn.run(app, host="0.0.0.0", port=8501, log_level="warning")
