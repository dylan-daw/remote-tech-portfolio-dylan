# Tutorial: Retrieval-Augmented Generation (RAG) with Citations

This tutorial explains (at a practical level) how an LLM product can answer questions **grounded** in your documents via retrieval, and how to make the behavior testable.

The mock server in this sample does not call a real LLM; it provides the same developer-facing surface area:
- you can **upsert documents**
- run **retrieval queries**
- request an **answer with citations**

## Goal

By the end, you will:
1) index a small document set
2) ask a question
3) receive an answer with citations
4) understand what to log and how to evaluate truthfulness

## Key concepts

### 1) Chunking

In production, long documents are split into chunks (e.g., 300–800 tokens) to improve retrieval granularity.

### 2) Embeddings & vector search

A vector database stores embeddings (numeric vectors) for each chunk. At query time, you embed the query and retrieve nearest neighbors.

### 3) Grounded answering

You pass retrieved chunks into the LLM as context. The LLM is instructed to answer using only that context and to provide citations.

### 4) Citations are a product feature

Citations make answers auditable:
- users can click what the model used
- reviewers can spot missing evidence
- you can measure hallucination rates

## Step-by-step (using the mock server)

### 1) Start the server

```bash
python -m project4_developer_docs_sample.examples.mock_server
```

### 2) Index documents

The sample client inserts three docs. You can edit them inside `examples/hello_client.py`.

Run:

```bash
python -m project4_developer_docs_sample.examples.hello_client
```

### 3) Ask a question

The client calls `/v1/answer`:

```json
{
  "question": "How can I stop a small fire?",
  "top_k": 3
}
```

The response includes:
- `answer`: a grounded summary
- `citations`: doc_ids used
- `results`: the retrieved context

## What to log (minimum viable observability)

When debugging epistemic rigor, you want to know:
- the **exact prompt/context** used to generate an answer
- which docs were retrieved (ids + scores)
- whether the answer contains claims **not supported** by retrieved context
- latency, timeouts, and error codes

A simple log record (per request):
- request id
- user question
- retrieved doc_ids + scores
- model config (temperature, max tokens, etc.)
- final answer + citations

## Evaluation: truthfulness & rigor checklist

Use a consistent rubric:

1) **Claim/evidence separation**
   - Are factual claims grounded in retrieved text?
2) **Calibration**
   - Does the assistant express uncertainty when evidence is weak?
3) **Coverage**
   - Are important counterpoints missing from the context?
4) **Overreach**
   - Does it infer beyond the evidence?
5) **Actionability**
   - If giving guidance, does it add constraints/safety checks?

## Failure modes (and mitigations)

- **Bad retrieval**: context doesn’t contain the needed evidence
  - Mitigate with better chunking, metadata filters, hybrid search, re-ranking

- **Hallucination**: answer includes unsupported claims
  - Mitigate with stricter grounding prompts, citation enforcement, refusal patterns

- **Context overload**: too much text harms generation
  - Mitigate with top-k tuning, summarizing retrieved chunks, hierarchical retrieval

## Next steps

- Add metadata filters (e.g., language, product version)
- Add idempotency keys for upsert
- Add a second retrieval strategy (BM25 + cosine hybrid)
- Add a test suite that checks: "all claims in answer trace to citations"
