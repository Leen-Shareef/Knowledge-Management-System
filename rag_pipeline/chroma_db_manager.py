# rag_pipeline/chroma_db_manager.py

import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from typing import TYPE_CHECKING
import sys

# Load environment variables
load_dotenv()

# --- Configuration Constants ---
# These must match the variables set in your .env file
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "enterprise_knowledge_base")

def get_vector_store(embeddings: Embeddings):
    """
    Initializes and returns the Chroma vector store client.
    Creates the store if it doesn't exist, otherwise loads from disk.
    """
    if not os.path.exists(CHROMA_PERSIST_DIR):
        print(f"[INFO] Creating new persistent Chroma directory at {CHROMA_PERSIST_DIR}")
        try:
            os.makedirs(CHROMA_PERSIST_DIR)
        except OSError as e:
             print(f"[ERROR] Failed to create directory: {e}")
             sys.exit(1)


    # Use the Chroma client to connect to the persistent storage
    try:
        vector_store = Chroma(
            collection_name=CHROMA_COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=CHROMA_PERSIST_DIR
        )
        print(f"[INFO] Connected to ChromaDB collection: {CHROMA_COLLECTION_NAME}")
        return vector_store
    except Exception as e:
        print(f"[ERROR] Failed to connect to ChromaDB: {e}")
        raise

if __name__ == "__main__":
    # Corrected import using relative path (the dot)
    from .embedding_models import initialize_embedding_model
    
    print("--- Running ChromaDB Manager Test ---")
    
    # 1. Initialize the embedding function
    embeddings = initialize_embedding_model()
    
    # 2. Get the vector store connection
    db = get_vector_store(embeddings)
    
    # Check the count (should be 0 if the collection is new)
    print(f"Current document count in collection: {db._collection.count()}")