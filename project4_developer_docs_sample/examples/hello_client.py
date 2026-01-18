"""Sample client for the Mock LLM Retrieval API.

Runs a tiny end-to-end flow:
1) health check
2) upsert a few documents
3) ask a question and print the answer with citations

Usage:
  python -m project4_developer_docs_sample.examples.hello_client
"""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.error

BASE_URL = os.getenv("MOCK_API_BASE_URL", "http://127.0.0.1:8080")


def _post(path: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {body}") from e


def _get(path: str) -> dict:
    req = urllib.request.Request(url=f"{BASE_URL}{path}", method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {body}") from e


def main() -> None:
    health = _get("/v1/health")
    print(f"Health: {health.get('status')}")

    docs = [
        {
            "doc_id": "doc-1",
            "title": "Small fire safety basics",
            "text": "For a small contained fire, cut off oxygen and use appropriate extinguishing media. If in doubt, evacuate and call emergency services.",
            "metadata": {"source": "demo", "topic": "safety"},
        },
        {
            "doc_id": "doc-2",
            "title": "Water and fire",
            "text": "Water can suppress many ordinary combustibles by cooling them below ignition temperature. Do not use water on grease or electrical fires.",
            "metadata": {"source": "demo", "topic": "suppression"},
        },
        {
            "doc_id": "doc-3",
            "title": "Class C and grease fires",
            "text": "For grease fires, smother with a lid or use baking soda; never throw water. For electrical fires, de-energize the circuit if safe and use a Class C extinguisher.",
            "metadata": {"source": "demo", "topic": "hazards"},
        },
    ]

    upsert = _post("/v1/docs:upsert", {"documents": docs})
    print(f"Upserted {upsert.get('upserted')} docs")

    answer = _post("/v1/answer", {"question": "How can I stop a small fire?", "top_k": 3})

    results = answer.get("results", [])
    if results:
        top = results[0]
        print(f"Query top result: (doc_id={top.get('doc_id')}, score={top.get('score')})")

    print("Answer:")
    print(answer.get("answer", ""))
    print("\nCitations:")
    for c in answer.get("citations", []):
        print(f"- {c}")


if __name__ == "__main__":
    main()
