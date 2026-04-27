import streamlit as st
import openai
from dataclasses import dataclass, field
from typing import List

# ==========================================
# 🧠 BACKEND LOGIC (The "Brain")
# ==========================================

@dataclass
class Task:
    title: str
    duration: int  # in minutes
    time: str      # format "HH:MM"
    priority: str  # "high", "medium", "low"
    completed: bool = False

    def mark_complete(self):
        self.completed = True

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
    """The Logic Layer for organizing tasks."""
    @staticmethod
    def get_sorted_tasks(tasks: List[Task]):
        return sorted(tasks, key=lambda x: x.time)

    @staticmethod
    def detect_conflicts(tasks: List[Task]):
        time_counts = {}
        for t in tasks:
            time_counts[t.time] = time_counts.get(t.time, 0) + 1
        return [time for time, count in time_counts.items() if count > 1]

    @staticmethod
    def calculate_total_time(tasks: List[Task]):
        return sum(t.duration for t in tasks)

# ==========================================
# 📖 AI RAG KNOWLEDGE BASE
# ==========================================
# This acts as our "retrieved" data source for the AI.
PET_KNOWLEDGE = """
PET CARE SAFETY GUIDELINES (Internal Database):
- TOXIC FOODS: Grapes, raisins, chocolate, onions, garlic, and Xylitol (sugar-free gum) are deadly.
- DOG EXERCISE: Most adult dogs need 30-60 minutes of physical activity daily.
- CAT HYDRATION: Cats have a low thirst drive; feeding wet food or using water fountains helps kidney health.
- TEMPERATURE: If it's too hot for your hand on the pavement (7-second rule), it's too hot for dog paws.
- EMERGENCY: Lethargy, vomiting, or refusal to eat for >24 hours requires a vet visit.
"""

def ask_pawpal_ai(api_key, user_query, pet_context=""):
    if not api_key:
        return "Please enter an OpenAI API Key in the sidebar to use the AI Assistant."
    
    client = openai.OpenAI(api_key=api_key)
    
    # This is the RAG Prompt - It forces the AI to use our "Knowledge Base"
    prompt = f"""
    You are PawPal AI, a professional pet care consultant. 
    Use the following internal knowledge to answer the user.
    
    Internal Knowledge:
    {PET_KNOWLEDGE}
    
    Current Pet Context: {pet_context}
    
    User Question: {user_query}
    
    Instructions:
    - If the answer is in the Internal Knowledge, prioritize it.
    - If the user asks about a toxic food, be very firm and helpful.
    - Keep answers concise and friendly.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a helpful pet care assistant."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"

# ==========================================
# 🎨 FRONTEND UI (The "Face")
# ==========================================

st.set_page_config(page_title="PawPal+ AI", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+ AI Care Assistant")

# --- Persistence: Keep the data alive ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Default User")

# --- SIDEBAR: Settings & Manage Pets ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    st.caption("Needed for the AI Assistant feature.")
    
    st.divider()
    st.header("🐕 My Pets")
    new_pet_name = st.text_input("Pet Name", placeholder="e.g. Mochi")
    new_pet_species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Other"])
    
    if st.button("➕ Add Pet"):
        if new_pet_name:
            st.session_state.owner.add_pet(Pet(new_pet_name, new_pet_species))
            st.success(f"Added {new_pet_name}!")
            st.rerun()
        else:
            st.error("Please enter a name.")

# --- MAIN UI: Task Management ---
if not st.session_state.owner.pets:
    st.info("👈 Use the sidebar to add your first pet and enter your API key!")
else:
    # 1. Select which pet to work with
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_name = st.selectbox("Select Pet Profile", pet_names)
    selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_name)

    # --- AI ASSISTANT SECTION (RAG FEATURE) ---
    with st.expander("🤖 Ask PawPal AI Expert", expanded=False):
        st.write(f"Ask anything about caring for **{selected_name}**.")
        query = st.text_input("Question (e.g., 'Can I give my dog grapes?')")
        if st.button("Ask AI"):
            with st.spinner("Consulting knowledge base..."):
                context = f"The user is asking about their {selected_pet.species} named {selected_name}."
                answer = ask_pawpal_ai(api_key, query, context)
                st.info(answer)

    st.divider()

    # 2. Add Task Form
    st.subheader(f"📅 Schedule a Task for {selected_name}")
    with st.form("task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            t_name = st.text_input("Task Name", placeholder="e.g. Walkies")
            t_time = st.text_input("Time (HH:MM)", value="08:00")
        with col2:
            t_duration = st.number_input("Duration (mins)", min_value=5, value=20)
            t_priority = st.select_slider("Priority", options=["low", "medium", "high"])
        
        if st.form_submit_button("Add to Schedule"):
            if t_name and t_time:
                new_task = Task(t_name, int(t_duration), t_time, t_priority)
                selected_pet.add_task(new_task)
                st.toast(f"Scheduled: {t_name}")
                st.rerun()
            else:
                st.error("Missing name or time!")

    # 3. The Schedule Display
    st.subheader(f"Today's Plan for {selected_name}")

    if not selected_pet.tasks:
        st.write("No tasks yet. Use the form above to start planning!")
    else:
        # Run backend algorithms
        sorted_tasks = Scheduler.get_sorted_tasks(selected_pet.tasks)
        conflicts = Scheduler.detect_conflicts(selected_pet.tasks)
        total_mins = Scheduler.calculate_total_time(selected_pet.tasks)

        if conflicts:
            st.warning(f"⚠️ **Time Conflict:** Multiple tasks scheduled for {', '.join(conflicts)}.")

        for t in sorted_tasks:
            color = {"high": "red", "medium": "orange", "low": "blue"}[t.priority]
            st.markdown(f"**{t.time}** | {t.title} ({t.duration}m) — :{color}[{t.priority.upper()}]")

        st.metric("Total Care Time", f"{total_mins} min")

        if st.button("🗑️ Reset Schedule"):
            selected_pet.tasks = []
            st.rerun()

    # --- REASONING ---
    with st.expander("❓ How does this system work?"):
        st.write("""
        1. **Retrieval (RAG):** When you ask the AI a question, it retrieves safety data from our internal 'Knowledge Base' before generating an answer.
        2. **Logic Layer:** The scheduler uses a sorting algorithm to arrange tasks chronologically.
        3. **Guardrails:** The conflict detector flags human errors (like overlapping start times) to ensure pet safety.
        """)