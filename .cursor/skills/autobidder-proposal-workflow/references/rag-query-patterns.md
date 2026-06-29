# RAG Query Patterns — ChromaDB / LangChain

## Query Construction Rules

1. **Always run 2–3 queries per job posting**, not one broad query
2. **Decompose by skill cluster**, not by job section
3. **Use outcome-focused phrasing** — ChromaDB retrieves by semantic similarity, 
   so "built e-commerce checkout" retrieves better than "e-commerce experience"

## Query Templates by Job Type

### SaaS / Dashboard Build
```python
queries = [
    f"{primary_tech} SaaS dashboard development",
    f"React data visualization project",
    f"subscription billing backend integration"
]
```

### API / Backend Job
```python
queries = [
    f"FastAPI REST API design",
    f"PostgreSQL database optimization",
    f"third-party API integration Python"
]
```

### Full-Stack Web App
```python
queries = [
    f"Next.js full-stack web application",
    f"user authentication JWT implementation",
    f"deployment Docker production"
]
```

### Mobile / Cross-Platform
```python
queries = [
    f"React Native mobile app development",
    f"cross-platform iOS Android project"
]
```

---

## Metadata Filtering

ChromaDB supports `where` clause filtering. Use these filters to narrow retrieval:

```python
# Only portfolio projects (not resume bullet points)
where={"doc_type": {"$in": ["portfolio", "case_study"]}}

# Filter by technology tag (if your ingestion pipeline adds these)
where={"$and": [
    {"doc_type": {"$eq": "portfolio"}},
    {"tech_tags": {"$contains": "Next.js"}}
]}

# Prioritize recent projects
where={"year": {"$gte": 2022}}
```

---

## Similarity Threshold Guide

| Score | Meaning | Action |
|-------|---------|--------|
| ≥ 0.85 | Strong match | Use directly in proposal |
| 0.70–0.84 | Reasonable match | Use with light editing |
| 0.50–0.69 | Weak match | Mention only if no better option |
| < 0.50 | No relevant content | Tell user to upload better portfolio docs |

---

## Debugging Poor Retrieval

If proposals are getting bad context, check these in order:

1. **Collection populated?**
   ```bash
   curl http://localhost:8000/api/knowledge/stats
   # Should return doc_count > 0
   ```

2. **Embedding model mismatch?**
   ChromaDB and LangChain must use the same embedding model.
   Default in AutoBidder: `text-embedding-ada-002` (OpenAI)
   
3. **Chunk size too large?**
   Portfolio docs should be chunked at 500–800 tokens with 100-token overlap.
   Large chunks hurt retrieval precision.

4. **Query too generic?**
   Replace "web development experience" with "Next.js e-commerce storefront built 2023"

5. **Wrong collection?**
   Check user_id scoping — each user has their own ChromaDB collection.
   Verify `collection_name = f"portfolio_{user_id}"` in the backend.
