# src/diagnostic_ai/rag/retriever.py (Simplified - No FAISS, No Pickle)
from diagnostic_ai.rag.embeddings import get_embeddings
from diagnostic_ai.config import settings
from typing import List
import numpy as np

class MedicalKnowledgeRAG:
    def __init__(self):
        self.embeddings = get_embeddings()
        self.documents = []
        self.doc_embeddings = []
    
    def build_knowledge_base(self, documents: List[str]):
        """Build simple in-memory vector store"""
        print("📚 Building knowledge base...")
        self.documents = documents
        self.doc_embeddings = self.embeddings.embed_documents(documents)
        print(f"✓ Indexed {len(documents)} medical documents")
    
    def load_knowledge_base(self):
        """Load existing vector store (no-op for in-memory)"""
        pass
    
    def retrieve_relevant_docs(self, query: str, k: int = 3) -> List[str]:
        """Retrieve top-k relevant documents using cosine similarity"""
        if not self.documents:
            return ["No medical guidelines available."]
        
        query_embedding = self.embeddings.embed_query(query)
        
        # Cosine similarity
        similarities = []
        for doc_emb in self.doc_embeddings:
            similarity = np.dot(query_embedding, doc_emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb) + 1e-10
            )
            similarities.append(similarity)
        
        # Get top-k indices
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        
        return [self.documents[i] for i in top_k_indices]
    
    def get_retriever(self):
        """Return retriever interface"""
        return self