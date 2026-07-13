"""PawPal+ logic layer.

Class stubs generated from diagrams/uml_draft.mmd. Attributes and method
signatures only — no logic yet. Fill in method bodies incrementally.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Owner:
    name: str
    available_time: int = 0
    preferred_task_times: list[str] = field(default_factory=list)
    task_preferences: dict = field(default_factory=dict)
    unavailable_times: list[str] = field(default_factory=list)
    maximum_task_duration: int = 0
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        ...

    def remove_pet(self, pet: Pet) -> None:
        ...

    def update_available_time(self, minutes: int) -> None:
        ...

    def update_preferences(self, preferences: dict) -> None:
        ...

    def get_preferences(self) -> dict:
        ...

    def can_perform_task(self, task: Task) -> bool:
        ...


@dataclass
class Pet:
    name: str
    species: str
    age: int
    care_needs: list[str] = field(default_factory=list)
    medical_notes: str = ""
    activity_level: str = ""
    tasks: list[Task] = field(default_factory=list)

    def get_pet_info(self) -> dict:
        ...

    def update_pet_info(self, name: str, species: str, age: int) -> None:
        ...

    def add_care_need(self, care_need: str) -> None:
        ...

    def remove_care_need(self, care_need: str) -> None:
        ...

    def add_task(self, task: Task) -> None:
        ...

    def remove_task(self, task: Task) -> None:
        ...


@dataclass
class Task:
    task_name: str
    category: str
    duration: int
    priority: str
    completed: bool = False
    preferred_time: str = ""
    required: bool = False
    pet: Pet | None = None

    def mark_complete(self) -> None:
        ...

    def mark_incomplete(self) -> None:
        ...

    def update_priority(self, priority: str) -> None:
        ...

    def update_duration(self, duration: int) -> None:
        ...

    def get_task_details(self) -> dict:
        ...

    def is_completed(self) -> bool:
        ...


@dataclass
class Scheduler:
    owner: Owner
    available_tasks: list[Task] = field(default_factory=list)
    daily_schedule: list[Task] = field(default_factory=list)
    total_scheduled_time: int = 0
    explanation: str = ""

    def collect_tasks(self) -> list[Task]:
        ...

    def generate_schedule(self) -> list[Task]:
        ...

    def prioritize_tasks(self) -> list[Task]:
        ...

    def filter_completed_tasks(self) -> list[Task]:
        ...

    def filter_tasks_by_time(self) -> list[Task]:
        ...

    def calculate_total_time(self) -> int:
        ...

    def add_task_to_schedule(self, task: Task) -> None:
        ...

    def explain_schedule(self) -> str:
        ...

    def get_schedule_summary(self) -> dict:
        ...
