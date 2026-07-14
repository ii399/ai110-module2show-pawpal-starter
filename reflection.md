# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
Add and manage a pet 
A user should be able to enter a pet's basic informstion, such as its name, species, age and specificcare needs. The user should be able tomupdate this information when the pet's needs change.

Create and manage pet care tasks
A user should be able to add tasks such as feeding, walking, giving medication, grooming, or enrichment activities. Each task can include a duration, priority level, category, and completion status.

Generate and review a daily care plan
A user should be able to enter how much time they have available and their care preferences. The system should then select appropriate tasks for the day, display the recommended schedule, and explain why each task was included.

- What classes did you include, and what responsibilities did you assign to each?
Pet - Store and manage information about an individual pet.
Owner - Store the owner's availability and preferences for completing pet care tasks.
Task -Represent a single pet care activity and track its status.
Scheduler - Generate and manage the daily pet care plan by selecting tasks that satisfy constraints.

**b. Design changes**

- Did your design change during implementation?
Yes
- If yes, describe at least one change and why you made it.
The UML initially showed an Owner and Pet as separate classes, but it did not explicitly model ownership in the class attributes.
The application needs an owner to manage one or more pets. By storing a list of pets in the Owner class, the Scheduler can easily retrieve all pets and their associated tasks when generating the daily schedule. This also better reflects the real-world relationship that one owner may have multiple pets.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
generate_schedule() drops a task that doesn't fit the remaining time, even if it is a required one, rather than overflowing available_time, so it guarantees the time budgeted over guaranteeing required tasks get done.

- Why is that tradeoff reasonable for this scenario?
For a planning tool, producing a schedule that can be relied on builds trust instead of producing a schedule that silently overruns it. An owner can easily raise available_time, mark a task non-required, or move it to another day. The scheduler leans on the owner for a judgment call rather than making a forced plan.
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
