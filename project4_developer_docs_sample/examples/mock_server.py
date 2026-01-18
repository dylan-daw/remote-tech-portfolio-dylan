"""Mock LLM Retrieval API server.

This is a lightweight, dependency-free HTTP server intended to support the
developer-docs sample in this folder.

It intentionally implements a small, realistic surface area:
- Health check
- Document upsert
- Retrieval query
- Grounded 'answer' with citations

The retrieval is a simple bag-of-words cosine similarity. In production you
would use embeddings and a vector database.
"""

from __future__ import annotations

import json
import math
import os
import re
from dataclasses import dataclass, asdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List, Tuple

HOST = os.getenv("MOCK_API_HOST", "127.0.0.1")
PORT = int(os.getenv("MOCK_API_PORT", "8080"))

TOKEN_RE = re.compile(r"[a-zA-Z0-9']+")


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: Dict[str, Any]) -> None:
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


def _error(handler: BaseHTTPRequestHandler, status: int, err_type: str, message: str, details: Dict[str, Any] | None = None) -> None:
    _json_response(
        handler,
        status,
        {
            "error": {
                "type": err_type,
                "message": message,
                "details": details or {},
            }
        },
    )


def _read_json(handler: BaseHTTPRequestHandler) -> Dict[str, Any] | None:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        return None

    raw = handler.rfile.read(length) if length > 0 else b"{}"
    try:
        obj = json.loads(raw.decode("utf-8"))
    except Exception:
        return None

    if not isinstance(obj, dict):
        return None
    return obj


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in TOKEN_RE.findall(text or "")]


def _tf(tokens: List[str]) -> Dict[str, float]:
    counts: Dict[str, int] = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    if not tokens:
        return {}
    return {k: v / len(tokens) for k, v in counts.items()}


def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = 0.0
    for k, av in a.items():
        bv = b.get(k)
        if bv is not None:
            dot += av * bv
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


@dataclass
class Doc:
    doc_id: str
    title: str
    text: str
    metadata: Dict[str, Any]

    @property
    def snippet(self) -> str:
        t = (self.text or "").strip().replace("\n", " ")
        return (t[:220] + "...") if len(t) > 220 else t


class InMemoryIndex:
    def __init__(self) -> None:
        self._docs: Dict[str, Doc] = {}
        self._vecs: Dict[str, Dict[str, float]] = {}

    def upsert(self, docs: List[Doc]) -> List[str]:
        doc_ids: List[str] = []
        for d in docs:
            self._docs[d.doc_id] = d
            self._vecs[d.doc_id] = _tf(_tokenize(f"{d.title} {d.text}"))
            doc_ids.append(d.doc_id)
        return doc_ids

    def query(self, query: str, top_k: int = 3, min_score: float = 0.0) -> List[Tuple[Doc, float]]:
        qv = _tf(_tokenize(query))
        scored: List[Tuple[Doc, float]] = []
        for doc_id, doc in self._docs.items():
            s = _cosine(qv, self._vecs.get(doc_id, {}))
            if s >= min_score:
                scored.append((doc, s))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[: max(0, int(top_k))]


INDEX = InMemoryIndex()


def _make_grounded_answer(question: str, retrieved: List[Tuple[Doc, float]]) -> str:
    if not retrieved:
        return (
            "I don't have enough information in the provided documents to answer confidently. "
            "Try indexing more relevant material or rephrasing the question."
        )

    # Simple grounded summary: stitch together a few key sentences.
    # This is intentionally basic; the point is the product surface area.
    bullets: List[str] = []
    for doc, _score in retrieved[:3]:
        # Grab first sentence-like chunk
        text = (doc.text or "").strip().replace("\n", " ")
        sentence = re.split(r"(?<=[.!?])\s+", text)[0] if text else ""
        if sentence:
            bullets.append(sentence)

    if not bullets:
        bullets = [retrieved[0][0].snippet]

    return "Here’s what the indexed documents say:\n- " + "\n- ".join(bullets)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        # Quiet logs (keep sample output clean). Uncomment for debugging.
        # super().log_message(format, *args)
        return

    def do_GET(self) -> None:
        if self.path == "/v1/health":
            _json_response(self, 200, {"status": "ok"})
            return
        _error(self, 404, "not_found", "Unknown endpoint")

    def do_POST(self) -> None:
        if self.path == "/v1/docs:upsert":
            body = _read_json(self)
            if body is None:
                _error(self, 400, "invalid_request", "Invalid JSON")
                return

            docs_raw = body.get("documents")
            if not isinstance(docs_raw, list) or not docs_raw:
                _error(self, 400, "invalid_request", "'documents' must be a non-empty list")
                return

            docs: List[Doc] = []
            for i, item in enumerate(docs_raw):
                if not isinstance(item, dict):
                    _error(self, 400, "invalid_request", "Each document must be an object", {"index": i})
                    return
                doc_id = str(item.get("doc_id", "")).strip()
                title = str(item.get("title", "")).strip()
                text = str(item.get("text", "")).strip()
                metadata = item.get("metadata")
                if metadata is None:
                    metadata = {}
                if not isinstance(metadata, dict):
                    _error(self, 400, "invalid_request", "metadata must be an object", {"index": i})
                    return
                if not doc_id or not text:
                    _error(self, 400, "invalid_request", "doc_id and text are required", {"index": i})
                    return
                docs.append(Doc(doc_id=doc_id, title=title or doc_id, text=text, metadata=metadata))

            doc_ids = INDEX.upsert(docs)
            _json_response(self, 200, {"upserted": len(doc_ids), "doc_ids": doc_ids})
            return

        if self.path == "/v1/query":
            body = _read_json(self)
            if body is None:
                _error(self, 400, "invalid_request", "Invalid JSON")
                return
            query = body.get("query")
            if not isinstance(query, str) or not query.strip():
                _error(self, 400, "invalid_request", "'query' is required")
                return
            top_k = body.get("top_k", 3)
            min_score = body.get("min_score", 0.0)
            try:
                top_k_i = int(top_k)
                min_score_f = float(min_score)
            except Exception:
                _error(self, 400, "invalid_request", "top_k must be int and min_score must be float")
                return

            results = []
            for doc, score in INDEX.query(query, top_k=top_k_i, min_score=min_score_f):
                results.append(
                    {
                        "doc_id": doc.doc_id,
                        "score": round(score, 4),
                        "title": doc.title,
                        "snippet": doc.snippet,
                        "metadata": doc.metadata,
                    }
                )
            _json_response(self, 200, {"results": results})
            return

        if self.path == "/v1/answer":
            body = _read_json(self)
            if body is None:
                _error(self, 400, "invalid_request", "Invalid JSON")
                return
            question = body.get("question")
            if not isinstance(question, str) or not question.strip():
                _error(self, 400, "invalid_request", "'question' is required")
                return
            top_k = body.get("top_k", 3)
            try:
                top_k_i = int(top_k)
            except Exception:
                _error(self, 400, "invalid_request", "top_k must be int")
                return

            retrieved = INDEX.query(question, top_k=top_k_i)
            answer = _make_grounded_answer(question, retrieved)

            results = []
            citations: List[str] = []
            for doc, score in retrieved:
                citations.append(doc.doc_id)
                results.append(
                    {
                        "doc_id": doc.doc_id,
                        "score": round(score, 4),
                        "title": doc.title,
                        "snippet": doc.snippet,
                    }
                )

            _json_response(self, 200, {"answer": answer, "citations": citations, "results": results})
            return

        _error(self, 404, "not_found", "Unknown endpoint")


def main() -> None:
    server = HTTPServer((HOST, PORT), Handler)
    print(f"Mock LLM Retrieval API listening on http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
