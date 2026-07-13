"""Simple tests for the PawPal+ core classes."""

import os
import sys
from datetime import time

# Allow running from anywhere by adding the project root to the path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Owner, Pet, Task, Frequency, Scheduler


def test_task_completion():
    """Calling mark_complete() changes the task's status to done."""
    task = Task("Morning walk", time(8, 0), Frequency.DAILY)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_task_addition_increases_count():
    """Adding a task to a Pet increases that pet's task count."""
    pet = Pet("Rex", "dog", "Labrador", 3)
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", time(7, 30), Frequency.DAILY))

    assert len(pet.tasks) == 1


def test_sort_by_time_orders_by_time():
    """sort_by_time() returns tasks in ascending time-of-day order."""
    morning = Task("Morning walk", time(8, 0), Frequency.DAILY)
    noon = Task("Lunch", time(12, 0), Frequency.DAILY)
    evening = Task("Evening walk", time(18, 30), Frequency.DAILY)

    ordered = Scheduler.sort_by_time([evening, morning, noon])

    assert ordered == [morning, noon, evening]


def test_sort_by_time_puts_untimed_tasks_last():
    """Tasks without a time sort to the end instead of raising."""
    timed = Task("Breakfast", time(7, 30), Frequency.DAILY)
    untimed = Task("Refill water", None, Frequency.DAILY)

    ordered = Scheduler.sort_by_time([untimed, timed])

    assert ordered == [timed, untimed]


def test_sort_by_time_does_not_mutate_input():
    """sort_by_time() returns a new list and leaves the original order intact."""
    later = Task("Evening walk", time(18, 30), Frequency.DAILY)
    earlier = Task("Morning walk", time(8, 0), Frequency.DAILY)
    original = [later, earlier]

    ordered = Scheduler.sort_by_time(original)

    assert ordered == [earlier, later]
    assert original == [later, earlier]


def _build_scheduler():
    """A scheduler with two pets and a mix of completed/pending tasks."""
    owner = Owner("Alex")
    rex = Pet("Rex", "dog", "Labrador", 3)
    mia = Pet("Mia", "cat", "Tabby", 2)
    owner.add_pet(rex)
    owner.add_pet(mia)

    walk = Task("Morning walk", time(8, 0), Frequency.DAILY)
    walk.mark_complete()
    rex.add_task(walk)
    rex.add_task(Task("Evening walk", time(18, 30), Frequency.DAILY))
    mia.add_task(Task("Breakfast", time(7, 30), Frequency.DAILY))

    scheduler = Scheduler()
    scheduler.register_owner(owner)
    return scheduler


def test_filter_tasks_by_completion():
    """completed=True/False selects finished vs. pending tasks."""
    scheduler = _build_scheduler()

    done = scheduler.filter_tasks(completed=True)
    pending = scheduler.filter_tasks(completed=False)

    assert [t.description for t in done] == ["Morning walk"]
    assert sorted(t.description for t in pending) == ["Breakfast", "Evening walk"]


def test_filter_tasks_by_pet_name():
    """pet_name selects only tasks belonging to that pet."""
    scheduler = _build_scheduler()

    rex_tasks = scheduler.filter_tasks(pet_name="Rex")

    assert sorted(t.description for t in rex_tasks) == ["Evening walk", "Morning walk"]


def test_filter_tasks_combines_filters():
    """completed and pet_name combine with AND."""
    scheduler = _build_scheduler()

    result = scheduler.filter_tasks(completed=False, pet_name="Rex")

    assert [t.description for t in result] == ["Evening walk"]


def test_filter_tasks_no_filters_returns_all():
    """With no filters, every task is returned."""
    scheduler = _build_scheduler()

    assert len(scheduler.filter_tasks()) == 3


def test_completing_daily_task_spawns_next_occurrence():
    """Completing a daily task auto-creates a fresh, pending copy on the pet."""
    pet = Pet("Rex", "dog", "Labrador", 3)
    walk = Task("Morning walk", time(8, 0), Frequency.DAILY)
    pet.add_task(walk)

    new_task = walk.complete()

    # The original is done; a new incomplete twin now exists on the pet.
    assert walk.completed is True
    assert new_task is not None
    assert new_task in pet.tasks
    assert new_task is not walk
    assert new_task.completed is False
    assert new_task.description == "Morning walk"
    assert new_task.time == time(8, 0)
    assert new_task.frequency is Frequency.DAILY
    assert len(pet.tasks) == 2
    assert pet.pending_tasks() == [new_task]


def test_completing_weekly_task_spawns_next_occurrence():
    """Weekly tasks also roll over to a next occurrence."""
    pet = Pet("Mia", "cat", "Tabby", 2)
    grooming = Task("Grooming", time(10, 0), Frequency.WEEKLY)
    pet.add_task(grooming)

    new_task = grooming.complete()

    assert new_task is not None
    assert new_task.frequency is Frequency.WEEKLY
    assert len(pet.tasks) == 2


def test_once_task_does_not_spawn():
    """A one-off task does not create a next occurrence."""
    pet = Pet("Rex", "dog", "Labrador", 3)
    vet = Task("Vet visit", time(9, 0), Frequency.ONCE)
    pet.add_task(vet)

    new_task = vet.complete()

    assert new_task is None
    assert len(pet.tasks) == 1


def test_completing_twice_does_not_spawn_duplicates():
    """Completing an already-done task is idempotent (no extra occurrences)."""
    pet = Pet("Rex", "dog", "Labrador", 3)
    walk = Task("Morning walk", time(8, 0), Frequency.DAILY)
    pet.add_task(walk)

    walk.complete()
    second = walk.complete()

    assert second is None
    assert len(pet.tasks) == 2  # original + one spawned, not two


def test_find_conflicts_same_pet():
    """Two tasks for the SAME pet at the same time are flagged as a conflict."""
    pet = Pet("Rex", "dog", "Labrador", 3)
    pet.add_task(Task("Walk", time(8, 0), Frequency.DAILY))
    pet.add_task(Task("Medicine", time(8, 0), Frequency.DAILY))
    owner = Owner("Alex")
    owner.add_pet(pet)
    scheduler = Scheduler()
    scheduler.register_owner(owner)

    conflicts = scheduler.find_conflicts()

    assert scheduler.has_conflicts() is True
    assert len(conflicts) == 1
    assert {t.description for t in conflicts[0]} == {"Walk", "Medicine"}


def test_find_conflicts_across_pets():
    """Tasks for DIFFERENT pets at the same time also conflict (owner's time)."""
    owner = Owner("Alex")
    rex = Pet("Rex", "dog", "Labrador", 3)
    mia = Pet("Mia", "cat", "Tabby", 2)
    owner.add_pet(rex)
    owner.add_pet(mia)
    rex.add_task(Task("Rex walk", time(8, 0), Frequency.DAILY))
    mia.add_task(Task("Mia breakfast", time(8, 0), Frequency.DAILY))
    scheduler = Scheduler()
    scheduler.register_owner(owner)

    conflicts = scheduler.find_conflicts()

    assert len(conflicts) == 1
    assert len(conflicts[0]) == 2


def test_no_conflicts_when_times_differ():
    """Distinct times produce no conflicts; untimed tasks are ignored."""
    pet = Pet("Rex", "dog", "Labrador", 3)
    pet.add_task(Task("Walk", time(8, 0), Frequency.DAILY))
    pet.add_task(Task("Dinner", time(18, 0), Frequency.DAILY))
    pet.add_task(Task("Whenever", None, Frequency.DAILY))
    owner = Owner("Alex")
    owner.add_pet(pet)
    scheduler = Scheduler()
    scheduler.register_owner(owner)

    assert scheduler.find_conflicts() == []
    assert scheduler.has_conflicts() is False


def test_find_conflicts_ignores_completed_by_default():
    """A completed task doesn't clash with a pending one unless asked."""
    pet = Pet("Rex", "dog", "Labrador", 3)
    done = Task("Walk", time(8, 0), Frequency.ONCE)
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task("Medicine", time(8, 0), Frequency.ONCE))
    owner = Owner("Alex")
    owner.add_pet(pet)
    scheduler = Scheduler()
    scheduler.register_owner(owner)

    assert scheduler.find_conflicts() == []
    assert len(scheduler.find_conflicts(include_completed=True)) == 1


def test_conflict_warning_message_when_clash():
    """conflict_warning() returns a non-empty, descriptive string on a clash."""
    owner = Owner("Alex")
    rex = Pet("Rex", "dog", "Labrador", 3)
    owner.add_pet(rex)
    rex.add_task(Task("Walk", time(8, 0), Frequency.DAILY))
    rex.add_task(Task("Medicine", time(8, 0), Frequency.DAILY))
    scheduler = Scheduler()
    scheduler.register_owner(owner)

    warning = scheduler.conflict_warning()

    assert warning != ""
    assert "08:00" in warning
    assert "Walk" in warning and "Medicine" in warning


def test_conflict_warning_empty_when_no_clash():
    """conflict_warning() returns an empty string (falsy) when all is clear."""
    owner = Owner("Alex")
    rex = Pet("Rex", "dog", "Labrador", 3)
    owner.add_pet(rex)
    rex.add_task(Task("Walk", time(8, 0), Frequency.DAILY))
    rex.add_task(Task("Dinner", time(18, 0), Frequency.DAILY))
    scheduler = Scheduler()
    scheduler.register_owner(owner)

    assert scheduler.conflict_warning() == ""


def test_conflict_warning_never_raises_on_empty_scheduler():
    """The lightweight check is safe to call even with no owners/tasks."""
    scheduler = Scheduler()

    assert scheduler.conflict_warning() == ""  # no crash, just empty


if __name__ == "__main__":
    test_task_completion()
    test_task_addition_increases_count()
    test_sort_by_time_orders_by_time()
    test_sort_by_time_puts_untimed_tasks_last()
    test_sort_by_time_does_not_mutate_input()
    test_filter_tasks_by_completion()
    test_filter_tasks_by_pet_name()
    test_filter_tasks_combines_filters()
    test_filter_tasks_no_filters_returns_all()
    test_completing_daily_task_spawns_next_occurrence()
    test_completing_weekly_task_spawns_next_occurrence()
    test_once_task_does_not_spawn()
    test_completing_twice_does_not_spawn_duplicates()
    test_find_conflicts_same_pet()
    test_find_conflicts_across_pets()
    test_no_conflicts_when_times_differ()
    test_find_conflicts_ignores_completed_by_default()
    test_conflict_warning_message_when_clash()
    test_conflict_warning_empty_when_no_clash()
    test_conflict_warning_never_raises_on_empty_scheduler()
    print("All tests passed.")
