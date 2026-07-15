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
1. Completed tasks are removed first. Any task that has already been completed is excluded from scheduling since it no longer needs to be done.
2. Tasks must be feasible. Each task is checked to make sure it can realistically be completed. A task is excluded if it exceeds the maximum allowed task duration, takes longer than the owner's available time, or is scheduled during one of the owner's unavailable times.
3. Tasks are prioritized. The remaining tasks are sorted so that required tasks come first, followed by higher-priority tasks. If two tasks have the same priority, the shorter task is scheduled first.
4. The schedule stays within the available time. Tasks are added to the daily schedule one at a time in priority order, but only if they fit within the owner's remaining available time. The schedule never exceeds the time budgeted.

- How did you decide which constraints mattered most?
generate_schedule() in pawpal_system.py is the method that determines the reasoning.
1. it filters completed and infeasible tasks first. Tasks that are already done or cannot fit into the day are removed before scheduling, making the remaining list smaller and easier to process.
2. it treats available time as a hard limit. The schedule never exceeds the owner's available time, even if that means leaving some required tasks unscheduled.
3. it uses priority to rank remaining tasks. After filtering, tasks are ordered by priority and whether they are required so the most important ones are scheduled first.
4. it applies preferences last. Preferred times improve the schedule when possible, but they do not override higher-priority tasks or the available time limit. Preferences are mainly used for ordering and conflict checking.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
generate_schedule() drops a task that doesn't fit the remaining time, even if it is a required one, rather than overflowing available_time, so it guarantees the time budgeted over guaranteeing required tasks get done.

- Why is that tradeoff reasonable for this scenario?
For a planning tool, producing a schedule that can be relied on builds trust instead of producing a schedule that silently overruns it. An owner can easily raise available_time, mark a task non-required, or move it to another day. The scheduler leans on the owner for a judgment call rather than making a forced plan.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
1. Design and planning. I used AI to brainstorm the system design, create the UML diagram, generate class skeletons, and reason about relationships such as the Pet–Task association.
2. Implementation and debugging. AI helped implement the scheduling logic, troubleshoot errors, and verify features by running the application and tests. It also helped resolve issues such as missing Streamlit dependencies and platform-specific output problems.
3. Refactoring and code review. I used AI to improve code organization, add documentation, simplify the design, identify performance issues like the O(n²) conflict check, and point out areas that still needed testing.
4. Documentation. AI assisted with writing the README, explaining design decisions, documenting the testing approach, and improving the clarity of project documentation.

- What kinds of prompts or questions were most helpful?
Feature-focused prompts. Breaking the work into small tasks, such as implementing one feature or method at a time, produced more accurate and easier-to-verify results.
Review and critique prompts. Questions like "What edge cases am I missing?", "Which version should I keep and why?", and "What constraints matter most?" were especially useful because they encouraged AI to evaluate and improve the design instead of only generating code.
Specific implementation prompts. Detailed requests, such as sorting tasks by time or implementing recurring task behavior, produced better results than broad requests like "build me a scheduler." Being specific reduced the need for multiple revisions.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
It suggested rewriting my conflict detection with a sort-and-sweep instead of the simple pairwise check. It was faster on paper, but with only a handful of tasks that speed never mattered, and the faster version was harder to read and relied on a hidden assumption that could break later. I kept the simpler version.

- How did you evaluate or verify what the AI suggested?
Mostly by running it. Every feature got exercised in main.py and checked with pytest, and I looked at the actual output, like confirming a completed daily task came back due the next day. If the reasoning behind a suggestion wasn't obvious, I asked it to explain the tradeoff before using it.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
Task completion, adding tasks to a pet, recurring tasks (daily rolling to the next day, weekly to seven days out, one-off tasks spawning nothing), chronological sorting, and conflict detection for two tasks at the same time, same pet and different pets, plus back-to-back tasks that shouldn't count as a clash.

- Why were these tests important?
They cover the logic that's easy to get wrong or overlook: date math, sort order, and the boundary between "overlapping" and "just touching." Those are the spots a small change could break without it being noticed.

**b. Confidence**

- How confident are you that your scheduler works correctly?
Fairly, but not fully, about 3 out of 5. The individual pieces are well tested, but the main generate_schedule() method that ties them together has no direct tests yet.

- What edge cases would you test next if you had more time?
1. schedule never exceeds the owner's available time
2. a pet or owner with no tasks doesn't crash
3. priority ordering holds in a real generated plan
4. a required task getting dropped when it doesn't fit behaves the way It intended.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
The separation between the logic layer and the UI. Because all the scheduling lived in pawpal_system.py, I could build and test it from the command line first, then wire it into Streamlit without changing any of the core logic.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would make the scheduler actually use preferred times and act on conflicts instead of just flagging them, and I'd add the missing tests around generate_schedule(). Right now preferred time affects sorting but not the plan itself.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
Building the logic on its own and verifying it before touching the UI made everything easier. And AI is most useful when you make it prove things work and question your design, not just when it writes code for you.