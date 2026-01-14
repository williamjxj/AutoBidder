from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from typing import List, Optional
from app.core.config import settings
import os


class LlamaIndexService:
    """Service for Llama Index operations."""
    
    def __init__(self):
        """Initialize Llama Index service."""
        self.embed_model = HuggingFaceEmbedding(
            model_name=settings.EMBEDDING_MODEL
        )
        
        self.llm = OpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Configure global settings
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        
        self.index = None
    
    def create_index_from_documents(self, documents: List[str]) -> VectorStoreIndex:
        """Create an index from a list of documents."""
        docs = [Document(text=doc) for doc in documents]
        
        self.index = VectorStoreIndex.from_documents(docs)
        
        return self.index
    
    def create_index_from_directory(self, directory_path: str) -> VectorStoreIndex:
        """Create an index from a directory of documents."""
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
            return None
        
        documents = SimpleDirectoryReader(directory_path).load_data()
        
        self.index = VectorStoreIndex.from_documents(documents)
        
        return self.index
    
    def query(self, query_text: str) -> str:
        """Query the index."""
        if not self.index:
            return "Index not initialized. Please create an index first."
        
        query_engine = self.index.as_query_engine()
        response = query_engine.query(query_text)
        
        return str(response)
    
    def get_relevant_context(self, query: str, top_k: int = 5) -> List[str]:
        """Get relevant context for a query."""
        if not self.index:
            return []
        
        retriever = self.index.as_retriever(similarity_top_k=top_k)
        nodes = retriever.retrieve(query)
        
        return [node.text for node in nodes]


# Singleton instance
llama_index_service = LlamaIndexService()
