from typing import List, Optional
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from app.core.config import settings
import os


class VectorStoreService:
    """Service for managing vector store operations."""
    
    def __init__(self):
        """Initialize the vector store service."""
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )
        
        # Ensure persist directory exists
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        
        self.vectorstore = Chroma(
            persist_directory=settings.CHROMA_PERSIST_DIR,
            embedding_function=self.embeddings
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )
    
    def add_documents(self, texts: List[str], metadatas: Optional[List[dict]] = None):
        """Add documents to the vector store."""
        # Split texts into chunks
        documents = []
        for i, text in enumerate(texts):
            chunks = self.text_splitter.split_text(text)
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            
            for chunk in chunks:
                documents.append(Document(
                    page_content=chunk,
                    metadata=metadata
                ))
        
        # Add to vector store
        self.vectorstore.add_documents(documents)
        self.vectorstore.persist()
        
        return len(documents)
    
    def similarity_search(self, query: str, k: int = None) -> List[Document]:
        """Search for similar documents."""
        k = k or settings.TOP_K_RESULTS
        results = self.vectorstore.similarity_search(query, k=k)
        return results
    
    def similarity_search_with_score(self, query: str, k: int = None):
        """Search for similar documents with relevance scores."""
        k = k or settings.TOP_K_RESULTS
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return results
    
    def clear(self):
        """Clear all documents from the vector store."""
        self.vectorstore.delete_collection()
        self.vectorstore = Chroma(
            persist_directory=settings.CHROMA_PERSIST_DIR,
            embedding_function=self.embeddings
        )


# Singleton instance
vector_store_service = VectorStoreService()
