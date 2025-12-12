# rag_pipeline/ingestion_script.py

import os
import sys
from dotenv import load_dotenv

# Use relative imports to fetch our core components
from .utils import load_and_split_documents
from .embedding_models import initialize_embedding_model
from .chroma_db_manager import get_vector_store

# Load environment variables
load_dotenv()

# --- Configuration ---
DATA_PATH = "data"

def run_ingestion():
    """
    Executes the full RAG indexing pipeline:
    1. Loads and splits documents with RBAC metadata.
    2. Initializes the embedding model.
    3. Connects to the ChromaDB vector store.
    4. Adds all document chunks to the vector store.
    """
    if not os.path.exists(DATA_PATH) or not os.listdir(DATA_PATH):
        print(f"[FATAL] Data directory '{DATA_PATH}' is empty or does not exist.")
        print("Please run the download_data.py script first.")
        sys.exit(1)

    print("--- Starting RAG Ingestion Pipeline ---")
    
    # 1. Load, Split, and Tag Documents
    print("[STEP 1/4] Loading and splitting documents with RBAC tags...")
    chunks = load_and_split_documents(data_path=DATA_PATH)
    if not chunks:
        print("[FATAL] No chunks were created. Aborting ingestion.")
        sys.exit(1)
        
    print(f"[SUCCESS] Total documents processed into {len(chunks)} chunks.")

    # 2. Initialize Embedding Model
    print("\n[STEP 2/4] Initializing embedding model...")
    embeddings = initialize_embedding_model()
    print("[SUCCESS] Embedding model ready.")
    
    # 3. Connect to Vector Store
    print("\n[STEP 3/4] Connecting to ChromaDB vector store...")
    vector_store = get_vector_store(embeddings)
    initial_count = vector_store._collection.count()
    print(f"[INFO] Current document count in DB: {initial_count}")

    # Check if the collection is already populated (optional but helpful)
    if initial_count > 0 and input("Collection is not empty. Proceed with adding new data? (y/n): ").lower() != 'y':
        print("[INFO] Aborting ingestion at user request.")
        return

    # 4. Add Documents to Vector Store
    print("\n[STEP 4/4] Adding new document chunks to ChromaDB...")
    
    # LangChain's add_documents handles the embedding process automatically
    # The RBAC metadata is automatically stored alongside the vectors
    vector_store.add_documents(chunks)
    
    final_count = vector_store._collection.count()
    print(f"[SUCCESS] Ingestion complete. Documents added: {final_count - initial_count}")
    print(f"Final document count in ChromaDB: {final_count}")
    print("\n--- RAG Knowledge Base is ready for retrieval! ---")


if __name__ == "__main__":
    run_ingestion()