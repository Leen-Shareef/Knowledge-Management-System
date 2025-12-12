# rag_pipeline/embedding_models.py

import os
from dotenv import load_dotenv
# --- CHANGED IMPORT ---
# We switched from 'langchain_huggingface' to 'langchain_community'
# This matches the stable LangChain 0.1.20 version we installed.
from langchain_community.embeddings import HuggingFaceEmbeddings
from functools import lru_cache 

load_dotenv()

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" 

@lru_cache(maxsize=1)
def initialize_embedding_model():
    """
    Initializes the HuggingFace Embedding Model.
    Uses @lru_cache to ensure we load the model ONLY ONCE into memory.
    """
    try:
        print(f"[INFO] Loading embedding model: {EMBEDDING_MODEL_NAME}...")
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'} 
        )
        print(f"[SUCCESS] Embedding model loaded.")
        return embeddings
    except Exception as e:
        print(f"[ERROR] Failed to initialize embedding model: {e}")
        raise