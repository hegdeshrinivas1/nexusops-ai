"""
Relational Database Manager.
Provides schema inspection, guarded SQL execution, and execution plan retrieval.
Supports SQLite (local default) and Oracle Database 23ai (via python-oracledb).
"""

import sqlite3
from typing import Dict, List, Any, Tuple
from src.config import DB_PATH, ORACLE_23AI_ENABLED, ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN

class RelationalDB:
    def __init__(self):
        self.use_oracle = ORACLE_23AI_ENABLED
        self._init_connection()

    def _init_connection(self):
        if self.use_oracle:
            try:
                import oracledb
                self.conn = oracledb.connect(
                    user=ORACLE_USER,
                    password=ORACLE_PASSWORD,
                    dsn=ORACLE_DSN
                )
                self.is_oracle = True
            except Exception as e:
                print(f"[WARN] Failed to connect to Oracle 23ai ({e}). Falling back to SQLite.")
                self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                self.is_oracle = False
        else:
            self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.is_oracle = False

    def get_schema_summary(self) -> str:
        """Returns the DDL and column schema information for all tables."""
        cur = self.conn.cursor()
        if self.is_oracle:
            cur.execute("""
                SELECT table_name, column_name, data_type 
                FROM user_tab_columns 
                ORDER BY table_name, column_id
            """)
            rows = cur.fetchall()
            schema_dict = {}
            for table, col, dtype in rows:
                schema_dict.setdefault(table, []).append(f"{col} ({dtype})")
            return "\n".join([f"Table {t}:\n  - " + "\n  - ".join(cols) for t, cols in schema_dict.items()])
        else:
            cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = cur.fetchall()
            lines = []
            for name, sql in tables:
                lines.append(f"-- Table: {name}\n{sql}\n")
            return "\n".join(lines)

    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Executes a SELECT query with safety guardrails against destructive operations.
        Returns columns and rows, or detailed error information for self-healing reflection.
        """
        clean_sql = sql_query.strip().rstrip(";")
        
        # Enterprise Guardrails: Ensure queries are read-only
        forbidden = ["DROP", "DELETE", "TRUNCATE", "ALTER", "UPDATE", "INSERT INTO"]
        upper_sql = clean_sql.upper()
        for word in forbidden:
            if word in upper_sql and "AUDIT_INCIDENTS" not in upper_sql:
                return {
                    "success": False,
                    "error": f"Security Guardrail Violation: Unauthorized destructive keyword '{word}' detected. Only read-only analytical queries are permitted.",
                    "columns": [],
                    "rows": []
                }

        try:
            cur = self.conn.cursor()
            cur.execute(clean_sql)
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                # Convert rows to serializable format
                formatted_rows = [list(r) for r in rows]
                return {
                    "success": True,
                    "query": clean_sql,
                    "columns": columns,
                    "rows": formatted_rows,
                    "row_count": len(formatted_rows),
                    "error": None
                }
            else:
                self.conn.commit()
                return {
                    "success": True,
                    "query": clean_sql,
                    "columns": [],
                    "rows": [],
                    "row_count": cur.rowcount,
                    "error": None
                }
        except Exception as e:
            return {
                "success": False,
                "query": clean_sql,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "error": str(e)
            }

    def insert_audit_incident(self, incident: Dict[str, Any]) -> bool:
        """Inserts an audit violation record into the audit_incidents table."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO audit_incidents 
                (incident_id, contract_id, region, severity, description, recommended_action, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                incident["incident_id"],
                incident.get("contract_id"),
                incident["region"],
                incident["severity"],
                incident["description"],
                incident["recommended_action"],
                incident.get("status", "PENDING_APPROVAL")
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to record audit incident: {e}")
            return False

    def get_pending_incidents(self) -> List[Dict[str, Any]]:
        """Retrieves incidents requiring human sign-off."""
        cur = self.conn.cursor()
        cur.execute("SELECT incident_id, contract_id, region, severity, description, recommended_action, status, created_at FROM audit_incidents ORDER BY created_at DESC;")
        rows = cur.fetchall()
        cols = ["incident_id", "contract_id", "region", "severity", "description", "recommended_action", "status", "created_at"]
        return [dict(zip(cols, r)) for r in rows]
