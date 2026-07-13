from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Task, Frequency, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")

# Session "vault": create the Owner and Scheduler ONCE, then reuse them across
# reruns. Guard with `in` checks so we don't overwrite them on every click.
owner_name = st.text_input("Owner name", value="Jordan")
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name)
    st.session_state.scheduler = Scheduler()
    st.session_state.scheduler.register_owner(st.session_state.owner)

owner = st.session_state.owner
scheduler = st.session_state.scheduler
owner.name = owner_name  # keep the owner's name in sync with the input

# --- Adding a Pet -----------------------------------------------------------
st.markdown("### Add a Pet")
pcol1, pcol2 = st.columns(2)
with pcol1:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
with pcol2:
    breed = st.text_input("Breed", value="Shiba")
    age = st.number_input("Age", min_value=0, max_value=40, value=2)

if st.button("Add pet"):
    # Only add the pet if the owner doesn't already have one by that name.
    if any(p.name == pet_name for p in owner.pets):
        st.info(f"{pet_name} is already one of {owner.name}'s pets.")
    else:
        owner.add_pet(Pet(pet_name, species, breed, int(age)))
        st.success(f"Added {pet_name} to {owner.name}.")

if owner.pets:
    st.caption("Current pets: " + ", ".join(p.name for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

# --- Scheduling a Task ------------------------------------------------------
st.markdown("### Schedule a Task")
if not owner.pets:
    st.info("Add a pet first, then you can schedule tasks for it.")
else:
    tcol1, tcol2, tcol3, tcol4 = st.columns(4)
    with tcol1:
        target_pet_name = st.selectbox("Pet", [p.name for p in owner.pets])
    with tcol2:
        task_title = st.text_input("Task", value="Morning walk")
    with tcol3:
        task_time = st.time_input("Time", value=time(8, 0))
    with tcol4:
        freq_name = st.selectbox("Frequency", [f.name for f in Frequency], index=1)

    if st.button("Add task"):
        target_pet = next(p for p in owner.pets if p.name == target_pet_name)
        target_pet.add_task(Task(task_title, task_time, Frequency[freq_name]))
        st.success(
            f"Scheduled '{task_title}' for {target_pet_name} "
            f"at {task_time.strftime('%H:%M')}."
        )

# --- Completing a Task ------------------------------------------------------
st.markdown("### Complete a Task")
st.caption(
    "Marking a daily or weekly task done automatically schedules its next "
    "occurrence."
)

pending = scheduler.pending_tasks()
if not pending:
    st.info("No pending tasks to complete.")
else:
    labels = [
        f"{t.pet.name if t.pet else 'Unassigned'} — {t.description}"
        f" ({t.time.strftime('%H:%M') if t.time else '--'}, {t.frequency.value})"
        for t in pending
    ]
    choice = st.selectbox("Pending task", range(len(pending)), format_func=lambda i: labels[i])

    if st.button("Mark complete"):
        done_task = pending[choice]
        next_occurrence = scheduler.complete_task(done_task)
        if next_occurrence is not None:
            st.success(
                f"Completed '{done_task.description}'. Scheduled its next "
                f"{done_task.frequency.value} occurrence automatically."
            )
        else:
            st.success(f"Completed '{done_task.description}'.")

st.divider()

# --- Today's Schedule (the Scheduler brain) ---------------------------------
st.subheader("Build Schedule")
st.caption(
    "Everything below is driven by the Scheduler class: it filters, sorts by "
    "time of day, flags same-time conflicts, and points out what's up next."
)

# Filter controls — these map directly onto Scheduler.filter_tasks() and
# Scheduler.organize(frequency=...). The view is reactive (no button), so it
# updates the moment you change a filter.
fcol1, fcol2, fcol3 = st.columns(3)
with fcol1:
    pet_filter = st.selectbox(
        "Pet", ["All pets"] + [p.name for p in owner.pets]
    )
with fcol2:
    status_filter = st.selectbox("Status", ["Pending", "Completed", "All"])
with fcol3:
    freq_filter = st.selectbox("Frequency", ["All"] + [f.name for f in Frequency])

# Translate the UI choices into the Scheduler's own arguments.
completed_arg = {"Pending": False, "Completed": True, "All": None}[status_filter]
pet_arg = None if pet_filter == "All pets" else pet_filter

# filter_tasks() handles pet + completion; sort_by_time() orders the result.
tasks = Scheduler.sort_by_time(
    scheduler.filter_tasks(completed=completed_arg, pet_name=pet_arg)
)
# Frequency isn't a filter_tasks() argument, so apply it here.
if freq_filter != "All":
    tasks = [t for t in tasks if t.frequency is Frequency[freq_filter]]

if not tasks:
    st.info("Nothing matches these filters yet. Add pets/tasks or widen the filters.")
else:
    # Collect the exact tasks involved in a same-time clash so we can both
    # summarize the count and flag each conflicting row in the table.
    conflict_groups = scheduler.find_conflicts()
    conflicting = {id(t) for group in conflict_groups for t in group}

    # At-a-glance summary of the currently filtered view.
    mcol1, mcol2, mcol3 = st.columns(3)
    mcol1.metric("Tasks shown", len(tasks))
    mcol2.metric("Pending", sum(1 for t in tasks if not t.completed))
    mcol3.metric("Conflicts", len(conflict_groups))

    # Point out the single earliest pending task across ALL pets.
    up_next = scheduler.next_task()
    if up_next is not None and up_next.time is not None:
        st.info(
            f"⏭️ Up next: **{up_next.description}** for "
            f"{up_next.pet.name if up_next.pet else 'Unassigned'} "
            f"at {up_next.time.strftime('%H:%M')}."
        )

    # Lightweight conflict check: warn when tasks clash, reassure when clear.
    warning = scheduler.conflict_warning()
    if warning:
        st.warning(warning)
    else:
        st.success("✅ No scheduling conflicts — every task has its own time slot.")

    st.markdown("### 🐾 Today's Schedule")
    st.table(
        [
            {
                "Time": t.time.strftime("%H:%M") if t.time else "--",
                "Pet": t.pet.name if t.pet else "Unassigned",
                "Task": t.description,
                "Frequency": t.frequency.value.capitalize(),
                "Status": "✅ Done" if t.completed else "⏳ Pending",
                "Conflict": "⚠️ Clash" if id(t) in conflicting else "—",
            }
            for t in tasks
        ]
    )
