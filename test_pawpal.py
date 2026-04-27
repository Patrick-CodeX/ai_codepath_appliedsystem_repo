import pytest
from unittest.mock import patch, MagicMock
from app import Task, Pet, Scheduler, Owner, ask_pawpal_ai

# ==========================================
# 🧪 BACKEND LOGIC TESTS
# ==========================================

@pytest.fixture
def sample_pet():
    pet = Pet(name="Mochi", species="Dog")
    pet.add_task(Task(title="Feeding", duration=15, time="08:00", priority="high"))
    pet.add_task(Task(title="Walk", duration=30, time="18:00", priority="medium"))
    return pet

def test_task_initialization():
    """Verify Task dataclass stores values correctly."""
    t = Task("Grooming", 45, "14:00", "low")
    assert t.title == "Grooming"
    assert t.completed is False

def test_scheduler_sorting():
    """Verify tasks are sorted chronologically regardless of input order."""
    tasks = [
        Task("Dinner", 10, "20:00", "high"),
        Task("Breakfast", 10, "07:00", "high"),
        Task("Lunch", 10, "12:00", "medium")
    ]
    sorted_tasks = Scheduler.get_sorted_tasks(tasks)
    assert sorted_tasks[0].time == "07:00"
    assert sorted_tasks[-1].time == "20:00"

def test_conflict_detection_logic():
    """Verify that multiple tasks at the same time trigger a conflict."""
    tasks = [
        Task("Medication", 5, "09:00", "high"),
        Task("Morning Walk", 20, "09:00", "low")
    ]
    conflicts = Scheduler.detect_conflicts(tasks)
    assert "09:00" in conflicts
    assert len(conflicts) == 1

def test_owner_pet_relationship():
    """Verify owner can hold multiple pets."""
    owner = Owner("Alice")
    owner.add_pet(Pet("Luna", "Cat"))
    owner.add_pet(Pet("Rex", "Dog"))
    assert len(owner.pets) == 2
    assert owner.pets[0].name == "Luna"

# ==========================================
# 🤖 AI & RAG TESTS (Mocked)
# ==========================================

@patch("app.Groq")
def test_ask_pawpal_ai_success(mock_groq):
    """
    Test the AI logic by mocking the Groq client.
    This ensures the RAG prompt is built correctly without calling the real API.
    """
    # Setup the mock response structure
    mock_client = MagicMock()
    mock_groq.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Dogs should not eat grapes as they cause kidney failure."))
    ]
    mock_client.chat.completions.create.return_value = mock_response

    # Execute function
    result = ask_pawpal_ai("fake_key", "Can my dog eat grapes?", "Context: Dog named Rex")

    # Assertions
    assert "grapes" in result.lower()
    mock_client.chat.completions.create.assert_called_once()

def test_ask_pawpal_ai_no_key():
    """Ensure the system handles missing API keys gracefully."""
    result = ask_pawpal_ai("", "Hello?")
    assert "Please enter your Groq API Key" in result

@patch("app.Groq")
def test_ask_pawpal_ai_error_handling(mock_groq):
    """Ensure the system handles API errors without crashing."""
    mock_client = MagicMock()
    mock_groq.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("API Quota Exceeded")

    result = ask_pawpal_ai("valid_key", "Hi", "Context")
    assert "API Error" in result