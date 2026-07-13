"""Simple tests for the PawPal+ core classes."""

import os
import sys
from datetime import time

# Allow running from anywhere by adding the project root to the path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Pet, Task, Frequency


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


if __name__ == "__main__":
    test_task_completion()
    test_task_addition_increases_count()
    print("All tests passed.")
