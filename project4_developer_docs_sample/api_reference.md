# API Reference: Mock LLM Retrieval API

This document describes the REST API exposed by the mock server in `examples/mock_server.py`.

## Base URL

Local dev:

- `http://127.0.0.1:8080`

## Authentication

The mock API **does not require authentication**. In a production system, you would typically use an API key or OAuth.

A common pattern is an `Authorization: Bearer <token>` header and per-project rate limits.

## Content type

All requests and responses use JSON.

- Request header: `Content-Type: application/json`
- Response header: `Content-Type: application/json`

## Error model

Errors return a JSON object with the following schema:

```json
{
  "error": {
    "type": "invalid_request",
    "message": "Human-readable description",
    "details": {"field": "additional context"}
  }
}
```

Common error types:
- `invalid_request` (missing fields, invalid JSON)
- `not_found` (unknown resource)
- `internal` (unexpected server error)

## Endpoints

### GET /v1/health

Health check.

**Response**

```json
{ "status": "ok" }
```

---

### POST /v1/docs:upsert

Create or update documents in the retrieval index.

**Request body**

```json
{
  "documents": [
    {
      "doc_id": "doc-1",
      "title": "Short title",
      "text": "Document content to index",
      "metadata": {"source": "demo", "lang": "en"}
    }
  ]
}
```

**Notes**
- `doc_id` is caller-provided and must be unique.
- `metadata` is optional and must be JSON-serializable.

**Response**

```json
{
  "upserted": 1,
  "doc_ids": ["doc-1"]
}
```

**Example**

```bash
curl -s http://127.0.0.1:8080/v1/docs:upsert \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {"doc_id": "doc-1", "title": "Alpha", "text": "Fire is hot."}
    ]
  }'
```

---

### POST /v1/query

Run a retrieval query against indexed documents.

**Request body**

```json
{
  "query": "What is fire?",
  "top_k": 3,
  "min_score": 0.0
}
```

**Parameters**
- `query` (string, required): user question or search query
- `top_k` (int, optional): number of results to return (default: 3)
- `min_score` (float, optional): filter out results below this score (default: 0.0)

**Response**

```json
{
  "results": [
    {
      "doc_id": "doc-2",
      "score": 0.73,
      "title": "Beta",
      "snippet": "...",
      "metadata": {"source": "demo"}
    }
  ]
}
```

**Example**

```bash
curl -s http://127.0.0.1:8080/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What suppresses fire?", "top_k": 2}'
```

---

### POST /v1/answer

Generate a mock "assistant" answer by retrieving relevant docs and summarizing them.

This is a stand-in for a real LLM call. The server:
1) retrieves `top_k` docs
2) produces a short, grounded answer
3) returns **citations** (doc_ids) so a client can render attribution

**Request body**

```json
{
  "question": "How can I stop a small fire?",
  "top_k": 3
}
```

**Response**

```json
{
  "answer": "...",
  "citations": ["doc-2", "doc-1"],
  "results": [
    {"doc_id": "doc-2", "score": 0.61, "title": "...", "snippet": "..."}
  ]
}
```

## Versioning

All endpoints are versioned under `/v1/`. A typical approach is:
- add non-breaking fields freely
- make breaking changes under a new major version (`/v2/`)
- publish a migration guide with concrete examples

## OpenAPI (minimal sample)

Below is an intentionally small OpenAPI snippet showing how these endpoints could be specified.

```yaml
openapi: 3.0.3
info:
  title: Mock LLM Retrieval API
  version: 1.0.0
servers:
  - url: http://127.0.0.1:8080
paths:
  /v1/health:
    get:
      responses:
        '200':
          description: OK
  /v1/query:
    post:
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [query]
              properties:
                query: {type: string}
                top_k: {type: integer, default: 3}
      responses:
        '200':
          description: OK
```
