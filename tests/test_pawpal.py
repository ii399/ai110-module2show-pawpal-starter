"""Tests for core PawPal+ behaviors."""

from pawpal_system import Pet, Priority, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() flips the task from incomplete to complete."""
    task = Task("Morning walk", "exercise", 30, Priority.HIGH)

    # A new task starts incomplete.
    assert task.is_completed() is False

    task.mark_complete()

    assert task.is_completed() is True
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a pet increases that pet's task count by one."""
    pet = Pet("Biscuit", "dog", 4)
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", "food", 10, Priority.HIGH))

    assert len(pet.tasks) == 1
