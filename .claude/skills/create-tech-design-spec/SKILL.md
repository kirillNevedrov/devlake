---
name: create-tech-design-spec
description: Create technical design specification. Use it to clarify technical details and prepare technical design specification.
allowed-tools: Read, Write, Bash
---

## Input

- Initial user requirements: @features_context/$ARGUMENTS[0]/initial_user_requirements.md
- Requirements specification: @features_context/$ARGUMENTS[0]/requirements_spec.md
- Template: @spec_templates/tech_design_spec.md

## Instructions

1. Read the initial user requirements file.
2. Read the requirements specification file. If it does not exist, skip this step — the initial user requirements will serve as the primary source of requirements instead.
3. Read the template file.
4. Ask the user all necessary questions to clarify technical details before writing the spec.
5. Write the technical design specification following the template structure.

### How to use the input sources

- **Primary source**: the requirements specification (describes what to build from the user's perspective).
- **Supplementary source**: the initial user requirements. Always review them — they may contain important technical details (e.g., specific APIs, infrastructure constraints, data formats) that the requirements specification omits because it focuses on user-facing behavior.
- **Fallback**: if the requirements specification does not exist, use the initial user requirements as the primary source.

### Writing guidelines

- Be concise and specific — avoid vague descriptions.
- Include only template sections that are relevant to the feature.
- Document data models as real Python classes to reduce interpretation ambiguity.
- Use Mermaid diagrams for flow logic when applicable.
- Link to the requirements specification for business rules instead of duplicating them.

## Output

- Write the technical design specification to @features_context/$ARGUMENTS[0]/tech_design_spec.md
