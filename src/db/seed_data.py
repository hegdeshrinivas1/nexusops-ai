"""
Seed enterprise relational database and vector document collection.
Generates realistic transactional sales data, regional margins, and policy embeddings.
"""

import sqlite3
import json
from pathlib import Path
from src.config import DB_PATH, DOCS_DIR, VECTOR_INDEX_PATH

def init_relational_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Regional Financials Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS regional_financials (
        financial_id INTEGER PRIMARY KEY AUTOINCREMENT,
        fiscal_quarter TEXT NOT NULL,
        region TEXT NOT NULL,
        revenue_usd REAL NOT NULL,
        operating_cost REAL NOT NULL,
        operating_margin_pct REAL NOT NULL,
        cogs_usd REAL NOT NULL
    );
    """)

    # 2. Sales Contracts Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales_contracts (
        contract_id TEXT PRIMARY KEY,
        customer_name TEXT NOT NULL,
        region TEXT NOT NULL,
        product_line TEXT NOT NULL,
        deal_size_usd REAL NOT NULL,
        discount_pct REAL NOT NULL,
        sales_rep TEXT NOT NULL,
        approval_waiver TEXT,
        close_date TEXT NOT NULL,
        status TEXT DEFAULT 'CLOSED'
    );
    """)

    # 3. Audit Incidents Table (for Operations Agent / HITL remediation)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_incidents (
        incident_id TEXT PRIMARY KEY,
        contract_id TEXT,
        region TEXT NOT NULL,
        severity TEXT NOT NULL,
        description TEXT NOT NULL,
        recommended_action TEXT NOT NULL,
        status TEXT DEFAULT 'PENDING_APPROVAL',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Clear existing rows to ensure clean state
    cur.execute("DELETE FROM regional_financials;")
    cur.execute("DELETE FROM sales_contracts;")

    # Seed Financials
    financials_data = [
        # Q1 2024
        ('Q1-2024', 'North America', 62500000.0, 44375000.0, 29.0, 25000000.0),
        ('Q1-2024', 'EMEA', 41200000.0, 31312000.0, 24.0, 16480000.0),
        ('Q1-2024', 'APAC', 21000000.0, 16170000.0, 23.0, 8400000.0),
        ('Q1-2024', 'LATAM', 8800000.0, 6864000.0, 22.0, 3520000.0),
        # Q2 2024
        ('Q2-2024', 'North America', 65100000.0, 46546500.0, 28.5, 26040000.0),
        ('Q2-2024', 'EMEA', 42800000.0, 32314000.0, 24.5, 17120000.0),
        ('Q2-2024', 'APAC', 22500000.0, 17100000.0, 24.0, 9000000.0),
        ('Q2-2024', 'LATAM', 9100000.0, 7098000.0, 22.0, 3640000.0),
        # Q3 2024 (Erosion in North America)
        ('Q3-2024', 'North America', 68200000.0, 58515600.0, 14.2, 38192000.0),
        ('Q3-2024', 'EMEA', 44100000.0, 33604200.0, 23.8, 17640000.0),
        ('Q3-2024', 'APAC', 24800000.0, 18600000.0, 25.0, 9920000.0),
        ('Q3-2024', 'LATAM', 9700000.0, 7663000.0, 21.0, 3880000.0),
    ]
    cur.executemany("""
        INSERT INTO regional_financials 
        (fiscal_quarter, region, revenue_usd, operating_cost, operating_margin_pct, cogs_usd)
        VALUES (?, ?, ?, ?, ?, ?);
    """, financials_data)

    # Seed Contracts (Q3 2024)
    contracts_data = [
        ('CTR-2024-901', 'Acme Health Systems', 'North America', 'Autonomous DB', 4500000.0, 12.0, 'David Miller', None, '2024-07-15'),
        ('CTR-2024-902', 'Global Logistics Ltd', 'EMEA', 'Cloud Infrastructure', 6200000.0, 14.5, 'Sophie Laurent', None, '2024-07-28'),
        ('CTR-2024-903', 'Metro Transit Authority', 'North America', 'ERP Apps', 3100000.0, 9.5, 'Sarah Jenkins', None, '2024-08-04'),
        ('CTR-2024-904', 'Apex Global Bank', 'North America', 'Cloud Infrastructure', 18500000.0, 24.5, 'David Miller', None, '2024-09-28'), # Violation!
        ('CTR-2024-905', 'Tokyo Telecom Holdings', 'APAC', 'Autonomous DB', 8100000.0, 11.0, 'Kenji Sato', None, '2024-08-19'),
        ('CTR-2024-906', 'Vanguard Aerospace', 'EMEA', 'Cloud Infrastructure', 7400000.0, 15.0, 'Hans Weber', None, '2024-09-12'),
        ('CTR-2024-907', 'Banco de Sao Paulo', 'LATAM', 'ERP Apps', 2800000.0, 10.0, 'Carlos Silva', None, '2024-08-25'),
        ('CTR-2024-908', 'Nordic Energy Group', 'EMEA', 'Autonomous DB', 5100000.0, 13.0, 'Astrid Lind', None, '2024-09-02'),
        ('CTR-2024-909', 'OmniRetail Corp', 'North America', 'Cloud Infrastructure', 12000000.0, 22.0, 'Mark Thompson', None, '2024-09-30'), # Violation!
        ('CTR-2024-910', 'Sydney Mining Co', 'APAC', 'Cloud Infrastructure', 4900000.0, 10.5, 'Chloe Bennett', None, '2024-09-15'),
        ('CTR-2024-911', 'Horizon Media Group', 'North America', 'ERP Apps', 2100000.0, 14.0, 'Sarah Jenkins', None, '2024-08-11'),
        ('CTR-2024-912', 'FinTech Dynamics', 'North America', 'Autonomous DB', 9200000.0, 18.0, 'David Miller', 'EW-99', '2024-09-22'), # Compliant with waiver
    ]
    cur.executemany("""
        INSERT INTO sales_contracts 
        (contract_id, customer_name, region, product_line, deal_size_usd, discount_pct, sales_rep, approval_waiver, close_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, contracts_data)

    conn.commit()
    conn.close()
    print(f"[OK] Initialized SQLite Database at {DB_PATH}")

def chunk_document(text: str, chunk_size: int = 400):
    """Simple semantic/paragraph splitter."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if len(current_chunk) + len(p) < chunk_size:
            current_chunk += "\n\n" + p if current_chunk else p
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = p
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def build_vector_store():
    """Builds a lightweight vector store index simulating Oracle 23ai AI Vector Search."""
    from src.db.vector_store import VectorStore
    vs = VectorStore()
    
    docs_seeded = 0
    for doc_file in DOCS_DIR.glob("*.txt"):
        content = doc_file.read_text(encoding="utf-8")
        title = doc_file.stem.replace("_", " ").title()
        doc_type = "POLICY" if "policy" in doc_file.stem else ("MEMO" if "memo" in doc_file.stem else "SOP")
        chunks = chunk_document(content)
        
        for idx, chunk in enumerate(chunks):
            vs.add_document(
                doc_id=f"{doc_file.stem}_{idx}",
                title=title,
                doc_type=doc_type,
                chunk_index=idx,
                text=chunk,
                metadata={"source": doc_file.name, "doc_type": doc_type}
            )
            docs_seeded += 1
            
    vs.save(VECTOR_INDEX_PATH)
    print(f"[OK] Seeded {docs_seeded} chunks into Vector Store index at {VECTOR_INDEX_PATH}")

if __name__ == "__main__":
    init_relational_db()
    build_vector_store()
