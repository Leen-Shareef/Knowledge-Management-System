# rag_pipeline/llm_models.py (Switching to Ollama)

import os
from dotenv import load_dotenv
from langchain_community.llms import Ollama 
from langchain_core.language_models import BaseLanguageModel

# Load environment variables
load_dotenv()

# --- Configuration Constants ---
# Use the model name pulled with Ollama
GENERATION_MODEL_NAME = os.getenv("GENERATION_MODEL_NAME", "llama3") 


def initialize_llm() -> BaseLanguageModel:
    """
    Initializes and returns the Ollama LLM running locally.
    """
    print(f"[INFO] Attempting to connect to Ollama server for model: {GENERATION_MODEL_NAME}")
    try:
        # Ollama class connects to your locally running Ollama server
        # Ollama runs on port 11434 by default
        llm = Ollama(
            model=GENERATION_MODEL_NAME,
            base_url="http://localhost:11434"
        )
        # Quick check to ensure the connection is live
        llm.invoke("Hi") 
        
        print(f"[SUCCESS] Initialized LLM for generation via Ollama: {GENERATION_MODEL_NAME}")
        return llm
    except Exception as e:
        print(f"[ERROR] Failed to initialize Ollama LLM. Ensure Ollama application is running and the model is pulled.")
        print(f"Details: {e}")
        raise


if __name__ == "__main__":
    # Test initialization by invoking the model
    print("--- Running Ollama LLM Initialization Test ---")
    
    try:
        llm = initialize_llm()
        
        # Simple test query
        test_query = "What is the capital of France?"
        print(f"Query: {test_query}")
        
        # Note: Local API call here!
        response = llm.invoke(test_query)
        
        # Llama3 responses can be conversational, so we check if it's long enough
        if len(response.strip()) > 5:
            print(f"Response: {response.strip()[:100]}...")
            print("\nLLM Test successful (Local model responded).")
        else:
            print(f"Response: {response.strip()}")
            raise ValueError("Ollama responded, but the response was too short. Check model status.")
            
    except Exception as e:
        print(f"\n[FATAL] LLM Test failed.")