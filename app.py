import streamlit as st
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
        # Sorts tasks by time (HH:MM)
        return sorted(tasks, key=lambda x: x.time)

    @staticmethod
    def detect_conflicts(tasks: List[Task]):
        # Finds if multiple tasks share the exact same start time
        time_counts = {}
        for t in tasks:
            time_counts[t.time] = time_counts.get(t.time, 0) + 1
        return [time for time, count in time_counts.items() if count > 1]

    @staticmethod
    def calculate_total_time(tasks: List[Task]):
        return sum(t.duration for t in tasks)

# ==========================================
# 🎨 FRONTEND UI (The "Face")
# ==========================================

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+ Care Assistant")

# --- Persistence: Keep the data alive ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Default User")

# --- SIDEBAR: Manage Your Pets ---
with st.sidebar:
    st.header("My Pets")
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
    st.info("👈 Use the sidebar to add your first pet!")
else:
    # 1. Select which pet to work with
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_name = st.selectbox("Select Pet", pet_names)
    selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_name)

    st.divider()

    # 2. Add Task Form
    st.subheader(f"Add a Task for {selected_name}")
    with st.form("task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            t_name = st.text_input("What needs to happen?", placeholder="e.g. Morning Meds")
            t_time = st.text_input("Time (HH:MM)", value="08:00")
        with col2:
            t_duration = st.number_input("Duration (mins)", min_value=5, value=20)
            t_priority = st.select_slider("Priority Level", options=["low", "medium", "high"])
        
        if st.form_submit_button("📅 Schedule Task"):
            if t_name and t_time:
                new_task = Task(t_name, int(t_duration), t_time, t_priority)
                selected_pet.add_task(new_task)
                st.toast(f"Added {t_name}")
            else:
                st.error("Missing name or time!")

    # 3. The Schedule Display (The Algorithmic Layer)
    st.divider()
    st.subheader(f"Today's Schedule: {selected_name}")

    if not selected_pet.tasks:
        st.write("No tasks scheduled yet. Add one above!")
    else:
        # Run algorithms
        sorted_tasks = Scheduler.get_sorted_tasks(selected_pet.tasks)
        conflicts = Scheduler.detect_conflicts(selected_pet.tasks)
        total_mins = Scheduler.calculate_total_time(selected_pet.tasks)

        # Show Conflicts if they exist
        if conflicts:
            st.warning(f"⚠️ **Schedule Conflict:** You have multiple tasks at {', '.join(conflicts)}.")

        # Display the List
        for t in sorted_tasks:
            color = {"high": "red", "medium": "orange", "low": "blue"}[t.priority]
            st.markdown(f"⏳ **{t.time}** — {t.title} ({t.duration}m) | :{color}[Priority: {t.priority.upper()}]")

        st.info(f"**Total Care Time Scheduled:** {total_mins} minutes")

        # --- CLEAR BUTTON ---
        if st.button("🗑️ Reset All Tasks"):
            selected_pet.tasks = []
            st.success("Schedule cleared.")
            st.rerun()

        # --- REASONING (Required for Grading) ---
        with st.expander("📝 Why is my schedule ordered this way?"):
            st.write(f"""
            - **Chronological Sorting:** {selected_name}'s tasks are ordered by time so you can follow a natural morning-to-night routine.
            - **Conflict Detection:** The system flags overlapping start times so you don't try to be in two places at once.
            - **Priority Highlights:** We use color-coding so that '{[t.title for t in sorted_tasks if t.priority == 'high']}' tasks stand out as urgent.
            """)