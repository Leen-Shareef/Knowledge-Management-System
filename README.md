# 🧠 Enterprise Knowledge Management Agent (EKMA)

## Project Overview

The Enterprise Knowledge Management Agent (EKMA) is a secure, production-ready AI solution designed to serve as a central knowledge hub for internal organizations. Built using a **Retrieval-Augmented Generation (RAG)** architecture, it answers complex questions about company policies, procedures, and documentation with high accuracy, traceability, and role-based security.

This agent is built on a highly modular and scalable **FastAPI** backend, orchestrated by **LangChain**, and utilizes **ChromaDB** for vector storage.

## ✨ Key Features & Advanced Capabilities

This agent delivers the core required functionality plus the following advanced features for a best-in-class enterprise solution:

| Feature Category | Feature | Benefit |
| :--- | :--- | :--- |
| **RAG Core** | **Multi-Format Document Processing** | Seamless ingestion and chunking of **PDFs, DOCX, and XLSX** files into the knowledge base. |
| **Security** | **Role-Based Access Control (RBAC)** | Ensures users only retrieve documents relevant to their defined role/department, enforced during the retrieval step. |
| **Conversational** | **Agent Memory & Context Management** | Creates coherent multi-turn conversations by retaining chat history and session context. |
| **Automation** | **Tool Calling & Function Execution** | Enables the agent to execute custom API functions (e.g., department-specific queries) to retrieve real-time data or perform actions. |
| **Trust/Accuracy** | **Response Validation & Fact-Checking** | A secondary mechanism (LLM or heuristic) verifies the generated answer against the retrieved source documents to minimize hallucinations. |

## 📐 Architecture & Technology Stack

The EKMA follows a standard, scalable microservice architecture. 

### Core Stack

* **Backend API:** FastAPI (High-performance, async Python web framework).
* **LLM Orchestration:** LangChain (For defining the RAG flow, agent, and tool usage).
* **Generative Model:** GPT-5 Nano (Chosen for best-in-class cost-efficiency and speed).
* **Vector Database:** ChromaDB (Persistence for document embeddings).
* **Data Persistence:** SQLModel / PostgreSQL (For storing chat history, user metadata, and document records).
* **Server:** Uvicorn (ASGI server for running the FastAPI application).

