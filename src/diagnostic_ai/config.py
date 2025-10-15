# # src/diagnostic_ai/config.py
# from pydantic_settings import BaseSettings
# from typing import Optional

# class Settings(BaseSettings):
#     # LLM Config
#     openai_api_key: str
#     openai_model: str = "gpt-4-turbo-preview"
    
#     # RAG Config
#     embedding_model: str = "text-embedding-3-small"
#     vector_store_path: str = "./data/vector_store"
#     chunk_size: int = 500
#     chunk_overlap: int = 50
    
#     # Agent Config
#     max_iterations: int = 10
#     temperature: float = 0.3
    
#     # Data Config
#     patient_data_path: str = "./data/patient_records"
    
#     class Config:
#         env_file = ".env"

# settings = Settings()


# 

# src/diagnostic_ai/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # LLM Config - Using Groq (FREE)
    groq_api_key: str
    llm_model: str = "llama-3.3-70b-versatile"
    
    # Embeddings - Using free HuggingFace
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # RAG Config
    vector_store_path: str = "./data/vector_store"
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Agent Config
    max_iterations: int = 10
    temperature: float = 0.3
    
    # Data Config
    patient_data_path: str = "./data/patient_records"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()