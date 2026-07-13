"""PawPal+ system classes.

Four core classes:
  - Task:      a single activity (description, time, frequency, completion).
  - Pet:       pet details plus the list of tasks belonging to it.
  - Owner:     manages multiple pets and exposes all their tasks.
  - Scheduler: the "brain" that retrieves, organizes, and manages tasks
               across every pet of every owner.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
from enum import Enum
from typing import Optional


class Frequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# Frequencies that automatically roll over to a fresh occurrence when the
# current one is completed. ONCE never recurs; MONTHLY is left out on purpose
# (this system tracks only time-of-day, not dates, so a monthly rollover would
# be indistinguishable from a daily one — add real date logic before enabling).
RECURRING_FREQUENCIES = frozenset({Frequency.DAILY, Frequency.WEEKLY})


# eq=False so equality/`in`/remove use object identity rather than field
# values (two tasks named "walk" stay distinct). repr=False on back-references
# breaks the otherwise-infinite recursion when printing linked objects.
@dataclass(eq=False)
class Task:
    """A single activity to be performed for a pet."""

    description: str
    time: Optional[time] = None          # time of day the task should happen
    frequency: Frequency = Frequency.DAILY
    completed: bool = False
    pet: Optional[Pet] = field(default=None, repr=False)

    def complete(self) -> Optional[Task]:
        """Mark this task as done.

        If the task recurs (daily/weekly) and this call actually transitioned
        it from pending to done, a fresh incomplete copy is created for the
        next occurrence and attached to the same pet. Returns that new task,
        or None if nothing was spawned (already completed, or non-recurring).
        """
        if self.completed:
            return None  # idempotent: completing twice doesn't spawn duplicates
        self.completed = True
        if self.frequency in RECURRING_FREQUENCIES:
            return self.spawn_next()
        return None

    # Alias for readability at call sites / in tests.
    mark_complete = complete

    def spawn_next(self) -> Task:
        """Create a fresh, incomplete copy of this task for its next occurrence.

        The copy keeps the description, time-of-day, and frequency, and is
        attached to the same pet so it shows up as pending in the schedule.
        """
        next_occurrence = Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
        )
        if self.pet is not None:
            self.pet.add_task(next_occurrence)
        return next_occurrence

    def reset(self) -> None:
        """Mark this task as not-yet-done (e.g. for a recurring task's next run)."""
        self.completed = False

    def delete(self) -> None:
        """Detach this task from its pet."""
        if self.pet is not None:
            self.pet.remove_task(self)


@dataclass(eq=False)
class Pet:
    """Stores a pet's details and the tasks that belong to it."""

    name: str
    species: str
    breed: str
    age: int
    owners: list[Owner] = field(default_factory=list, repr=False)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Assign a task to this pet (a task belongs to exactly one pet)."""
        if task not in self.tasks:
            self.tasks.append(task)
        task.pet = self

    def remove_task(self, task: Task) -> None:
        """Unassign a task from this pet."""
        if task in self.tasks:
            self.tasks.remove(task)
        if task.pet is self:
            task.pet = None

    def pending_tasks(self) -> list[Task]:
        """Tasks for this pet that are not yet completed."""
        return [t for t in self.tasks if not t.completed]


@dataclass(eq=False)
class Owner:
    """Owns and manages one or more pets, and exposes all of their tasks."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Link this owner and pet, keeping both sides in sync."""
        if pet not in self.pets:
            self.pets.append(pet)
        if self not in pet.owners:
            pet.owners.append(self)

    def remove_pet(self, pet: Pet) -> None:
        """Unlink this owner and pet from both sides."""
        if pet in self.pets:
            self.pets.remove(pet)
        if self in pet.owners:
            pet.owners.remove(self)

    def all_tasks(self, include_completed: bool = True) -> list[Task]:
        """Every task across all of this owner's pets."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(
                t for t in pet.tasks if include_completed or not t.completed
            )
        return tasks


@dataclass(eq=False)
class Scheduler:
    """The brain: retrieves, organizes, and manages tasks across all pets."""

    owners: list[Owner] = field(default_factory=list)

    def register_owner(self, owner: Owner) -> None:
        """Track an owner (and therefore all of their pets and tasks)."""
        if owner not in self.owners:
            self.owners.append(owner)

    def all_pets(self) -> list[Pet]:
        """Every pet managed by every registered owner (de-duplicated)."""
        pets: list[Pet] = []
        for owner in self.owners:
            for pet in owner.pets:
                if pet not in pets:
                    pets.append(pet)
        return pets

    def all_tasks(self, include_completed: bool = True) -> list[Task]:
        """Every task across every pet."""
        tasks: list[Task] = []
        for pet in self.all_pets():
            tasks.extend(
                t for t in pet.tasks if include_completed or not t.completed
            )
        return tasks

    def pending_tasks(self) -> list[Task]:
        """All incomplete tasks across every pet."""
        return self.all_tasks(include_completed=False)

    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> list[Task]:
        """Return tasks filtered by completion status and/or pet name.

        Both filters are optional and combine with AND.

        Args:
            completed: ``True`` keeps only finished tasks, ``False`` keeps only
                pending ones, and ``None`` (default) skips the completion
                filter. Compared with ``is`` so ``None`` is distinct from
                ``False``.
            pet_name: Keep only tasks whose pet has this exact name; ``None``
                (default) skips the pet filter. Tasks with no pet are dropped
                when a name is given.

        Returns:
            A new list of matching tasks (unsorted; wrap in ``sort_by_time``
            for ordered output).

        Complexity:
            O(n) in the total number of tasks.
        """
        tasks = self.all_tasks(include_completed=True)
        if completed is not None:
            tasks = [t for t in tasks if t.completed is completed]
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet is not None and t.pet.name == pet_name]
        return tasks

    def assign_task(self, pet: Pet, task: Task) -> None:
        """Give a task to a pet."""
        pet.add_task(task)

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark a task complete, returning any auto-created next occurrence."""
        return task.complete()

    def remove_task(self, task: Task) -> None:
        """Remove a task from whatever pet it belongs to."""
        task.delete()

    @staticmethod
    def sort_by_time(tasks: list[Task]) -> list[Task]:
        """Return a new list of tasks ordered by time of day (ascending).

        Args:
            tasks: The tasks to order. Not mutated.

        Returns:
            A new list sorted earliest-first. Tasks without a time
            (``time is None``) sort last, using ``time.max`` as their key so
            untimed tasks land at the end of the day.

        Complexity:
            O(n log n) in the number of tasks (a single ``sorted`` call).
        """
        return sorted(tasks, key=lambda t: t.time or time.max)

    def organize(
        self, frequency: Optional[Frequency] = None, include_completed: bool = False
    ) -> list[Task]:
        """Return tasks ordered by time of day, optionally filtered to one frequency."""
        tasks = self.all_tasks(include_completed=include_completed)
        if frequency is not None:
            tasks = [t for t in tasks if t.frequency is frequency]
        return self.sort_by_time(tasks)

    def next_task(self) -> Optional[Task]:
        """The earliest pending task by time, or None if nothing is pending."""
        ordered = self.organize()
        return ordered[0] if ordered else None

    def find_conflicts(self, include_completed: bool = False) -> list[list[Task]]:
        """Group tasks scheduled at the exact same time of day.

        Conflicts span pets on purpose: two pets both needing attention at
        08:00 is still a clash for the single owner. Detection is by *exact*
        time match only -- overlapping durations are not considered, because
        ``Task`` stores a start time but no duration.

        Args:
            include_completed: If ``False`` (default), completed tasks are
                excluded (a finished task no longer competes for time).

        Returns:
            A list of conflict groups ordered earliest-first, where each group
            is a list of 2+ tasks sharing one time. Tasks without a time are
            ignored (nothing to clash with). Empty list if there are no
            clashes.

        Complexity:
            O(n) to bucket tasks by time, plus O(k log k) to sort the k
            distinct times (k <= n).
        """
        groups: dict[time, list[Task]] = {}
        for task in self.all_tasks(include_completed=include_completed):
            if task.time is None:
                continue
            groups.setdefault(task.time, []).append(task)
        return [groups[t] for t in sorted(groups) if len(groups[t]) > 1]

    def has_conflicts(self, include_completed: bool = False) -> bool:
        """Report whether any two tasks share a time.

        A convenience boolean over :meth:`find_conflicts` for callers that
        only need yes/no (e.g. deciding whether to show a warning banner).

        Args:
            include_completed: Passed through to :meth:`find_conflicts`.

        Returns:
            ``True`` if at least one same-time clash exists, else ``False``.
        """
        return bool(self.find_conflicts(include_completed=include_completed))

    def conflict_warning(self, include_completed: bool = False) -> str:
        """Build a lightweight, human-readable warning about conflicts.

        A "warn, don't crash" wrapper over :meth:`find_conflicts`: it never
        raises, so it can be shown to the owner (UI or terminal) rather than
        halting the program. Callers can simply check ``if warning:``.

        Args:
            include_completed: Passed through to :meth:`find_conflicts`.

        Returns:
            A multi-line message listing each clash (time, count, and the
            "description (pet)" of every task involved), or an empty string
            when there are no conflicts. The message uses an ASCII-only prefix
            so it is safe to ``print`` on any console encoding.

        Complexity:
            Same as :meth:`find_conflicts`, plus O(n) to format the message.
        """
        conflicts = self.find_conflicts(include_completed=include_completed)
        if not conflicts:
            return ""

        # ASCII-only prefix: this string is printed to terminals too, and a
        # fancy glyph can itself raise UnicodeEncodeError on some consoles.
        lines = ["[!] Scheduling conflicts found:"]
        for group in conflicts:
            when = group[0].time.strftime("%H:%M")
            items = ", ".join(
                f"{t.description} ({t.pet.name if t.pet else 'Unassigned'})"
                for t in group
            )
            lines.append(f"  {when} - {len(group)} tasks overlap: {items}")
        return "\n".join(lines)
