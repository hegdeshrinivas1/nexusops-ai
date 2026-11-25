"""
SQL Tools for the SQL Analyst Agent.
Implements schema inspection, query execution, and guardrail validations.
"""

from typing import Dict, Any
from src.db.relational import RelationalDB

_db = RelationalDB()

def inspect_database_schema() -> str:
    """Returns the schema definition, tables, and column data types available in the enterprise database."""
    return _db.get_schema_summary()

def execute_analytical_sql(sql_query: str) -> Dict[str, Any]:
    """
    Executes a read-only SQL query against the enterprise database.
    If the query fails with a syntax error, returns the error message so the agent can reflect and self-heal.
    """
    return _db.execute_query(sql_query)

def get_relational_db() -> RelationalDB:
    return _db
