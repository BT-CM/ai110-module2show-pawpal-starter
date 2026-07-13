"""PawPal+ demo: build an owner with pets and tasks (added out of order),
then print the results using the Scheduler's sorting and filtering methods."""

from datetime import time

from pawpal_system import Owner, Pet, Task, Frequency, Scheduler


def build_household() -> Scheduler:
    """Create an owner with two pets and tasks added deliberately OUT OF ORDER.

    Tasks are added in a jumbled time order (evening before morning, etc.) so
    the demo can prove that Scheduler.sort_by_time() does the ordering, not the
    insertion order.
    """
    owner = Owner("Alex")

    rex = Pet("Rex", "dog", "Labrador", 3)
    mia = Pet("Mia", "cat", "Tabby", 2)
    owner.add_pet(rex)
    owner.add_pet(mia)

    # Added out of order on purpose:
    rex.add_task(Task("Evening walk", time(18, 30), Frequency.DAILY))
    mia.add_task(Task("Clean litter box", time(12, 0), Frequency.DAILY))
    rex.add_task(Task("Morning walk", time(8, 0), Frequency.DAILY))
    mia.add_task(Task("Breakfast", time(7, 30), Frequency.DAILY))
    # Deliberate same-time clash: Mia's vitamins collide with Rex's 08:00 walk.
    mia.add_task(Task("Vitamins", time(8, 0), Frequency.DAILY))

    # Mark one task done so the completion filter has something to find.
    rex.tasks[-1].mark_complete()  # "Morning walk" is complete

    scheduler = Scheduler()
    scheduler.register_owner(owner)
    return scheduler


def _print_tasks(tasks: list[Task]) -> None:
    """Print a list of tasks, one per line, with time / pet / status."""
    if not tasks:
        print("  (none)")
        return
    for task in tasks:
        when = task.time.strftime("%H:%M") if task.time else "  --  "
        pet_name = task.pet.name if task.pet else "Unassigned"
        status = "done" if task.completed else "pending"
        print(f"  {when}  |  {pet_name:<5}  |  {task.description:<18}  ({status})")


def demo_insertion_order(scheduler: Scheduler) -> None:
    """Show the raw insertion order so the sort below is visibly doing work."""
    print("=" * 52)
    print("Tasks in INSERTION order (jumbled on purpose)")
    print("=" * 52)
    _print_tasks(scheduler.all_tasks(include_completed=True))


def demo_sort_by_time(scheduler: Scheduler) -> None:
    """Use Scheduler.sort_by_time() to order every task by time of day."""
    print()
    print("=" * 52)
    print("Sorted by time  (Scheduler.sort_by_time)")
    print("=" * 52)
    all_tasks = scheduler.all_tasks(include_completed=True)
    _print_tasks(Scheduler.sort_by_time(all_tasks))


def demo_filter_tasks(scheduler: Scheduler) -> None:
    """Use Scheduler.filter_tasks() to filter by status and by pet name."""
    print()
    print("=" * 52)
    print("Filtered: pending only  (filter_tasks(completed=False))")
    print("=" * 52)
    _print_tasks(Scheduler.sort_by_time(scheduler.filter_tasks(completed=False)))

    print()
    print("=" * 52)
    print("Filtered: completed only  (filter_tasks(completed=True))")
    print("=" * 52)
    _print_tasks(scheduler.filter_tasks(completed=True))

    print()
    print("=" * 52)
    print("Filtered: Rex's tasks  (filter_tasks(pet_name='Rex'))")
    print("=" * 52)
    _print_tasks(Scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Rex")))

    print()
    print("=" * 52)
    print("Combined: Rex's pending tasks  (completed=False, pet_name='Rex')")
    print("=" * 52)
    _print_tasks(scheduler.filter_tasks(completed=False, pet_name="Rex"))


def demo_recurrence(scheduler: Scheduler) -> None:
    """Complete a daily task and show its next occurrence appear automatically."""
    print()
    print("=" * 52)
    print("Recurrence: completing a daily task spawns the next")
    print("=" * 52)

    pending = scheduler.filter_tasks(completed=False)
    daily = next(t for t in pending if t.frequency is Frequency.DAILY)
    print(f"  Pending before: {len(pending)}")
    print(f"  Completing daily task: {daily.pet.name} - {daily.description}")

    next_occurrence = scheduler.complete_task(daily)

    if next_occurrence is not None:
        print(
            f"  -> auto-scheduled next {next_occurrence.frequency.value} occurrence: "
            f"{next_occurrence.pet.name} - {next_occurrence.description} "
            f"({next_occurrence.time.strftime('%H:%M')})"
        )
    print(f"  Pending after:  {len(scheduler.filter_tasks(completed=False))}")
    print()
    print("  Schedule now (pending, sorted by time):")
    _print_tasks(scheduler.organize())


def demo_conflict_warning(scheduler: Scheduler) -> None:
    """Show the lightweight conflict check: a warning string, not a crash."""
    print()
    print("=" * 52)
    print("Conflict detection (lightweight warning)")
    print("=" * 52)

    warning = scheduler.conflict_warning()
    if warning:
        print(warning)
    else:
        print("  No conflicts detected.")

    # Verify the scheduler actually caught the deliberate 08:00 clash.
    assert scheduler.has_conflicts(), "expected a same-time conflict!"
    print("\n  Verified: has_conflicts() == True")


def main() -> None:
    scheduler = build_household()
    demo_insertion_order(scheduler)
    demo_sort_by_time(scheduler)
    demo_filter_tasks(scheduler)
    demo_recurrence(scheduler)
    demo_conflict_warning(scheduler)


if __name__ == "__main__":
    main()
