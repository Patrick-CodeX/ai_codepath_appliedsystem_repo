import streamlit as st
from groq import Groq
from dataclasses import dataclass, field
from typing import List

# ==========================================
# 🧠 BACKEND LOGIC
# ==========================================

@dataclass
class Task:
    title: str
    duration: int
    time: str
    priority: str
    completed: bool = False

@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)
    def add_task(self, task: Task):
        self.tasks.append(task)

class Owner:
    def __init__(self, name: str):
        self.name = name
        self.pets: List[Pet] = []
    def add_pet(self, pet: Pet):
        self.pets.append(pet)

class Scheduler:
    @staticmethod
    def get_sorted_tasks(tasks: List[Task]):
        return sorted(tasks, key=lambda x: x.time)
    @staticmethod
    def detect_conflicts(tasks: List[Task]):
        time_counts = {}
        for t in tasks:
            time_counts[t.time] = time_counts.get(t.time, 0) + 1
        return [time for time, count in time_counts.items() if count > 1]

# ==========================================
# 📖 AI RAG KNOWLEDGE BASE
# ==========================================
PET_KNOWLEDGE = """
PET CARE SAFETY GUIDELINES:
- TOXIC FOODS: Grapes, raisins, chocolate, onions, garlic, and Xylitol are deadly.
- DOG EXERCISE: Most adult dogs need 30-60 minutes of physical activity daily.
- CAT HYDRATION: Cats have a low thirst drive; feeding wet food or using water fountains helps.
- TEMPERATURE: If it's too hot for your hand on the pavement (7-second rule), it's too hot for paws.
- EMERGENCY: Lethargy, vomiting, or refusal to eat for >24 hours requires a vet visit.
"""

def ask_pawpal_ai(api_key, user_query, pet_context=""):
    if not api_key:
        return "Please enter your Groq API Key in the sidebar."
    
    try:
        # Connect to Groq
        client = Groq(api_key=api_key.strip())
        
        prompt = f"""
        You are PawPal AI, a professional pet care consultant. 
        Use the following knowledge base to answer the user.
        
        Internal Knowledge:
        {PET_KNOWLEDGE}
        
        Current Pet Context: {pet_context}
        User Question: {user_query}
        
        Instructions:
        - Prioritize the 'Internal Knowledge' provided above.
        - Keep answers concise (2-3 sentences) and friendly.
        """
        
        # Call the new Llama 3.1 model
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful pet assistant."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant", 
        )
        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"API Error: Make sure your Groq key is correct. Details: {str(e)}"

# ==========================================
# 🎨 FRONTEND UI
# ==========================================

st.set_page_config(page_title="PawPal+ AI", page_icon="🐾")

st.title("🐾 PawPal+ AI Care Assistant")

if "owner" not in st.session_state:
    st.session_state.owner = Owner("Default User")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Groq API Key (Free)", type="password")
    
    st.divider()
    st.header("🐕 My Pets")
    new_pet_name = st.text_input("Pet Name")
    new_pet_species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Other"])
    if st.button("➕ Add Pet"):
        if new_pet_name:
            st.session_state.owner.add_pet(Pet(new_pet_name, new_pet_species))
            st.rerun()

if not st.session_state.owner.pets:
    st.info("👈 Add a pet and your API key in the sidebar to start!")
else:
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_name = st.selectbox("Select Pet", pet_names)
    selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_name)

    # --- AI ASSISTANT ---
    st.subheader(f"🤖 Chat with PawPal AI regarding {selected_name}")
    query = st.text_input("Ask a health or safety question:")
    if st.button("Ask AI"):
        with st.spinner("Searching knowledge base..."):
            context = f"The user has a {selected_pet.species} named {selected_name}."
            answer = ask_pawpal_ai(api_key, query, context)
            st.info(answer)

    st.divider()

    # --- Task Form ---
    st.subheader(f"📅 Schedule for {selected_name}")
    with st.form("task_form"):
        col1, col2 = st.columns(2)
        t_name = col1.text_input("Task Name")
        t_time = col1.text_input("Time (HH:MM)", value="08:00")
        t_duration = col2.number_input("Mins", min_value=5, value=15)
        t_priority = col2.select_slider("Priority", options=["low", "medium", "high"])
        if st.form_submit_button("Add Task"):
            selected_pet.add_task(Task(t_name, int(t_duration), t_time, t_priority))
            st.rerun()

    if selected_pet.tasks:
        sorted_tasks = Scheduler.get_sorted_tasks(selected_pet.tasks)
        conflicts = Scheduler.detect_conflicts(selected_pet.tasks)
        
        if conflicts:
            st.error(f"⚠️ SAFETY GUARDRAIL: Conflict detected at: {', '.join(conflicts)}")

        for t in sorted_tasks:
            st.write(f"**{t.time}** | {t.title} ({t.duration}m)")
        if st.button("Reset"):
            selected_pet.tasks = []
            st.rerun()