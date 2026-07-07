# Tech Design Specification

## Overview

This template provides a structured approach for creating tech design specifications. The specification should serve as a comprehensive blueprint that bridges requirements and implementation.

### Key Principles

1. **Connect through flow logic** - Use flow diagrams/descriptions as the backbone, linking other sections to relevant flow steps. This principle is only applicable to specifications which affect any existing system flow or introduce any new system flow. If the specification does not affect any existing system flow and does not introduce any new system flow then this principle is not applicable to it and flow logic section is not required in such specification.
2. **Build hierarchically** - Reference separate specs for sub-features rather than duplicating details
3. **Extract common specs** - Move shared patterns across features into separate documents
4. **Avoid duplication** - When content overlaps between sections, decide on a single location
5. **Vary detail level** - Adapt depth based on audience, include only relevant parts of the template in the spec, high-level specs can be passed for further detailing
6. **Apply to all changes** - Use for both new features and modifications to existing functionality

---

## 1. Core Sections

### 1.1. Overview

Concise description of the solution which is specified in the document

### 1.2 Flow Logic

Define the system behavior through diagrams and/or text descriptions.

- **Happy path flow** - Primary user/system journey
- **Alternative flows** - Valid variations from the main path
- **Error handling** - Both backend and frontend error scenarios
- **State transitions** - When applicable

> Use sequence diagrams, flowcharts, or state diagrams as appropriate.
> Use Marmaid for diagrams when possible.

### 1.3 Validation & Business Logic

Document decision-making logic at each relevant flow step.

- **Business rules** - Link to requirements spec where possible
- **Data format validation** - Input/output constraints
- **Calculation logic** - Formulas, algorithms
- **Backend validation** - Server-side checks
- **Frontend validation** - Client-side checks

### 1.4 API Contracts

Define all service interfaces, linked to relevant flow steps.

- **GraphQL** - Queries, mutations, subscriptions
- **REST** - Endpoints, methods, request/response schemas
- **Celery** - Celery tasks
- **Message queues** - RabbitMQ, Kafka message formats
- **Other protocols** - WebSocket, gRPC as relevant

Specify errors returned by API in a format:
```
{
  id: str,
  params: dict,
  description: str
}
```
For example:
```
{
  id: "care_program_not_found",
  params: {"id": "019c4668-9095-7c7a-b7f2-b37f7d1bf9e8"},
  description: "Care program not found"
}
```

### 1.5 Data Models

Document data models as real python classes to reduce interpretation ambiguity.
- For Postgres storage documment them as SQLAlchemy declarative ORM classes.
- For FHIR storage documment them as Entity models and specify FHIR resource they will be mapped to.

### 1.6 Automated Tests

Specify testing strategy for backend and frontend.

- **E2E tests** - Critical user journeys to cover. Use Playwright for E2E tests.
- **Integration tests** - Service interaction scenarios.
- **Unit tests** - Key functions/components requiring coverage.

### 1.7 Infrastructure

Infrastructure changes specification when applicable.

- **Terraform/IaC** - Required cloud resources (NOT an actual terrafotm configuration, but high level description of expected changes)
- **CI/CD** - Pipeline changes needed
- **Monitoring** - Metrics, alerts, dashboards
- **Logging** - Log points, formats, retention

### 1.8 Feature Flags

- **Flag name** - Purpose and behavior when enabled/disabled

### 1.9 Migration Scripts

- **Database migrations** - Schema changes, data transformations

---

## 2. Extra Sections

### 2.1 UI/UX

Link to relevant flow steps; avoid duplicating flow logic.

- **Figma links** - Design references
- **Key interface details** - Important UI behaviors
- **Special considerations**:
  - Multi-language support
  - White labeling
  - Error display
  - Navigation confirmations
  - Loading states
- **Reusable components** - Components/hooks to create or reuse

### 2.2 Technical Stack

Include when library/framework choices are non-obvious.

- **Frontend** - Libraries, frameworks, tools
- **Backend** - Libraries, frameworks, tools

### 2.3 Code Structure Guidelines

> Often shared across features - consider linking to a common document.

- **Directory structure** - Where new code should live
- **Naming conventions** - Specific to this feature
- **Patterns to follow** - Existing patterns to maintain

### 2.4 Functional Requirements

> Prefer placing in requirements spec; use here only as a quick interim solution.

- Brief summary of what the feature should accomplish

### 2.5 References

- Links to requirements specifications
- Links to related tech design specs
- External documentation references

---

## References

- [A practical guide to writing technical specs](https://stackoverflow.blog/2020/04/06/a-practical-guide-to-writing-technical-specs/)

## Examples

See examples at @tech_design folder