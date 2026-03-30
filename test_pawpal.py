import pytest
# We import the classes from app.py to test them
from app import Task, Pet, Scheduler, Owner

def test_task_creation():
    """Verify that a Task object stores data correctly."""
    task = Task(title="Feeding", duration=15, time="08:00", priority="high")
    assert task.title == "Feeding"
    assert task.duration == 15
    assert task.time == "08:00"
    assert task.priority == "high"
    assert task.completed is False

def test_add_task_to_pet():
    """Verify that adding a task to a pet works."""
    my_pet = Pet(name="Mochi", species="Dog")
    task = Task(title="Walk", duration=30, time="10:00", priority="medium")
    my_pet.add_task(task)
    
    assert len(my_pet.tasks) == 1
    assert my_pet.tasks[0].title == "Walk"

def test_scheduler_sorting():
    """Verify the algorithm sorts tasks by time correctly."""
    t1 = Task("Dinner", 20, "18:00", "high")
    t2 = Task("Breakfast", 20, "08:00", "high")
    t3 = Task("Lunch", 20, "12:00", "medium")
    
    tasks = [t1, t2, t3]
    sorted_tasks = Scheduler.get_sorted_tasks(tasks)
    
    # Check that 08:00 is first and 18:00 is last
    assert sorted_tasks[0].time == "08:00"
    assert sorted_tasks[1].time == "12:00"
    assert sorted_tasks[2].time == "18:00"

def test_conflict_detection():
    """Verify the algorithm detects overlapping start times."""
    t1 = Task("Walk 1", 30, "09:00", "low")
    t2 = Task("Walk 2", 30, "09:00", "high") # Same time!
    
    conflicts = Scheduler.detect_conflicts([t1, t2])
    assert "09:00" in conflicts
    assert len(conflicts) == 1

def test_total_time_calculation():
    """Verify the algorithm sums up duration correctly."""
    t1 = Task("A", 10, "01:00", "low")
    t2 = Task("B", 25, "02:00", "low")
    
    total = Scheduler.calculate_total_time([t1, t2])
    assert total == 35