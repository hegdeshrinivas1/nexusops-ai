"""
Vector Store and Hybrid Search Engine.
Simulates Oracle Database 23ai AI Vector Search with support for both:
1. Native vector similarity search (cosine distance).
2. Metadata filtering (hybrid query pattern).
3. Exportable Oracle 23ai VECTOR_DISTANCE SQL syntax.
"""

import json
import math
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

class VectorStore:
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

    def _tokenize(self, text: str) -> List[str]:
        """Simple alphanumeric tokenizer."""
        return re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", text.lower())

    def _compute_vector(self, text: str) -> List[float]:
        """
        Computes normalized TF-IDF vector for text.
        Guarantees fast, reproducible semantic vector representation with no network required.
        """
        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * max(len(self.vocabulary), 1)

        counts: Dict[str, int] = {}
        for t in tokens:
            counts[t] = counts.get(t, 0) + 1

        vec = np.zeros(len(self.vocabulary) if self.vocabulary else 1)
        for token, count in counts.items():
            if token in self.vocabulary:
                idx = self.vocabulary[token]
                tf = count / len(tokens)
                idf = self.idf.get(token, 1.0)
                vec[idx] = tf * idf

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def add_document(self, doc_id: str, title: str, doc_type: str, chunk_index: int, text: str, metadata: Dict[str, Any]):
        self.documents.append({
            "doc_id": doc_id,
            "title": title,
            "doc_type": doc_type,
            "chunk_index": chunk_index,
            "text": text,
            "metadata": metadata,
            "embedding": []
        })

    def _build_vocab(self):
        """Builds vocabulary and inverse document frequencies across loaded documents."""
        all_tokens = []
        doc_count = len(self.documents)
        doc_freq: Dict[str, int] = {}

        for doc in self.documents:
            tokens = set(self._tokenize(doc["text"]))
            for t in tokens:
                doc_freq[t] = doc_freq.get(t, 0) + 1

        # Keep top informative tokens
        sorted_tokens = sorted(doc_freq.keys())
        self.vocabulary = {token: idx for idx, token in enumerate(sorted_tokens)}
        self.idf = {
            token: math.log((1 + doc_count) / (1 + freq)) + 1.0
            for token, freq in doc_freq.items()
        }

        # Calculate vector for all chunks
        for doc in self.documents:
            doc["embedding"] = self._compute_vector(doc["text"])

    def save(self, filepath: Path):
        self._build_vocab()
        payload = {
            "vocabulary": self.vocabulary,
            "idf": self.idf,
            "documents": self.documents
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def load(self, filepath: Path):
        with open(filepath, "r", encoding="utf-8") as f:
            payload = json.load(f)
        self.vocabulary = payload["vocabulary"]
        self.idf = payload["idf"]
        self.documents = payload["documents"]

    def hybrid_search(
        self, 
        query: str, 
        top_k: int = 3, 
        doc_type_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes Hybrid Search: Semantic Vector Search + Metadata Filter.
        Equivalent to Oracle 23ai AI Vector Search:
        SELECT ... WHERE doc_type = :filter ORDER BY VECTOR_DISTANCE(embedding, :query_vec, COSINE)
        """
        query_vec = np.array(self._compute_vector(query))
        query_norm = np.linalg.norm(query_vec)

        results = []
        for doc in self.documents:
            # Metadata filter check
            if doc_type_filter and doc.get("doc_type") != doc_type_filter:
                continue

            doc_vec = np.array(doc["embedding"])
            doc_norm = np.linalg.norm(doc_vec)

            # Cosine similarity calculation
            if query_norm > 0 and doc_norm > 0:
                sim = float(np.dot(query_vec, doc_vec) / (query_norm * doc_norm))
            else:
                sim = 0.0

            results.append({
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "doc_type": doc["doc_type"],
                "chunk_index": doc["chunk_index"],
                "text": doc["text"],
                "similarity_score": round(sim, 4),
                "metadata": doc.get("metadata", {})
            })

        # Sort descending by similarity
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

    def generate_oracle_23ai_vector_sql(self, query_concept: str, top_k: int = 3) -> str:
        """Returns the equivalent SQL syntax for Oracle 23ai AI Vector Search."""
        return f"""-- Equivalent Oracle 23ai AI Vector Search SQL:
SELECT doc_title, doc_type, chunk_text, 
       ROUND(1 - VECTOR_DISTANCE(embedding, VECTOR_EMBEDDING(doc_model USING '{query_concept}'), COSINE), 4) AS similarity_score
FROM enterprise_documents_23ai
WHERE doc_type IN ('POLICY', 'MEMO', 'SOP')
ORDER BY VECTOR_DISTANCE(embedding, VECTOR_EMBEDDING(doc_model USING '{query_concept}'), COSINE) ASC
FETCH FIRST {top_k} ROWS ONLY;"""
