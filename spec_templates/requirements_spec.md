# Requirements Specification

## 1. Structure

### 1.1 Problem statement

Concise description of the problem and proposed solution.

### 1.2 Glossary

*Optional*

Define any specialized terms that a reader needs to know to understand the specification, including acronyms
and abbreviations.

### 1.3 Requirements

List of requirements.

1. Each requirement has a unique identifier in scope of the specification.
2. Describe requirements from user point of view
3. Do not include technical implementation details

Requirement can be one of two types:
- **User story**: when requirement can be expressed as high-level user goals
- **Use case**: when requirement must be expressed as detailed, precise interaction and behavior specification

> Use **User story** requirement type wherever possible.
> Use **Use case** requirement type only for complex requirements that cannot reasonably be expressed as User stories.

#### User story

User story structure (*can include any of the sections below*):
1. **Statement**
Text in the form "As a [role], I want [goal], so that [benefit]."
2. **Acceptance criteria**
Numbered list of conditions that a system must satisfy for a user story to be considered complete. Described from user point of view.

#### Use case

Use case structure (*can include any of the sections below*):
1. **Name**
2. **Primary Actor**
The primary actor initiates the use case and derives the main value from it. 
3. **Secondary Actors**
A secondary actor participates somehow in the successful execution of the use case
4. **Preconditions**
Preconditions define prerequisites that must be met before the system can begin executing the use
case.
5. **Trigger**
A trigger condition initiates execution of the use case.
6. **Normal flow**
One scenario is identified as the normal flow of events for the use case. 
A numbered list of steps that shows the sequence of interactions between the actor and the
system—a dialog—that leads from the preconditions to the postconditions.
7. **Alternative flows**
Other success scenarios within the use case are called alternative flows or secondary scenarios.
Alternative flows deliver the same business outcome (sometimes with variations) as the normal
flow but represent less common or lower-priority variations in the specifics of the task or how it is
accomplished.
8. **Exceptions**
Conditions that have the potential to prevent a use case from succeeding are called exceptions. 
9. **Postconditions**
Postconditions describe the state of the system after the use case executed successfully. 
10. **Functional requirements**
Required system behaviors under specific conditions.

(See "Software requirements, 3rd edition, by Karl Wiegers and Joy Beatty" book, chapter 8 "Understanding user requirements", chapter 11 "Writing excellent requirements" for details.)

### 1.4 Analysis models

*Optional*

This section includes or points to relevant analysis models such as data flow diagrams, feature trees, state-transition diagrams, or entity-relationship diagrams.

(See "Software requirements, 3rd edition, by Karl Wiegers and Joy Beatty" book, chapter 12 "A picture is
worth 1024 words" for details.)

### 1.5 Prototypes

*Optional*

Links to user interface prototypes. For example Lovable prototypes.

Simple prototyping tool https://excalidraw.com/. To just draw sketches of the UI with a pen tool.

---

## 2. Examples

- @spec_templates/requirements_spec_user_stories_example.md - Example of requirements specification with user story requirements
- @spec_templates/requirements_spec_use_cases_example.md - Example of requirements specification with use case requirements

> A single requirements specification document can contain both user story and use case requirements.
