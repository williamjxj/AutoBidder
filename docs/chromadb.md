# ChromaDB — Vector Store for RAG

**Purpose:** Stores document embeddings for Knowledge Base RAG (proposal generation).

---

## Modes

| Mode | Config | Use Case |
|------|--------|----------|
| **Local** | `CHROMA_PERSIST_DIR=./chroma_db`, no `CHROMA_HOST` | Development |
| **Docker** | `CHROMA_HOST=localhost`, `CHROMA_PORT=8001` | Production, teams |

**Logic:** `CHROMA_HOST` wins. If set → HTTP client; else → PersistentClient. Falls back to local if Docker fails.

---

## Quick Config

**Local (dev):** Unset/comment `CHROMA_HOST`. Data in `backend/chroma_db/`.

**Docker:** `docker-compose up -d chromadb`. Set `CHROMA_HOST=localhost` and `CHROMA_PORT=8001` in `.env`.

---

## Upgrade to Docker

1. `pip install --upgrade chromadb` (v0.5+ for Docker v2 API)
2. Set `CHROMA_HOST=localhost`, `CHROMA_PORT=8001`
3. Restart backend

---

## Troubleshooting

- **Connection refused:** Ensure Docker ChromaDB is running (`docker ps | grep chromadb`).
- **v1 API deprecated:** Upgrade client to chromadb>=0.5.
- **Data after switch:** Local and Docker use separate storage; migrate if needed.
