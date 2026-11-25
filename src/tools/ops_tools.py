"""
Operations & Human-in-the-Loop (HITL) Tools.
Allows the multi-agent system to stage remediation actions and draft audit tickets.
"""

import uuid
from typing import Dict, Any
from src.tools.sql_tools import get_relational_db

def create_audit_ticket(
    contract_id: str,
    region: str,
    severity: str,
    description: str,
    recommended_action: str
) -> Dict[str, Any]:
    """
    Drafts an official enterprise audit ticket for a detected policy violation.
    The ticket is placed in PENDING_APPROVAL status awaiting Human-in-the-Loop review.
    """
    db = get_relational_db()
    incident_id = f"INC-{uuid.uuid4().hex[:6].upper()}"
    incident_data = {
        "incident_id": incident_id,
        "contract_id": contract_id,
        "region": region,
        "severity": severity,
        "description": description,
        "recommended_action": recommended_action,
        "status": "PENDING_APPROVAL"
    }
    
    success = db.insert_audit_incident(incident_data)
    return {
        "success": success,
        "incident_id": incident_id,
        "status": "PENDING_APPROVAL",
        "details": incident_data,
        "message": f"Audit ticket {incident_id} successfully drafted. Requires Compliance Officer (Human) confirmation before locking commission."
    }

def approve_incident_action(incident_id: str, approver_name: str = "Compliance Officer") -> Dict[str, Any]:
    """Human-in-the-loop action: Approves and resolves an audit incident ticket."""
    db = get_relational_db()
    cur = db.conn.cursor()
    cur.execute("UPDATE audit_incidents SET status = 'APPROVED_BY_HUMAN' WHERE incident_id = ?;", (incident_id,))
    db.conn.commit()
    return {
        "incident_id": incident_id,
        "status": "APPROVED_BY_HUMAN",
        "approver": approver_name,
        "message": f"Incident {incident_id} approved by {approver_name}. Commission hold and corrective workflow initiated."
    }

def reject_incident_action(incident_id: str, reviewer_name: str = "Compliance Officer") -> Dict[str, Any]:
    """Human-in-the-loop action: Rejects / dismisses a drafted audit incident ticket."""
    db = get_relational_db()
    cur = db.conn.cursor()
    cur.execute("UPDATE audit_incidents SET status = 'REJECTED_BY_HUMAN' WHERE incident_id = ?;", (incident_id,))
    db.conn.commit()
    return {
        "incident_id": incident_id,
        "status": "REJECTED_BY_HUMAN",
        "reviewer": reviewer_name,
        "message": f"Incident {incident_id} deferred/rejected by {reviewer_name}. No financial hold applied."
    }

def clear_audit_incidents() -> bool:
    """Clears audit incident history for clean demo resets."""
    db = get_relational_db()
    cur = db.conn.cursor()
    cur.execute("DELETE FROM audit_incidents;")
    db.conn.commit()
    return True
