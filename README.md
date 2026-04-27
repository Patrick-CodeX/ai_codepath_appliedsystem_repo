# Applied AI System: PawPal+ AI
**Loom Video Demo:** [[Loom Video](https://www.loom.com/share/b0759cf61fe94d46a049ad94ff28960e)]

## 1. Base Project & Original Scope
**Base Project:** PawPal+ (Module 2)
**Original Scope:** The original project was a Python scheduling algorithm that used standard Object-Oriented Programming (OOP) to help pet owners schedule tasks and detect time conflicts. It had no AI features.

## 2. New AI System Features
This project has been extended into an Applied AI System by adding:
1. **Retrieval-Augmented Generation (RAG):** An AI assistant powered by Groq (Llama 3.1) that retrieves information from a static safety knowledge base before answering user questions.
2. **Reliability Guardrails:** A dual-layer safety system. The AI blocks dangerous advice (e.g., toxic foods), while the Python backend algorithm blocks scheduling conflicts.

## 3. System Architecture Diagram
```mermaid
graph TD
    A[User Input / Question] --> B{App Layer: Streamlit}
    B --> C[Backend Logic: Scheduler / Conflict Check]
    B --> D[AI RAG System: Groq Llama 3.1]
    D --> E[(Static Knowledge Base)]
    E --> F[AI Guardrail Check]
    C --> G[Output to User]
    F --> G