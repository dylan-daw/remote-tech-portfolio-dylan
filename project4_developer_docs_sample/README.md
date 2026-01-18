# Developer Docs Sample: LLM Retrieval API (Mock)

This folder is a **developer documentation writing sample** that demonstrates how I structure and write docs for an LLM-enabled product.

It includes:
- A **Quickstart** (this file)
- An **API reference** with examples: `api_reference.md`
- A **RAG tutorial** (LLM + vector retrieval): `tutorial_rag.md`
- A **runnable mock server + client** (pure Python, no external dependencies)

The API is intentionally a **mock** so the examples are runnable without external services.

## Audience

This sample is written for:
- Application developers integrating an LLM product into an app
- Platform/infra engineers who care about reliability, error modes, and versioning

## Quickstart (5 minutes)

### 1) Requirements

- Python 3.10+ (works on Windows/macOS/Linux)

### 2) Start the mock API server

From the repository root (or anywhere), run:

```bash
python -m project4_developer_docs_sample.examples.mock_server
```

If port 8080 is already in use, pick another port:

```bash
MOCK_API_PORT=8088 python -m project4_developer_docs_sample.examples.mock_server
```

You should see:

```text
Mock LLM Retrieval API listening on http://127.0.0.1:8080
```

### 3) Run the sample client

In a new terminal:

```bash
python -m project4_developer_docs_sample.examples.hello_client
```

If you changed the server port, point the client at it:

```bash
MOCK_API_BASE_URL=http://127.0.0.1:8088 python -m project4_developer_docs_sample.examples.hello_client
```

If you changed the server port, point the client at it:

```bash
MOCK_API_BASE_URL=http://127.0.0.1:8088 python -m project4_developer_docs_sample.examples.hello_client
```

Expected output (abridged):

```text
Health: ok
Upserted 3 docs
Query top result: (doc_id=doc-2, score=...)
Answer:
- ...
Citations:
- doc-2
- doc-1
```

## Documentation map

- **API reference:** `api_reference.md`
  - endpoints, request/response schemas, error handling, pagination, versioning
- **Tutorial:** `tutorial_rag.md`
  - how retrieval-augmented generation (RAG) fits together, what to log, how to evaluate

## Notes on realism

The mock server uses a simple bag-of-words similarity score (not embeddings) and returns citations. This is deliberate: it keeps the sample runnable while still demonstrating the core product surface area and the style of documentation.

## Style principles used in this sample

- **Developer-first:** quickstart before theory; examples before edge cases
- **Copy/pasteable:** code blocks are complete and runnable where possible
- **Explicit assumptions:** what is mock vs what is production-facing
- **Failure-aware:** clear error shapes and what to do next
- **Scannable:** short sections, consistent headings, and predictable layout
