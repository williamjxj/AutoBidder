# Retrieval Tuning — MMR, Re-ranking & Advanced Strategies

## When to Tune

Tune retrieval when you notice:
- Proposals citing the same project repeatedly (low diversity in retrieved chunks)
- Relevant portfolio work being missed even though it exists
- Inconsistent quality across similar job types

---

## Maximal Marginal Relevance (MMR)

MMR trades off pure similarity for diversity — prevents the same case study
from dominating all retrieved slots.

ChromaDB doesn't have native MMR, but LangChain's `Chroma` wrapper does:

```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

vectorstore = Chroma(
    client=chromadb.HttpClient(host="localhost", port=8001),
    collection_name=f"portfolio_{user_id}",
    embedding_function=OpenAIEmbeddings(model="text-embedding-ada-002"),
)

# MMR retrieval
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 3,           # final chunks to return
        "fetch_k": 10,    # candidate pool to MMR-rank from
        "lambda_mult": 0.6,  # 0 = max diversity, 1 = max similarity
    },
)

chunks = retriever.get_relevant_documents(query)
```

**`lambda_mult` guide:**
- `0.8` — prioritize relevance (good for very specific queries)
- `0.6` — balanced (default recommendation)
- `0.4` — prioritize diversity (good for broad jobs with many requirements)

---

## Metadata-Weighted Re-ranking

After retrieval, boost chunks from recent high-value documents:

```python
from datetime import datetime

def rerank_by_recency(chunks_with_meta: list[tuple[str, dict]], decay: float = 0.05):
    """
    Boost chunks from recent years. decay=0.05 means a 2-year-old doc
    gets a ~10% score penalty vs a current one.
    """
    current_year = datetime.now().year
    scored = []
    for doc, meta, base_score in chunks_with_meta:
        doc_year = meta.get("year", current_year - 2)
        age_penalty = (current_year - doc_year) * decay
        final_score = base_score - age_penalty
        scored.append((doc, meta, final_score))
    
    return sorted(scored, key=lambda x: x[2], reverse=True)
```

---

## Hybrid Search (Keyword + Semantic)

For jobs with very specific tech requirements (e.g., "must have Stripe Connect
experience"), pure semantic search can miss exact matches. Combine with keyword filter:

```python
def hybrid_search(collection, query: str, required_tags: list[str], n_results: int = 3):
    """First filter by required tech tags, then rank by semantic similarity."""
    
    # Step 1: semantic search with a larger pool
    semantic = collection.query(
        query_texts=[query],
        n_results=20,
        where={"user_id": {"$eq": user_id}},
        include=["documents", "metadatas", "distances"],
    )
    
    # Step 2: re-filter to only chunks that have required tags
    filtered = []
    for doc, meta, dist in zip(
        semantic["documents"][0],
        semantic["metadatas"][0],
        semantic["distances"][0],
    ):
        stored_tags = meta.get("tech_tags", "").split(",")
        if any(tag.lower() in [t.lower() for t in stored_tags] for tag in required_tags):
            filtered.append((doc, meta, 1 - dist))
    
    # Step 3: return top-k from the filtered set
    filtered.sort(key=lambda x: x[2], reverse=True)
    return [doc for doc, _, _ in filtered[:n_results]]
```

---

## Chunk Size Trade-offs

| chunk_size | Effect | Best for |
|---|---|---|
| 200–300 | Very precise retrieval, low context volume | Short, specific portfolio bullets |
| 400–600 | Balanced (AutoBidder default) | Case studies, project summaries |
| 800–1200 | Rich context, lower precision | Long-form writing samples |

Changing chunk size requires a **full re-ingest** — embeddings are tied to the chunk text.

To re-ingest without losing data:
1. Export current metadata: `collection.get(include=["metadatas"])`
2. Delete old collection
3. Re-ingest with new splitter settings
4. Verify with `collection.count()` matches original doc count

---

## Cost Optimization

Embedding calls cost money. Reduce unnecessary re-embedding:

```python
# Before ingesting, check if the doc was already processed
def is_already_ingested(collection, filename: str, user_id: str) -> bool:
    result = collection.get(
        where={"$and": [
            {"user_id": {"$eq": user_id}},
            {"filename": {"$eq": filename}},
        ]},
        limit=1,
    )
    return len(result["ids"]) > 0
```

For large portfolios (100+ docs), cache embeddings to disk before inserting:
```python
import json, hashlib

def get_cache_key(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]

# Write: json.dump({key: embedding}, cache_file)
# Read: check cache before calling OpenAI
```
