# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    Owner: Name; [Owner with 1 or more pets], you can add and remove owners
    Pet: Name, Speecies, Breed, Age ; [Pets with one or more owners, and some tasks to be done], you can add and remove pets
    Task: Name, Duration, Priority; [Tasks assigned to one pet], you can create, delete and complete a task
    Schedule: Task, start time, end time; [ A list of tasks to be completed, likely 1 schedule for each pet] -- youu can ccreate, modify, and delete a scheule
- What classes did you include, and what responsibilities did you assign to each?
    Owners show what pets are associated with them [ 1 or more], Pets give infromations on what the pet is, and what tasks need to be done [i.e. walking should be assigned and completed on dog, and a dog should have an owner]; Tasks are things that the owner/caretakers has to do for the pet [i.e. walking, feeding, grooming, etc]; schedule is a set of tasks that must be done, likely 1 schedule per pet
**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
