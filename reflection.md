# Project Reflection: Building PawPal+ AI

## 1. Working with AI
I used AI to help me bridge the gap between my original Module 2 Python code and this new Streamlit version. It was especially helpful for figuring out `st.session_state` so my pet data wouldn't disappear every time the page refreshed. 

However, I ran into a major roadblock when the AI suggested using an older Groq model (`llama3-8b-8192`). I kept getting "model decommissioned" errors (400) because that model was no longer supported. I had to manually check the Groq documentation to find the correct model name, `llama-3.1-8b-instant`. This was a good reminder that AI suggestions can quickly become outdated, and I have to be ready to debug the API documentation myself. Gemini and OpenAI constantly didn't work.

## 2. System Guardrails & Limits
The biggest limitation right now is the knowledge base. Since it's just a static text block, the AI only knows the specific safety rules I've typed in. If a user asks about a rare pet or a specific medical condition not in that list, the AI might give a generic answer instead of a specialized one. 

To make the system more reliable, I added a "soft guardrail" in the scheduling logic. Instead of just letting the user make a mistake, my code checks if two tasks share a time slot and triggers a red conflict warning. I wanted to make sure the app wasn't just a chatbot, but a tool that actually helps catch human errors.

## 3. What's Next?
If I were to keep building this, I’d move away from a static text block and use a real vector database. This would allow me to upload entire PDF manuals for different animals, which would make the "Retrieval" part of the RAG system much more powerful. I'd also like to add a feature where the AI can automatically suggest a time for a task based on the pet's specific needs.