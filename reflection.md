---

### 4. `reflection.md`
Replace everything in your `reflection.md` with this:

```markdown
# System Reflection & AI Collaboration

## 1. AI Collaboration & Development
During this project, I collaborated extensively with AI to evolve a standard Python script into a full Applied AI System.
*   **Helpful Suggestion:** The AI was highly effective in helping me structure the Streamlit UI and convert my standard Python logic into a stateful web app using `st.session_state`.
*   **Flawed Suggestion:** When setting up the AI API connections, the AI initially suggested a deprecated Groq model (`llama3-8b-8192`) which caused a 400 error. I had to debug the API documentation to find the updated `llama-3.1-8b-instant` model to restore functionality.

## 2. System Limitations & Guardrails
*   **Limitations:** The current RAG system relies on a static text block (`PET_KNOWLEDGE`). If a user asks about a safety issue not in that exact text block, the AI cannot dynamically search the internet for a safe answer.
*   **Guardrails:** I implemented strict backend guardrails for time scheduling to ensure overlapping tasks trigger a red UI warning to the user.

## 3. Future Improvements
If I were to extend this further, I would implement **Multi-Source Retrieval**. Instead of a single text block, the system would use a vector database to search through full veterinary PDFs, allowing for much more nuanced and detailed health advice.