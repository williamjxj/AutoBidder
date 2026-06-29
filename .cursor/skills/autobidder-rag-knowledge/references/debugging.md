# Debugging RAG Retrieval — Query Traces & Diagnosis

## Full Debug Script

Run this against a live ChromaDB to trace exactly what the proposal generator sees:

```python
#!/usr/bin/env python3
"""
Usage: python debug_retrieval.py --user_id <id> --query "Next.js SaaS dashboard"
"""
import argparse
import chromadb

def debug_retrieval(user_id: str, query: str, n_results: int = 5):
    client = chromadb.HttpClient(host="localhost", port=8001)
    
    try:
        collection = client.get_collection(f"portfolio_{user_id}")
    except Exception:
        print(f"❌ Collection 'portfolio_{user_id}' not found.")
        print("   → Upload at least one document first.")
        return

    total = collection.count()
    print(f"\n📚 Collection: portfolio_{user_id} ({total} chunks)")
    print(f"🔍 Query: '{query}'\n{'─'*60}")

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, total),
        include=["documents", "metadatas", "distances"],
        where={"user_id": {"$eq": user_id}},
    )

    docs      = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    if not docs:
        print("⚠️  No results returned. Collection may be empty or filtered out.")
        return

    for i, (doc, meta, dist) in enumerate(zip(docs, metadatas, distances)):
        score = 1 - dist
        bar   = "█" * int(score * 20)
        flag  = "✅" if score >= 0.72 else ("⚠️ " if score >= 0.50 else "❌")
        
        print(f"\n[{i+1}] {flag} Score: {score:.3f}  {bar}")
        print(f"     File: {meta.get('filename', 'unknown')} | "
              f"Type: {meta.get('doc_type')} | "
              f"Year: {meta.get('year')} | "
              f"Tags: {meta.get('tech_tags', '')}")
        print(f"     Preview: {doc[:200].replace(chr(10), ' ')}…")

    passing = sum(1 for d in distances if (1 - d) >= 0.72)
    print(f"\n{'─'*60}")
    print(f"Summary: {passing}/{len(docs)} chunks pass similarity threshold (≥0.72)")
    if passing == 0:
        print("💡 Suggestion: Try a more specific query, or upload more relevant docs.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--user_id", required=True)
    p.add_argument("--query",   required=True)
    p.add_argument("--n",       type=int, default=5)
    args = p.parse_args()
    debug_retrieval(args.user_id, args.query, args.n)
```

**Run it:**
```bash
# From repo root with backend deps available
docker compose exec backend python debug_retrieval.py \
  --user_id "abc123" \
  --query "Next.js e-commerce storefront project"
```

---

## Interpreting Results

### All scores < 0.50 — "No match at all"
The query and stored content are semantically unrelated.

Check: Does the collection even have docs about this topic?
```python
results = collection.peek(limit=10)
for doc in results["documents"]:
    print(doc[:100])
```
If the peeked docs aren't about the queried topic → **upload relevant content**.

---

### Scores 0.50–0.69 — "Weak match"
Retrieval found something related but not specific enough.

**Cause A: Query is too generic**
```python
# ❌ Too broad
"web development experience"

# ✅ More specific
"Next.js App Router SaaS application built for client"
```

**Cause B: Chunks are too large**
Large chunks dilute specificity. Reduce `chunk_size` from 600 → 400 and re-ingest.

**Cause C: Missing relevant docs**
The portfolio doesn't contain a project matching this job's tech. Tell the user.

---

### Scores ≥ 0.72 but proposal still feels generic

The retrieval is working — the problem is in how context is injected into the prompt.

Debug the prompt builder in `proposal_service.py`:
```python
# Add this temporarily to log what the LLM actually receives
print("=== CONTEXT SENT TO LLM ===")
for i, chunk in enumerate(context_chunks):
    print(f"[Chunk {i+1}] {chunk[:300]}")
print("=== END CONTEXT ===")
```

Common issues:
- Context chunks are being truncated before injection
- Prompt template has a bug placing context after the instruction (model ignores it)
- Model is using its training data instead of the injected context (system prompt
  needs stronger grounding instruction)

**Stronger grounding instruction:**
```
SYSTEM: You MUST base the "Relevant experience" section exclusively on the 
portfolio context provided below. Do not invent projects or outcomes not 
mentioned in the context. If the context doesn't contain relevant experience, 
say "I'm still building my portfolio in this area" rather than fabricating.
```

---

## Embedding Sanity Check

If you suspect embeddings are broken (all identical or all near-zero):

```python
from langchain_openai import OpenAIEmbeddings

emb = OpenAIEmbeddings(model="text-embedding-ada-002")

# Test two obviously different texts
e1 = emb.embed_query("Next.js React frontend dashboard")
e2 = emb.embed_query("PostgreSQL database schema migrations")

# Cosine similarity between them should be 0.70–0.85 (related but distinct)
import numpy as np
cos_sim = np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))
print(f"Cosine similarity: {cos_sim:.4f}")

# If this prints 1.0000 → embeddings are identical → API key broken / quota exceeded
# If this prints 0.0000 → embeddings are zero vectors → same issue
```

Expected output for healthy embeddings: `Cosine similarity: 0.7823` (approximately)
