# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

```
Today's Schedule
----------------------------------------
Morning    | Feed Breakfast       | Luna   | 10 min
Morning    | Morning Walk         | Buddy  | 30 min
Afternoon  | Play Time            | Buddy  | 20 min
Evening    | Brush Fur            | Luna   | 15 min
----------------------------------------
Total Time: 75 minutes

Daily plan for Jordan: 4 task(s), 75/90 min used.
08:00 AM - Feed Breakfast (Luna, 10 min) [required, priority: high]
08:10 AM - Morning Walk (Buddy, 30 min) [required, priority: high]
08:40 AM - Play Time (Buddy, 20 min) [priority: medium]
09:00 AM - Brush Fur (Luna, 15 min) [priority: low]

```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
================================================================ test session starts ========================================================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\projects\codepath\AI110\ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
collected 2 items                                                                                                                                     

tests\test_pawpal.py ..                                                                                                                [100%]
================================================================= 2 passed in 0.01s =========================================================

```

## 📐 Smarter Scheduling

All scheduling logic lives in `pawpal_system.py`. Each feature and the method
that implements it:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.prioritize_tasks()` | `sort_by_time()` orders tasks chronologically by `preferred_time` ("HH:MM", compared as zero-padded strings); `prioritize_tasks()` orders by required → priority → shorter duration. |
| Filtering | `Scheduler.filter_tasks()`, `Scheduler.filter_completed_tasks()`, `Scheduler.filter_tasks_by_time()` | `filter_tasks(completed=?, pet_name=?)` filters by completion status and/or pet; `filter_completed_tasks()` drops finished tasks; `filter_tasks_by_time()` drops tasks the owner can't individually fit (`Owner.can_perform_task()`). |
| Conflict handling | `Scheduler.detect_conflicts()` | Pairwise check of each task's `[preferred_time, +duration)` window (same pet or different pets). Returns a list of warning strings; never raises. Touching edges don't conflict. |
| Recurring tasks | `Task.mark_complete()` → `Task.next_occurrence()` | Completing a `"daily"` / `"weekly"` task auto-creates the next instance on the same pet. `next_occurrence()` computes the new `due_date` with `timedelta` (+1 day / +7 days). |
| Budget fit | `Scheduler.generate_schedule()` | Greedily adds prioritized tasks while they fit `Owner.available_time`; never overflows the budget (may drop a task that doesn't fit). |
| Timed plan output | `Scheduler.scheduled_with_times()`, `Scheduler.explain_schedule()` | Assigns back-to-back `HH:MM` start times from `day_start`; renders a readable plan with 12-hour AM/PM times. |

### Feature summary

- **Sorting behavior** — `Scheduler.sort_by_time()` (chronological, by `preferred_time`).
- **Filtering behavior** — `Scheduler.filter_tasks()` (by pet and/or completion status).
- **Conflict detection** — `Scheduler.detect_conflicts()` (overlapping time windows → warnings).
- **Recurring task logic** — `Task.mark_complete()` via `Task.next_occurrence()` (daily/weekly re-creation with `timedelta`).

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
