# rag_pipeline/utils.py

import os
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter 

# We only need PyPDFLoader now
from langchain_community.document_loaders import PyPDFLoader 

from langchain_core.documents import Document

# --- Configuration ---
# MODIFIED: Smaller chunks for higher precision on fact-based queries
CHUNK_SIZE = 400  
CHUNK_OVERLAP = 50  # ~12.5% overlap

def get_rbac_metadata(file_path: str) -> Dict[str, str]:
    """
    Determines the appropriate Role-Based Access Control (RBAC) metadata 
    based on the document's filename or category.
    """
    filename = os.path.basename(file_path).lower()
    
    # --- RBAC Logic ---
    if "hr_policy" in filename or "employee_handbook" in filename or "diversity_inclusion" in filename:
        return {"role": "HR_Employee", "department": "HR"}
    elif "it_security" in filename:
        return {"role": "IT_Tech", "department": "IT"}
    elif "sales_playbook" in filename or "client_case_studies" in filename:
        return {"role": "Sales_Team", "department": "Sales"}
    else:
        # Default for general policies (e.g., Company Overview)
        return {"role": "General_Employee", "department": "General"}

def load_and_split_documents(data_path: str = "data") -> List[Document]:
    """
    Loads ONLY PDF documents from the data directory, assigns metadata, 
    and splits them into uniform chunks for vector storage.
    """
    all_documents = []
    
    # Initialize the text splitter with the new smaller size
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    for root, _, files in os.walk(data_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            # Skip non-PDF files explicitly
            if not file_name.endswith('.pdf'):
                continue

            # 1. Load Document
            loader = PyPDFLoader(file_path)

            try:
                document_data = loader.load()
            except Exception as e:
                print(f"Error loading {file_name}: {e}")
                continue

            # 2. Assign Metadata (RBAC, source file name, etc.)
            base_metadata = get_rbac_metadata(file_path)
            
            for doc in document_data:
                # Merge the RBAC metadata into the document's metadata
                doc.metadata.update(base_metadata)
                doc.metadata['source'] = file_name 

            # 3. Split Document into Chunks
            chunks = text_splitter.split_documents(document_data)
            all_documents.extend(chunks)
            print(f"Processed {len(document_data)} pages/sections from {file_name} into {len(chunks)} chunks.")

    return all_documents

if __name__ == "__main__":
    # Test to verify the new chunk sizes
    print("--- Running Utils Test (Small Chunks) ---")
    documents = load_and_split_documents()
    print(f"\nTotal Chunks created: {len(documents)}")
    if documents:
        print("\nExample Chunk Metadata:")
        hr_chunk = next((doc for doc in documents if doc.metadata.get('department') == 'HR'), documents[0])
        print(f"Content Length: {len(hr_chunk.page_content)} characters") # Verify size is close to 400
        print(f"Content Start: '{hr_chunk.page_content[:100]}...'")