# rag_pipeline/retrieval_chain.py

from typing import List, Dict, Any
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Import components
from rag_pipeline.embedding_models import initialize_embedding_model
from rag_pipeline.chroma_db_manager import get_vector_store
from rag_pipeline.llm_models import initialize_llm 
from app.services.memory_service import load_message_history 

# --- UPDATED & POLISHED SYSTEM PROMPT ---
RAG_PROMPT_TEMPLATE = """
You are the Enterprise Knowledge Agent for KNAgent. 
Your goal is to provide accurate, natural, and professional answers based ONLY on the provided context.

CONTEXT (Securely filtered):
{context}

CHAT HISTORY:
{chat_history}

USER QUESTION: {question}

INSTRUCTIONS:
1. **Response Style:** Answer naturally and smoothly. Do NOT mention "Document id", "metadata", or "chunks". 
   - BAD: "In Document(id='123')..."
   - GOOD: "According to the IT policy..."
2. **Synthesis:** Combine information from multiple sections into a single coherent paragraph or bulleted list.
3. **No Outside Knowledge:** Answer ONLY using the provided context.
4. **Handling Missing Info:**
   - If the question is about **HR, Leave, Probation, or Benefits** and you don't see the answer: 
     State: "I do not have access to this information based on your current role permissions. Please contact the HR Department directly."
   - If the question is about **IT, Security, or Passwords** and you don't see the answer: 
     State: "This information appears to be restricted. Please contact IT Support."
   - For other queries, state: "I cannot find this information in the documents available to your role."

Answer:
"""

# --- Secure Retriever Setup (Unchanged) ---
def create_retriever(user_role: str):
    embeddings = initialize_embedding_model()
    vector_store = get_vector_store(embeddings)
    
    rbac_filter = {"role": user_role}
    
    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": 5,
            "filter": rbac_filter
        }
    )
    return retriever

# --- Full Retrieval Chain Construction (Unchanged) ---
def create_rag_chain(user_id: str, session_id: str, user_role: str):
    llm = initialize_llm()
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
    retriever = create_retriever(user_role)
    
    # Mock session for memory loading
    from app.database.database import get_session
    db_session_gen = get_session()
    db_session = next(db_session_gen)
    
    chat_history_list = load_message_history(db_session, session_id=session_id)
    chat_history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history_list])
    
    rag_chain = (
        RunnablePassthrough.assign(
            context=(lambda x: x['question']) | retriever,
            chat_history=lambda x: chat_history_str 
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain