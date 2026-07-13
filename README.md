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
-------------------------------------------


========================================
Today's Schedule
========================================
  07:30  |  Mia    |  Breakfast
  08:00  |  Rex    |  Morning walk
  12:00  |  Mia    |  Clean litter box
  18:30  |  Rex    |  Evening walk
----------------------------------------
  4 task(s) scheduled


--------------------------------------
```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

The test suite lives in [`tests/test_pawpal.py`](tests/test_pawpal.py) and covers the
core scheduling behaviors. It uses plain `assert` statements, so it runs either
under `pytest` or directly with the standard library.

```bash
# Run the full suite with pytest (auto-discovers test_* functions):
python -m pytest

# ...or run it directly, no dependencies required:
python tests/test_pawpal.py
```

### What's covered

| Behavior | What we verify |
|----------|----------------|
| **Sorting correctness** | `sort_by_time()` / `organize()` return tasks in ascending time-of-day order; untimed tasks sort last; the input list is not mutated |
| **Recurrence logic** | Completing a daily/weekly task spawns a fresh, pending copy on the same pet; `once`/`monthly` do not recur; completing twice is idempotent (no duplicates) |
| **Conflict detection** | `find_conflicts()` flags tasks sharing the exact same time (within and across pets); completed and untimed tasks are ignored; `conflict_warning()` returns a readable string and never crashes |
| **Filtering** | `filter_tasks()` narrows by completion status and/or pet name, combining with AND |
| **Edge cases** | Empty scheduler, a pet with no tasks, and a pet shared by two owners (counted once) |

Sample test output:

```
# Paste your `pytest` output here, e.g.:
# ==================== 20 passed in 0.03s ====================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Orders by time of day; untimed tasks sort last |
| Filtering | `Scheduler.filter_tasks()` | By completion status and/or pet name (AND) |
| Conflict handling | `Scheduler.find_conflicts()`, `has_conflicts()`, `conflict_warning()` | Flags same-time clashes across pets; warns without crashing. Exact-time only, not overlaps |
| Recurring tasks | `Task.complete()` / `Task.spawn_next()` | Daily/weekly auto-spawn next occurrence; once/monthly do not |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
