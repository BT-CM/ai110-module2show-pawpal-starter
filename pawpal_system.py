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

    def complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    # Alias for readability at call sites / in tests.
    mark_complete = complete

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

    def assign_task(self, pet: Pet, task: Task) -> None:
        """Give a task to a pet."""
        pet.add_task(task)

    def complete_task(self, task: Task) -> None:
        """Mark a task complete."""
        task.complete()

    def remove_task(self, task: Task) -> None:
        """Remove a task from whatever pet it belongs to."""
        task.delete()

    def organize(
        self, frequency: Optional[Frequency] = None, include_completed: bool = False
    ) -> list[Task]:
        """Return tasks ordered by time of day, optionally filtered to one frequency."""
        tasks = self.all_tasks(include_completed=include_completed)
        if frequency is not None:
            tasks = [t for t in tasks if t.frequency is frequency]
        return sorted(tasks, key=lambda t: t.time or time.max)

    def next_task(self) -> Optional[Task]:
        """The earliest pending task by time, or None if nothing is pending."""
        ordered = self.organize()
        return ordered[0] if ordered else None
