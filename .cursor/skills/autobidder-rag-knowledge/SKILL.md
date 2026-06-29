---
name: autobidder-rag-knowledge
description: >
  Guides Claude when managing, debugging, or improving AutoBidder's RAG knowledge
  base pipeline. Use this skill whenever the user mentions: "knowledge base", "RAG",
  "ChromaDB", "embeddings", "document upload", "retrieval", "the AI isn't using the
  right context", "portfolio docs", "LangChain", "chunking", "vector store", "bad
  proposals", or "why did it generate that". Also trigger when the user wants to
  upload new portfolio documents, inspect what's in the knowledge base, tune retrieval
  quality, debug why a proposal got irrelevant context, or rebuild/reset the vector
  store. Always consult this skill before touching anything in
  backend/app/services/knowledge_service.py or the ChromaDB collection — it encodes
  all ingestion, retrieval, and debugging patterns for this project.
---

# AutoBidder — RAG Knowledge Base Guide

The knowledge base is the core of AutoBidder's personalization. A proposal is only
as good as the portfolio context retrieved for it. This skill covers the full pipeline:
ingest → store → retrieve → debug → tune.

## Pipeline Overview

```
Portfolio Doc (PDF/MD/TXT)
    ↓
[1] Load  →  LangChain DocumentLoader
    ↓
[2] Chunk →  RecursiveCharacterTextSplitter
    ↓
[3] Embed →  OpenAI text-embedding-ada-002
    ↓
[4] Store →  ChromaDB (collection per user)
    ↓
[5] Query →  Similarity search → top-k chunks → proposal prompt
```

---

## Step 1 — Identify the Task

| User says… | Go to |
|---|---|
| "upload my portfolio / resume / case study" | Step 2: Ingestion |
| "what's in my knowledge base?" | Step 3: Inspection |
| "the proposal got wrong context" / "bad retrieval" | Step 4: Debugging |
| "improve retrieval quality" / "tune top-k" | Step 5: Tuning |
| "reset / rebuild the knowledge base" | Step 6: Collection Management |

---

## Step 2 — Document Ingestion

Read `references/ingestion.md` for the full ingestion pipeline.

**Quick reference — loader selection:**

| File type | LangChain Loader | Notes |
|---|---|---|
| `.pdf` | `PyPDFLoader` | Best for resumes, case studies |
| `.md` | `UnstructuredMarkdownLoader` | Good for README-style portfolios |
| `.txt` | `TextLoader` | Plain text bios, project summaries |
| `.docx` | `Docx2txtLoader` | Word documents |
| Web URL | `WebBaseLoader` | Portfolio websites, LinkedIn |

**Chunking config (canonical AutoBidder settings):**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,       # tokens ≈ 450 words — enough context, not too diluted
    chunk_overlap=80,     # overlap preserves continuity across chunk boundaries
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""],
)
```

**Metadata to attach at ingestion time** (critical for filtering later):
```python
metadata = {
    "user_id": user.id,
    "doc_type": "portfolio",          # portfolio | resume | case_study | testimonial
    "filename": original_filename,
    "tech_tags": extract_tech_tags(text),  # ["Next.js", "FastAPI", "PostgreSQL"]
    "year": extract_year(text) or 2024,
    "source": "upload",
}
```

Always set `user_id` in metadata — it's how the query layer scopes results to the
correct user. Missing `user_id` = cross-user retrieval contamination.

---

## Step 3 — Inspecting the Knowledge Base

Backend endpoint: `GET /api/knowledge/stats`

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/knowledge/stats
```

Expected response shape:
```json
{
  "collection_name": "portfolio_<user_id>",
  "doc_count": 47,
  "doc_types": { "portfolio": 32, "resume": 8, "case_study": 7 },
  "tech_tags": ["Next.js", "FastAPI", "React", "PostgreSQL"],
  "oldest_doc": "2022-01-15",
  "newest_doc": "2024-11-02"
}
```

**Inspect raw chunks** (direct ChromaDB — useful for debugging):
```python
import chromadb

client = chromadb.HttpClient(host="localhost", port=8001)
collection = client.get_collection(f"portfolio_{user_id}")

# Peek at stored documents
results = collection.peek(limit=5)
print(results["documents"])   # chunk text
print(results["metadatas"])   # metadata dicts
print(results["ids"])         # chunk IDs

# Count total
print(collection.count())
```

---

## Step 4 — Debugging Poor Retrieval

When a proposal gets bad context, work through this checklist in order.

### 4a. Run the retrieval manually
```python
results = collection.query(
    query_texts=["Next.js SaaS dashboard project"],
    n_results=5,
    include=["documents", "metadatas", "distances"],
)
for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
    print(f"Score: {1 - dist:.3f} | Type: {meta.get('doc_type')} | {doc[:120]}...")
```

Scores below 0.70 → the query didn't match anything relevant → see 4b/4c.

### 4b. Diagnose the root cause

| Symptom | Likely cause | Fix |
|---|---|---|
| All scores < 0.50 | No relevant content ingested | Upload better portfolio docs |
| Good scores but wrong content | Query too generic | Use more specific query text |
| Right topic, wrong project | Old/stale chunks dominating | Delete old docs, re-ingest |
| Scores look fine but proposal ignores context | Prompt injection issue | Check `build_prompt()` in `proposal_service.py` |
| Different users' content appearing | Missing `user_id` in metadata | Re-ingest with correct metadata |

### 4c. Check embedding model consistency
The same model must be used at ingestion AND query time. In AutoBidder:
```python
# Both must use this — if mismatched, all similarity scores will be garbage
embedding_fn = OpenAIEmbeddings(model="text-embedding-ada-002")
```

If you suspect a mismatch: delete the collection and re-ingest everything.

Read `references/debugging.md` for query trace walkthrough and advanced diagnosis.

---

## Step 5 — Tuning Retrieval Quality

### top-k selection
```python
# Default in knowledge_service.py
n_results = 3   # good balance: enough context, stays under prompt token budget

# When to increase:
# - Job has many distinct skill requirements
# - Portfolio is large (50+ docs)
n_results = 5

# When to decrease:
# - Proposals are getting too long / incoherent
# - Token budget is tight (GPT-4 cost pressure)
n_results = 2
```

### Similarity threshold gating
Don't inject low-quality chunks into the prompt — they hurt more than they help:
```python
MIN_SIMILARITY = 0.72

def filter_results(results):
    docs, scores = results["documents"][0], results["distances"][0]
    return [
        doc for doc, dist in zip(docs, scores)
        if (1 - dist) >= MIN_SIMILARITY
    ]
```

### Multi-query retrieval (for complex jobs)
When a job has multiple distinct requirement clusters, run separate queries
and deduplicate — one broad query misses specifics:
```python
queries = [
    f"{primary_tech} project portfolio",
    f"{project_type} case study outcome",
    f"{domain} freelance development",
]
all_chunks = []
seen_ids = set()
for q in queries:
    r = collection.query(query_texts=[q], n_results=2)
    for doc, id_ in zip(r["documents"][0], r["ids"][0]):
        if id_ not in seen_ids:
            all_chunks.append(doc)
            seen_ids.add(id_)
```

Read `references/tuning.md` for MMR (maximal marginal relevance) setup and
metadata-weighted re-ranking patterns.

---

## Step 6 — Collection Management

### Delete a specific document (by filename)
```python
collection.delete(where={"filename": {"$eq": "old_resume_2021.pdf"}})
```

### Delete all docs of a type
```python
collection.delete(where={"doc_type": {"$eq": "resume"}})
```

### Full reset (nuke and re-ingest)
```bash
# Via API
curl -X DELETE -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/knowledge/reset

# Direct (dev only)
python -c "
import chromadb
c = chromadb.HttpClient(host='localhost', port=8001)
c.delete_collection('portfolio_<user_id>')
print('Collection deleted')
"
```

After a reset, re-upload all portfolio documents through the UI or API.

---

## Common Failure Modes

| Problem | Fix |
|---|---|
| `chromadb.errors.NotFoundError` | Collection doesn't exist yet — upload at least one doc first |
| `openai.RateLimitError` during ingestion | Batch embed with delay: `asyncio.sleep(0.5)` between chunks |
| Duplicate chunks on re-upload | Check for existing docs by filename before ingesting: `collection.get(where={"filename": ...})` |
| ChromaDB container not running | `docker compose up chromadb` |
| Embeddings all identical | API key wrong or quota exceeded — embeddings silently return zeros |
