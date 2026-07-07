---
name: create-requirements-spec
description: Create requirements specification from user point of view. Use it to clarify requirements and prepare requirements specification from user point of view.
allowed-tools: Read, Write, Bash
---

## Input

- Initial user requirements: @features_context/$ARGUMENTS[0]/initial_user_requirements.md
- Template: @spec_templates/requirements_spec.md

## Instructions

1. Read the initial user requirements file.
2. Read the template file.
3. Ask the user all necessary questions to clarify missing or conflicting requirements before writing the spec.
4. Write the requirements specification following the template structure.

### Writing guidelines

- Be concise and specific — describe requirements from the user's perspective.
- Focus on what the system should do, not how it should be implemented.
- Identify and resolve ambiguities or conflicts in the initial user requirements by asking the user.
- Include only template sections that are relevant to the feature.

## Output

- Write the requirements specification to @features_context/$ARGUMENTS[0]/requirements_spec.md
