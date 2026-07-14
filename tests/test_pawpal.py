"""Tests for core PawPal+ behaviors."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


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


def test_daily_task_spawns_next_occurrence():
    """Completing a daily task creates a new incomplete one due tomorrow."""
    pet = Pet("Biscuit", "dog", 4)
    task = Task("Feed", "food", 10, Priority.HIGH, frequency="daily", due_date=date.today())
    pet.add_task(task)

    task.mark_complete()

    assert len(pet.tasks) == 2  # original + next occurrence
    nxt = pet.tasks[-1]
    assert nxt.is_completed() is False
    assert nxt.frequency == "daily"
    assert nxt.due_date == date.today() + timedelta(days=1)


def test_weekly_task_spawns_seven_days_later():
    """Completing a weekly task schedules the next one a week out."""
    pet = Pet("Luna", "cat", 2)
    task = Task("Bath", "grooming", 45, Priority.LOW, frequency="weekly", due_date=date.today())
    pet.add_task(task)

    task.mark_complete()

    assert pet.tasks[-1].due_date == date.today() + timedelta(weeks=1)


def test_non_recurring_task_does_not_spawn():
    """A one-off task ('none') creates no follow-up when completed."""
    pet = Pet("Luna", "cat", 2)
    task = Task("Nail trim", "grooming", 15, Priority.LOW)  # frequency defaults to "none"
    pet.add_task(task)

    task.mark_complete()

    assert len(pet.tasks) == 1


def test_detect_conflicts_flags_overlapping_tasks():
    """Two tasks at the same time (different pets) produce one warning."""
    owner = Owner("Jordan", available_time=120)
    buddy, luna = Pet("Buddy", "dog", 4), Pet("Luna", "cat", 2)
    owner.add_pet(buddy)
    owner.add_pet(luna)
    buddy.add_task(Task("Walk", "exercise", 30, Priority.HIGH, preferred_time="08:00"))
    luna.add_task(Task("Feed", "food", 10, Priority.HIGH, preferred_time="08:00"))

    scheduler = Scheduler(owner)
    scheduler.collect_tasks()
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "Walk" in conflicts[0] and "Feed" in conflicts[0]


def test_no_conflict_for_touching_tasks():
    """Back-to-back tasks (one ends as the next starts) do not conflict."""
    owner = Owner("Jordan", available_time=120)
    pet = Pet("Buddy", "dog", 4)
    owner.add_pet(pet)
    pet.add_task(Task("Walk", "exercise", 30, Priority.HIGH, preferred_time="08:00"))  # 08:00-08:30
    pet.add_task(Task("Feed", "food", 10, Priority.HIGH, preferred_time="08:30"))       # 08:30-08:40

    scheduler = Scheduler(owner)
    scheduler.collect_tasks()

    assert scheduler.detect_conflicts() == []
