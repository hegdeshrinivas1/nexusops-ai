"""
Unit and Integration Tests for the Oracle Agentic AI System.
Tests relational execution, vector similarity search, agent reasoning, and LangGraph workflow.
"""

import unittest
from src.tools.sql_tools import inspect_database_schema, execute_analytical_sql
from src.tools.doc_tools import search_enterprise_knowledge
from src.graph import enterprise_agent_app

class TestOracleAgenticAI(unittest.TestCase):

    def test_schema_inspection(self):
        schema = inspect_database_schema()
        self.assertIn("regional_financials", schema)
        self.assertIn("sales_contracts", schema)

    def test_sql_execution(self):
        query = "SELECT count(*) FROM sales_contracts;"
        res = execute_analytical_sql(query)
        self.assertTrue(res["success"])
        self.assertEqual(res["rows"][0][0], 12)

    def test_vector_search(self):
        results = search_enterprise_knowledge("discount policy exception waiver", top_k=2)
        self.assertGreater(len(results), 0)
        top_title = results[0]["title"]
        self.assertIn("Discount", top_title)

    def test_end_to_end_langgraph_workflow(self):
        state = {
            "user_query": "Why did North America operating margin drop in Q3 2024, and did any sales contracts breach corporate discount guidelines?",
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

        output = enterprise_agent_app.invoke(state)

        # Assert plan was generated
        self.assertTrue(len(output["plan"]) >= 2)
        # Assert SQL was executed
        self.assertIsNotNone(output["sql_results"])
        self.assertTrue(output["sql_results"]["success"])
        # Assert Vector Search returned chunks
        self.assertIsNotNone(output["doc_results"])
        self.assertTrue(len(output["doc_results"]) > 0)
        # Assert Violations were caught
        self.assertIsNotNone(output["compliance_violations"])
        self.assertTrue(len(output["compliance_violations"]) >= 1)
        # Assert HITL gate was flagged
        self.assertTrue(output["needs_human_approval"])
        # Assert synthesis was generated
        self.assertIn("Executive Analysis", output["final_synthesis"])

if __name__ == "__main__":
    unittest.main()
