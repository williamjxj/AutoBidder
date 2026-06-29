# Ingestion Pipeline — LangChain + ChromaDB

## Full Ingestion Service

```python
# backend/app/services/knowledge_service.py

import asyncio
from pathlib import Path
from typing import Literal

import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, Docx2txtLoader,
    UnstructuredMarkdownLoader, WebBaseLoader,
)
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings

DocType = Literal["portfolio", "resume", "case_study", "testimonial"]

class KnowledgeService:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
        )
        self.collection = self.client.get_or_create_collection(
            name=f"portfolio_{user_id}",
            metadata={"hnsw:space": "cosine"},  # cosine similarity
        )
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=settings.OPENAI_API_KEY,
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=80,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    async def ingest_file(
        self,
        file_path: str,
        doc_type: DocType = "portfolio",
        filename: str | None = None,
    ) -> dict:
        """Load, chunk, embed, and store a document. Returns ingestion stats."""
        
        # 1. Load
        docs = self._load_document(file_path)
        full_text = "\n\n".join(d.page_content for d in docs)
        
        # 2. Dedup check — skip if already ingested
        fname = filename or Path(file_path).name
        existing = self.collection.get(where={"filename": {"$eq": fname}})
        if existing["ids"]:
            return {"status": "skipped", "reason": "already_ingested", "filename": fname}
        
        # 3. Chunk
        chunks = self.splitter.split_text(full_text)
        
        # 4. Build metadata for each chunk
        tech_tags = extract_tech_tags(full_text)
        year = extract_year(full_text) or 2024
        metadatas = [
            {
                "user_id": self.user_id,
                "doc_type": doc_type,
                "filename": fname,
                "tech_tags": ",".join(tech_tags),  # ChromaDB stores as string
                "year": year,
                "chunk_index": i,
                "source": "upload",
            }
            for i in range(len(chunks))
        ]
        
        # 5. Embed + store (batch with rate-limit protection)
        ids = [f"{self.user_id}_{fname}_{i}" for i in range(len(chunks))]
        embeddings = await self._embed_with_retry(chunks)
        
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )
        
        return {
            "status": "success",
            "filename": fname,
            "chunks_stored": len(chunks),
            "tech_tags": tech_tags,
        }

    def _load_document(self, file_path: str):
        ext = Path(file_path).suffix.lower()
        loaders = {
            ".pdf":  PyPDFLoader,
            ".txt":  TextLoader,
            ".docx": Docx2txtLoader,
            ".md":   UnstructuredMarkdownLoader,
        }
        loader_cls = loaders.get(ext)
        if not loader_cls:
            raise ValueError(f"Unsupported file type: {ext}")
        return loader_cls(file_path).load()

    async def _embed_with_retry(self, chunks: list[str], batch_size: int = 20):
        """Embed in batches with backoff to avoid OpenAI rate limits."""
        all_embeddings = []
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            embeddings = await asyncio.to_thread(
                self.embeddings.embed_documents, batch
            )
            all_embeddings.extend(embeddings)
            if i + batch_size < len(chunks):
                await asyncio.sleep(0.3)  # gentle rate-limit buffer
        return all_embeddings

    async def search(
        self,
        query: str,
        n_results: int = 3,
        doc_type_filter: list[str] | None = None,
        min_similarity: float = 0.72,
    ) -> list[str]:
        """Retrieve top-k chunks for a query. Returns filtered, deduped chunks."""
        where = {"user_id": {"$eq": self.user_id}}
        if doc_type_filter:
            where["doc_type"] = {"$in": doc_type_filter}
        
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results + 2, self.collection.count() or 1),
            where=where,
            include=["documents", "distances"],
        )
        
        return [
            doc
            for doc, dist in zip(results["documents"][0], results["distances"][0])
            if (1 - dist) >= min_similarity
        ][:n_results]
```

---

## Tech Tag Extractor

```python
# Simple keyword scan — extend this list as your stack grows
TECH_KEYWORDS = [
    "React", "Next.js", "Vue", "Angular", "Svelte",
    "FastAPI", "Django", "Flask", "Node.js", "Express",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite",
    "TypeScript", "JavaScript", "Python", "Go", "Rust",
    "AWS", "GCP", "Azure", "Vercel", "Railway", "Docker",
    "Stripe", "Twilio", "Resend", "OpenAI", "LangChain",
    "ChromaDB", "Pinecone", "Weaviate",
    "TailwindCSS", "shadcn", "Material UI", "Chakra UI",
]

def extract_tech_tags(text: str) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in TECH_KEYWORDS if kw.lower() in text_lower]
```

---

## FastAPI Upload Endpoint

```python
# backend/app/routers/knowledge.py
from fastapi import APIRouter, UploadFile, File, Form, Depends
import tempfile, shutil

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(default="portfolio"),
    current_user: User = Depends(get_current_user),
):
    allowed = {".pdf", ".txt", ".md", ".docx"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(400, detail=f"File type {ext} not supported")
    
    # Write to temp file (LangChain loaders need a file path)
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        svc = KnowledgeService(user_id=str(current_user.id))
        result = await svc.ingest_file(tmp_path, doc_type=doc_type, filename=file.filename)
        return result
    finally:
        Path(tmp_path).unlink(missing_ok=True)
```
