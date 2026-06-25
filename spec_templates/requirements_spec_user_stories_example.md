# FC3: Feature Contract: Dashboard Management Hub of care pathways and programs

## Problem statement

The healthcare program administrator needs a single, unified management hub to organize, search, filter, and maintain all Care Pathways and Programs. This enables efficient monitoring of the health and growth of the therapeutic content library and allows performing critical management actions from one place.

## Glossary

- **Care Pathway**: A reusable building block that defines a sequence of therapeutic actions or interventions for patient care
- **Program**: A complete care package composed of one or more Care Pathways, representing a full treatment or wellness program for patients
- **Marketplace**: An external platform where published Programs can be exported for commercialization

## Requirements

### Requirement 1

**User Story:** As an administrator, I want to view all my Care Pathways and Programs in a single dashboard, so that I can have a complete overview of my therapeutic content library.

#### Acceptance Criteria

1. Given I view the dashboard, I see two main sections: Care Pathways and Programs
2. Given I view the dashboard, I only see Care Pathways and Programs belonging to my workspace
3. Given I view the Care Pathways section, I see a table with columns: Name, Description, Actions Count, and Status
4. Given I view the Programs section, I see programs displayed as cards in a grid layout
5. Given I view the dashboard, I see a stats overview showing: Active Programs count, Care Pathways count, Active Patients count, and Total Actions count

### Requirement 2

**User Story:** As an administrator, I want to search and filter Care Pathways and Programs, so that I can quickly find specific content in my library.

#### Acceptance Criteria

1. Given I enter a search term, both Care Pathways and Programs sections filter in real-time to show matching items
2. Given I search by name, description, or tags, the system returns relevant results from both sections
3. Given I want to focus on a specific content type, I can use a Type filter with options: "All", "Programs only", or "Pathways only"
4. Given I select "Programs only", only the Programs section is visible
5. Given I select "Pathways only", only the Care Pathways section is visible
6. Given I apply a Status filter, only items matching the selected status are displayed
7. Given my search returns no results, I see a message "No items match your filters" with an option to clear filters
