from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler, Priority


def show(label, tasks):
    """Print a labeled list of tasks as `HH:MM  Name  Pet  done?`."""
    print(f"\n{label}")
    if not tasks:
        print("  (none)")
        return
    for t in tasks:
        pet = t.pet.name if t.pet else "-"
        print(f"  {t.preferred_time}  {t.task_name:16} {pet:6} done={t.is_completed()}")


def main():
    owner = Owner(name="Jordan", available_time=180)

    buddy = Pet(name="Buddy", species="Dog", age=4, activity_level="High")
    luna = Pet(name="Luna", species="Cat", age=2, activity_level="Medium")
    owner.add_pet(buddy)
    owner.add_pet(luna)

    # Add tasks OUT OF ORDER on purpose: preferred_time values are not
    # chronological in insertion order, so sort_by_time() has real work to do.
    buddy.add_task(Task("Evening Walk", "Exercise", 30, Priority.HIGH, preferred_time="18:00"))
    buddy.add_task(Task("Morning Walk", "Exercise", 30, Priority.HIGH, preferred_time="07:30", required=True))
    buddy.add_task(Task("Lunch Play", "Enrichment", 20, Priority.MEDIUM, preferred_time="12:15"))

    luna.add_task(Task("Feed Dinner", "Feeding", 10, Priority.HIGH, preferred_time="17:45"))
    luna.add_task(Task("Feed Breakfast", "Feeding", 10, Priority.HIGH, preferred_time="08:00", required=True))
    groom = Task("Brush Fur", "Grooming", 15, Priority.LOW, preferred_time="09:30")
    groom.mark_complete()  # already done today
    luna.add_task(groom)

    scheduler = Scheduler(owner)
    scheduler.collect_tasks()  # gather every pet's tasks into available_tasks

    print("=" * 50)
    print("PawPal+ - sorting & filtering check")
    print("=" * 50)

    # As inserted (deliberately unsorted).
    show("Insertion order (unsorted):", scheduler.available_tasks)

    # SORT: chronological by preferred_time.
    show("Sorted by time (sort_by_time):", scheduler.sort_by_time())

    # FILTER: by pet name.
    show("Filter pet_name='Buddy':", scheduler.filter_tasks(pet_name="Buddy"))

    # FILTER: by completion status.
    show("Filter completed=False (still to do):", scheduler.filter_tasks(completed=False))
    show("Filter completed=True (already done):", scheduler.filter_tasks(completed=True))

    # COMPOSE: filter then sort — Luna's outstanding tasks, chronological.
    luna_todo = scheduler.filter_tasks(completed=False, pet_name="Luna")
    show("Luna's outstanding tasks, chronological:", scheduler.sort_by_time(luna_todo))

    # RECURRING TASKS: completing a daily/weekly task auto-creates the next one.
    print("\n" + "=" * 50)
    print("Recurring tasks (auto-create next occurrence)")
    print("=" * 50)

    daily_feed = Task(
        "Daily Feed", "Feeding", 10, Priority.HIGH,
        preferred_time="06:30", frequency="daily", due_date=date.today(),
    )
    weekly_bath = Task(
        "Weekly Bath", "Grooming", 45, Priority.LOW,
        preferred_time="10:00", frequency="weekly", due_date=date.today(),
    )
    buddy.add_task(daily_feed)
    buddy.add_task(weekly_bath)

    print(f"Buddy task count before completing: {len(buddy.tasks)}")
    daily_feed.mark_complete()
    weekly_bath.mark_complete()
    print(f"Buddy task count after completing:  {len(buddy.tasks)}  (+2 auto-created)")

    for t in buddy.tasks:
        if t.frequency != "none" and not t.is_completed():
            print(f"  next '{t.task_name}' ({t.frequency}) due {t.due_date}")

    # CONFLICT DETECTION: two tasks wanting the same time slot.
    print("\n" + "=" * 50)
    print("Conflict detection")
    print("=" * 50)

    # Buddy's "Backyard Play" at 08:00 collides with Luna's "Feed Breakfast"
    # at 08:00 (already added above) — different pets, same time, one owner.
    buddy.add_task(Task("Backyard Play", "Enrichment", 20, Priority.MEDIUM, preferred_time="08:00"))

    scheduler.collect_tasks()  # refresh available_tasks with the new task
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print(f"Found {len(conflicts)} conflict(s):")
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("No conflicts detected.")


if __name__ == "__main__":
    main()
