import streamlit as st

# Import the specific classes we need from the logic layer. We only pull in
# what this UI actually uses, rather than `import pawpal_system` wholesale.
from pawpal_system import Owner, Pet, Task, Scheduler, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan a day of pet care based on time, priority, and preferences.")

# ---------------------------------------------------------------------------
# Application "memory"
#
# Streamlit re-runs this whole script top to bottom on every interaction, so a
# plain `owner = Owner(...)` here would be recreated (and wiped) on every click.
# st.session_state is a dict-like "vault" that survives reruns. We create the
# Owner ONCE — only if it isn't already stored — then reuse that same instance.
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_time=90)

# Bind a local name to the persisted object. Mutating this instance mutates the
# one in the vault, so changes stick across reruns.
owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Owner settings (sidebar)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Owner settings")
    owner.name = st.text_input("Owner name", value=owner.name)
    owner.available_time = st.number_input(
        "Available time today (min)", min_value=0, max_value=1440, value=owner.available_time
    )
    owner.maximum_task_duration = st.number_input(
        "Max minutes per task (0 = no cap)", min_value=0, max_value=1440,
        value=owner.maximum_task_duration,
    )

# ---------------------------------------------------------------------------
# Add a Pet  ->  Owner.add_pet()
# ---------------------------------------------------------------------------
st.subheader("Add a pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)
    add_pet_clicked = st.form_submit_button("Add pet")

    if add_pet_clicked:
        if pet_name.strip():
            # The Owner class method owns this data change.
            owner.add_pet(Pet(name=pet_name.strip(), species=species, age=int(age)))
            st.success(f"Added {pet_name}.")
        else:
            st.error("Please enter a pet name.")

# ---------------------------------------------------------------------------
# Schedule (add) a Task  ->  Pet.add_task()
# ---------------------------------------------------------------------------
st.subheader("Add a task")
if not owner.pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        target_pet_name = st.selectbox("For which pet?", [p.name for p in owner.pets])
        task_title = st.text_input("Task title", value="Morning walk")
        category = st.text_input("Category", value="general")
        col1, col2 = st.columns(2)
        with col1:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col2:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        required = st.checkbox("Required (must happen today)")
        add_task_clicked = st.form_submit_button("Add task")

        if add_task_clicked and task_title.strip():
            # Find the selected Pet instance, then let Pet.add_task() handle it.
            pet = next(p for p in owner.pets if p.name == target_pet_name)
            pet.add_task(
                Task(
                    task_name=task_title.strip(),
                    category=category.strip() or "general",
                    duration=int(duration),
                    priority=Priority[priority.upper()],
                    required=required,
                )
            )
            st.success(f"Added '{task_title}' to {target_pet_name}.")

# ---------------------------------------------------------------------------
# Current pets & tasks (read straight from the persisted Owner)
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Current pets & tasks")
if not owner.pets:
    st.info("No pets yet.")
else:
    for pet in owner.pets:
        with st.expander(f"{pet.name} ({pet.species}, {pet.age}) — {len(pet.tasks)} task(s)", expanded=True):
            if pet.tasks:
                st.table([t.get_task_details() for t in pet.tasks])
            else:
                st.caption("No tasks yet.")

# ---------------------------------------------------------------------------
# Build Schedule  ->  Scheduler.generate_schedule()
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Build schedule")
day_start = st.text_input("Day starts at (HH:MM, 24h)", value="08:00")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner=owner, day_start=day_start)
    scheduler.generate_schedule()
    st.text(scheduler.explain_schedule())
    st.json(scheduler.get_schedule_summary())
