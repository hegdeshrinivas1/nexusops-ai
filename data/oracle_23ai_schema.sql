-- ============================================================================
-- ORACLE DATABASE 23ai DDL & AI VECTOR SEARCH DEFINITION
-- Enterprise Sales, Financial Performance & Vector Memory
-- ============================================================================

-- 1. Relational Table: Regional Financials
CREATE TABLE regional_financials (
    financial_id    NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fiscal_quarter  VARCHAR2(10) NOT NULL,    -- e.g., 'Q3-2024'
    region          VARCHAR2(50) NOT NULL,    -- 'North America', 'EMEA', 'APAC', 'LATAM'
    revenue_usd     NUMBER(14, 2) NOT NULL,
    operating_cost  NUMBER(14, 2) NOT NULL,
    operating_margin_pct NUMBER(5, 2) NOT NULL,
    cogs_usd        NUMBER(14, 2) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Relational Table: Sales Contracts & Transactions
CREATE TABLE sales_contracts (
    contract_id     VARCHAR2(20) PRIMARY KEY, -- e.g., 'CTR-2024-901'
    customer_name   VARCHAR2(100) NOT NULL,
    region          VARCHAR2(50) NOT NULL,
    product_line    VARCHAR2(80) NOT NULL,    -- 'Cloud Infrastructure', 'Autonomous DB', 'Apps'
    deal_size_usd   NUMBER(14, 2) NOT NULL,
    discount_pct    NUMBER(5, 2) NOT NULL,    -- e.g., 24.50
    sales_rep       VARCHAR2(80) NOT NULL,
    approval_waiver VARCHAR2(20) DEFAULT NULL, -- 'EW-99' if approved, NULL if unauthorized
    close_date      DATE NOT NULL,
    status          VARCHAR2(30) DEFAULT 'CLOSED'
);

-- 3. Oracle 23ai Vector Table: Enterprise Knowledge & Policies
-- Uses Oracle 23ai native VECTOR data type (e.g., 384 dimensions for all-MiniLM-L6-v2)
CREATE TABLE enterprise_documents_23ai (
    doc_id          VARCHAR2(50) PRIMARY KEY,
    doc_title       VARCHAR2(255) NOT NULL,
    doc_type        VARCHAR2(50) NOT NULL,    -- 'POLICY', 'MEMO', 'SOP'
    chunk_index     NUMBER NOT NULL,
    chunk_text      CLOB NOT NULL,
    embedding       VECTOR(384, FLOAT32),     -- Oracle 23ai Native Vector Type
    metadata_json   JSON                      -- Oracle JSON support for hybrid metadata filtering
);

-- 4. Oracle 23ai Vector Index (Hierarchical Navigable Small World / HNSW Graph)
CREATE VECTOR INDEX doc_hnsw_idx ON enterprise_documents_23ai(embedding)
ORGANIZATION INMEMORY NEIGHBOR GRAPH
DISTANCE COSINE;

-- 5. Oracle 23ai Hybrid Search Query Example (Relational Filter + Semantic Distance)
-- Demonstrates how an Agent issues a hybrid SQL query in Oracle 23ai:
/*
SELECT 
    doc_title, 
    chunk_text, 
    VECTOR_DISTANCE(embedding, :query_vector, COSINE) AS distance
FROM enterprise_documents_23ai
WHERE doc_type = 'POLICY'
ORDER BY distance ASC
FETCH FIRST 3 ROWS ONLY;
*/
