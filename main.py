"""PawPal+ demo: build an owner with pets and tasks, then print today's schedule."""

from datetime import time

from pawpal_system import Owner, Pet, Task, Frequency, Scheduler


def build_household() -> Scheduler:
    """Create an owner with two pets and a handful of timed tasks."""
    owner = Owner("Alex")

    rex = Pet("Rex", "dog", "Labrador", 3)
    mia = Pet("Mia", "cat", "Tabby", 2)
    owner.add_pet(rex)
    owner.add_pet(mia)

    rex.add_task(Task("Morning walk", time(8, 0), Frequency.DAILY))
    rex.add_task(Task("Evening walk", time(18, 30), Frequency.DAILY))
    mia.add_task(Task("Breakfast", time(7, 30), Frequency.DAILY))
    mia.add_task(Task("Clean litter box", time(12, 0), Frequency.DAILY))

    scheduler = Scheduler()
    scheduler.register_owner(owner)
    return scheduler


def print_todays_schedule(scheduler: Scheduler) -> None:
    """Print pending tasks for today, ordered by time of day."""
    print("=" * 40)
    print("Today's Schedule")
    print("=" * 40)

    tasks = scheduler.organize(frequency=Frequency.DAILY)
    if not tasks:
        print("Nothing scheduled. Enjoy the day!")
        return

    for task in tasks:
        when = task.time.strftime("%H:%M") if task.time else "  --  "
        pet_name = task.pet.name if task.pet else "Unassigned"
        print(f"  {when}  |  {pet_name:<5}  |  {task.description}")

    print("-" * 40)
    print(f"  {len(tasks)} task(s) scheduled")


def main() -> None:
    scheduler = build_household()
    print_todays_schedule(scheduler)


if __name__ == "__main__":
    main()
