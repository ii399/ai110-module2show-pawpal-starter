"""PawPal+ logic layer.

Backend classes translated from diagrams/uml_draft.mmd. This module is
CLI-first: run it directly (`python pawpal_system.py`) to build a small
owner/pet/task scenario and verify the scheduling logic end to end, with no
Streamlit or UI involved.

Classes
-------
Task      : a single care activity (name, category, duration, priority, ...).
Pet       : pet details plus the list of tasks belonging to that pet.
Owner     : owns multiple pets and exposes constraints/preferences.
Scheduler : the "brain" — collects tasks across pets, filters, prioritizes,
            and builds a daily schedule that fits the owner's time budget.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import IntEnum
from itertools import combinations


class Priority(IntEnum):
    """Task priority. Ordered so higher urgency has the larger value."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    """A single care activity for a pet."""

    task_name: str
    category: str
    duration: int  # minutes
    priority: Priority
    completed: bool = False
    preferred_time: str = ""
    required: bool = False
    frequency: str = "none"  # "none", "daily", or "weekly"
    due_date: date | None = None
    pet: Pet | None = None

    # Recurrence intervals: how far ahead the next occurrence is due.
    _RECUR_INTERVALS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}

    def next_occurrence(self) -> Task | None:
        """Return a fresh, incomplete copy of this task for its next due date.

        Returns None for non-recurring tasks. For "daily"/"weekly" the new
        due_date is computed with timedelta from this task's due_date (or
        today if it has none): +1 day for daily, +7 days for weekly.
        """
        interval = self._RECUR_INTERVALS.get(self.frequency)
        if interval is None:
            return None
        base = self.due_date or date.today()
        return Task(
            task_name=self.task_name,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            completed=False,
            preferred_time=self.preferred_time,
            required=self.required,
            frequency=self.frequency,
            due_date=base + interval,
            pet=None,  # the owning Pet is set when it's added via add_task()
        )

    def mark_complete(self) -> None:
        """Mark this task done; for recurring tasks, spawn the next occurrence."""
        self.completed = True
        upcoming = self.next_occurrence()
        if upcoming is not None and self.pet is not None:
            self.pet.add_task(upcoming)

    def mark_incomplete(self) -> None:
        """Mark this task as not done."""
        self.completed = False

    def update_priority(self, priority: Priority) -> None:
        """Set the task's priority level."""
        self.priority = priority

    def update_duration(self, duration: int) -> None:
        """Set the task's duration in minutes (rejects negatives)."""
        if duration < 0:
            raise ValueError("duration cannot be negative")
        self.duration = duration

    def get_task_details(self) -> dict:
        """Return the task's fields as a plain dict."""
        return {
            "task_name": self.task_name,
            "category": self.category,
            "duration": self.duration,
            "priority": self.priority.name,
            "completed": self.completed,
            "preferred_time": self.preferred_time,
            "required": self.required,
            "frequency": self.frequency,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "pet": self.pet.name if self.pet else None,
        }

    def is_completed(self) -> bool:
        """Return True if the task has been completed."""
        return self.completed


@dataclass
class Pet:
    """A pet, its details, and the tasks that belong to it."""

    name: str
    species: str
    age: int
    care_needs: list[str] = field(default_factory=list)
    medical_notes: str = ""
    activity_level: str = ""
    tasks: list[Task] = field(default_factory=list)

    def get_pet_info(self) -> dict:
        """Return the pet's details as a plain dict."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "care_needs": list(self.care_needs),
            "medical_notes": self.medical_notes,
            "activity_level": self.activity_level,
            "task_count": len(self.tasks),
        }

    def update_pet_info(self, name: str, species: str, age: int) -> None:
        """Update the pet's name, species, and age."""
        self.name = name
        self.species = species
        self.age = age

    def add_care_need(self, care_need: str) -> None:
        """Add a care need if not already present."""
        if care_need not in self.care_needs:
            self.care_needs.append(care_need)

    def remove_care_need(self, care_need: str) -> None:
        """Remove a care need if present."""
        if care_need in self.care_needs:
            self.care_needs.remove(care_need)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet, keeping the Pet <-> Task link in sync."""
        # Keep both sides of the Pet <-> Task link in sync.
        if not any(t is task for t in self.tasks):
            self.tasks.append(task)
        task.pet = self

    def remove_task(self, task: Task) -> None:
        """Detach a task from this pet by identity, clearing its back-reference."""
        # Remove by identity (dataclass __eq__ is field-based, so two tasks
        # with identical fields would otherwise be indistinguishable).
        self.tasks = [t for t in self.tasks if t is not task]
        if task.pet is self:
            task.pet = None


@dataclass
class Owner:
    """An owner: their constraints/preferences and the pets they own."""

    name: str
    available_time: int = 0  # minutes available today
    preferred_task_times: list[str] = field(default_factory=list)
    task_preferences: dict = field(default_factory=dict)
    unavailable_times: list[str] = field(default_factory=list)
    maximum_task_duration: int = 0  # 0 == no per-task cap
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner if not already present."""
        if not any(p is pet for p in self.pets):
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner by identity."""
        self.pets = [p for p in self.pets if p is not pet]

    def update_available_time(self, minutes: int) -> None:
        """Set the minutes available today (rejects negatives)."""
        if minutes < 0:
            raise ValueError("available_time cannot be negative")
        self.available_time = minutes

    def update_preferences(self, preferences: dict) -> None:
        """Merge the given preferences into task_preferences."""
        self.task_preferences.update(preferences)

    def get_preferences(self) -> dict:
        """Return the owner's preferences and constraints as a dict."""
        return {
            "preferred_task_times": list(self.preferred_task_times),
            "task_preferences": dict(self.task_preferences),
            "unavailable_times": list(self.unavailable_times),
            "maximum_task_duration": self.maximum_task_duration,
        }

    def can_perform_task(self, task: Task) -> bool:
        """Whether this task is individually feasible for the owner.

        This is a per-task feasibility check only (duration cap + time
        conflicts). The overall daily time budget is enforced by the
        Scheduler, not here, to avoid duplicating that rule.
        """
        if self.maximum_task_duration and task.duration > self.maximum_task_duration:
            return False
        if task.duration > self.available_time:
            return False
        if task.preferred_time and task.preferred_time in self.unavailable_times:
            return False
        return True


@dataclass
class Scheduler:
    """The brain: builds a daily schedule from the owner's pets' tasks.

    total_scheduled_time and explanation are intentionally NOT stored as
    fields — they are always derived from daily_schedule via
    calculate_total_time() and explain_schedule(), so they can't go stale.
    """

    owner: Owner
    available_tasks: list[Task] = field(default_factory=list)
    daily_schedule: list[Task] = field(default_factory=list)
    day_start: str = "08:00"  # HH:MM the plan begins

    def collect_tasks(self) -> list[Task]:
        """Gather every task across all of the owner's pets."""
        self.available_tasks = [task for pet in self.owner.pets for task in pet.tasks]
        return self.available_tasks

    def filter_completed_tasks(self, tasks: list[Task] | None = None) -> list[Task]:
        """Drop tasks that are already done."""
        tasks = self.available_tasks if tasks is None else tasks
        return [t for t in tasks if not t.is_completed()]

    def filter_tasks_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Keep only tasks the owner can individually perform."""
        tasks = self.available_tasks if tasks is None else tasks
        return [t for t in tasks if self.owner.can_perform_task(t)]

    def prioritize_tasks(self, tasks: list[Task] | None = None) -> list[Task]:
        """Order tasks: required first, then higher priority, then shorter."""
        tasks = self.available_tasks if tasks is None else tasks
        return sorted(
            tasks,
            key=lambda t: (not t.required, -int(t.priority), t.duration),
        )

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Sort tasks chronologically by their preferred_time ('HH:MM').

        Zero-padded 24-hour 'HH:MM' strings compare correctly as plain
        strings ('07:30' < '12:15' < '18:00'), so the lambda keys directly
        on the string. For unpadded or 12-hour input you'd parse to numbers
        instead, e.g. key=lambda t: [int(p) for p in t.preferred_time.split(":")].
        """
        tasks = self.available_tasks if tasks is None else tasks
        return sorted(tasks, key=lambda t: t.preferred_time)

    def filter_tasks(
        self,
        completed: bool | None = None,
        pet_name: str | None = None,
        tasks: list[Task] | None = None,
    ) -> list[Task]:
        """Filter tasks by completion status and/or owning pet name.

        Pass completed=True/False to keep only (in)complete tasks, and/or
        pet_name to keep only that pet's tasks. Both are optional; omitting
        both returns every task unchanged.
        """
        tasks = self.available_tasks if tasks is None else tasks
        result = list(tasks)
        if completed is not None:
            result = [t for t in result if t.is_completed() == completed]
        if pet_name is not None:
            result = [t for t in result if t.pet is not None and t.pet.name == pet_name]
        return result

    def add_task_to_schedule(self, task: Task) -> None:
        """Append a task to the daily schedule if not already present."""
        if not any(t is task for t in self.daily_schedule):
            self.daily_schedule.append(task)

    def calculate_total_time(self) -> int:
        """Return the total minutes of all scheduled tasks."""
        return sum(t.duration for t in self.daily_schedule)

    def scheduled_with_times(self) -> list[tuple[str, Task]]:
        """Pair each scheduled task with its HH:MM start time.

        Tasks run back to back starting at day_start; each start is
        day_start plus the summed duration of all preceding tasks.
        """
        cursor = datetime.strptime(self.day_start, "%H:%M")
        timed = []
        for task in self.daily_schedule:
            timed.append((cursor.strftime("%I:%M %p"), task))
            cursor += timedelta(minutes=task.duration)
        return timed

    def generate_schedule(self) -> list[Task]:
        """Full pipeline: collect -> filter -> prioritize -> fit to budget."""
        self.collect_tasks()
        candidates = self.filter_completed_tasks()
        candidates = self.filter_tasks_by_time(candidates)
        candidates = self.prioritize_tasks(candidates)

        self.daily_schedule = []
        remaining = self.owner.available_time
        for task in candidates:
            if task.duration <= remaining:
                self.add_task_to_schedule(task)
                remaining -= task.duration
        return self.daily_schedule

    def explain_schedule(self) -> str:
        """Human-readable rationale for the current schedule."""
        if not self.daily_schedule:
            return "No tasks scheduled — check available time and pending tasks."

        lines = [
            f"Daily plan for {self.owner.name}: "
            f"{len(self.daily_schedule)} task(s), "
            f"{self.calculate_total_time()}/{self.owner.available_time} min used."
        ]
        for start_time, task in self.scheduled_with_times():
            pet_name = task.pet.name if task.pet else "unassigned"
            flags = []
            if task.required:
                flags.append("required")
            flags.append(f"priority: {task.priority.name.lower()}")
            lines.append(
                f"  {start_time} - {task.task_name} ({pet_name}, {task.duration} min) "
                f"[{', '.join(flags)}]"
            )
        return "\n".join(lines)

    def get_schedule_summary(self) -> dict:
        """Return a compact dict summary of the current schedule."""
        return {
            "owner": self.owner.name,
            "scheduled_count": len(self.daily_schedule),
            "available_count": len(self.available_tasks),
            "total_scheduled_time": self.calculate_total_time(),
            "available_time": self.owner.available_time,
            "tasks": [t.task_name for t in self.daily_schedule],
        }

    @staticmethod
    def _to_minutes(hhmm: str) -> int | None:
        """Convert an 'HH:MM' string to minutes-since-midnight, or None if unparseable."""
        try:
            hours, minutes = hhmm.split(":")
            return int(hours) * 60 + int(minutes)
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def _fmt(minutes: int) -> str:
        """Format minutes-since-midnight back to 'HH:MM'."""
        return f"{minutes // 60:02d}:{minutes % 60:02d}"

    def detect_conflicts(self, tasks: list[Task] | None = None) -> list[str]:
        """Return warning strings for tasks whose time windows overlap.

        Lightweight, pairwise check: each task occupies the window
        [preferred_time, preferred_time + duration). Two tasks conflict when
        their windows overlap, whether they belong to the same pet or
        different pets (the owner can only do one thing at a time). Completed
        and untimed tasks are ignored. Returns [] when there are no conflicts;
        it never raises, so callers can just print the warnings.
        """
        tasks = self.available_tasks if tasks is None else tasks

        # Keep only incomplete tasks that have a parseable start time.
        timed = []
        for task in tasks:
            if task.is_completed():
                continue
            start = self._to_minutes(task.preferred_time)
            if start is not None:
                timed.append((start, task))

        warnings = []
        for (a_start, a), (b_start, b) in combinations(timed, 2):
            a_end, b_end = a_start + a.duration, b_start + b.duration
            # Half-open overlap: touching edges (e.g. 08:30-08:30) don't conflict.
            if a_start < b_end and b_start < a_end:
                a_pet = a.pet.name if a.pet else "unassigned"
                b_pet = b.pet.name if b.pet else "unassigned"
                warnings.append(
                    f"WARNING: '{a.task_name}' ({a_pet} "
                    f"{self._fmt(a_start)}-{self._fmt(a_end)}) overlaps "
                    f"'{b.task_name}' ({b_pet} "
                    f"{self._fmt(b_start)}-{self._fmt(b_end)})"
                )
        return warnings


def _demo() -> None:
    """Build a small scenario and verify the scheduling logic from the CLI."""
    owner = Owner(
        name="Jordan",
        available_time=90,
        maximum_task_duration=60,
        unavailable_times=["night"],
    )

    biscuit = Pet(name="Biscuit", species="dog", age=4, activity_level="high")
    mochi = Pet(name="Mochi", species="cat", age=2)
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    biscuit.add_task(Task("Morning walk", "exercise", 30, Priority.HIGH, required=True))
    biscuit.add_task(Task("Feeding", "food", 10, Priority.HIGH, required=True))
    biscuit.add_task(Task("Fetch/enrichment", "play", 20, Priority.MEDIUM))
    biscuit.add_task(Task("Bath", "grooming", 45, Priority.LOW, preferred_time="night"))
    mochi.add_task(Task("Feeding", "food", 10, Priority.HIGH, required=True))
    mochi.add_task(Task("Litter cleanup", "hygiene", 10, Priority.MEDIUM))
    done = Task("Nail trim", "grooming", 15, Priority.LOW)
    done.mark_complete()
    mochi.add_task(done)

    scheduler = Scheduler(owner=owner)
    scheduler.generate_schedule()

    print("=" * 60)
    print("PawPal+ - CLI verification")
    print("=" * 60)
    print(scheduler.explain_schedule())
    print("-" * 60)
    print("Summary:", scheduler.get_schedule_summary())
    print("-" * 60)
    print(
        f"Collected {len(scheduler.available_tasks)} task(s); "
        f"scheduled {len(scheduler.daily_schedule)}. "
        "(Completed 'Nail trim' and the 45-min night 'Bath' were excluded.)"
    )


if __name__ == "__main__":
    _demo()
