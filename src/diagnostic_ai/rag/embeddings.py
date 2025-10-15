# src/diagnostic_ai/rag/embeddings.py
from langchain_community.embeddings import HuggingFaceEmbeddings
from diagnostic_ai.config import settings

def get_embeddings():
    """Initialize embeddings model - FREE HuggingFace"""
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )