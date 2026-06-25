# FC3: Feature Contract: Dashboard Management Hub of care pathways and programs

## Problem statement

The healthcare program administrator needs a single, unified management hub to organize, search, filter, and maintain all Care Pathways and Programs. This enables efficient monitoring of the health and growth of the therapeutic content library and allows performing critical management actions from one place.

## Glossary

- **Care Pathway**: A reusable building block that defines a sequence of therapeutic actions or interventions for patient care
- **Program**: A complete care package composed of one or more Care Pathways, representing a full treatment or wellness program for patients
- **Marketplace**: An external platform where published Programs can be exported for commercialization

## Requirements

### Requirement 1

**Use case:** Publish a Program

#### Main Flow
1. Administrator navigates to the Dashboard Management Hub
2. Administrator locates the Program to publish in the Programs section
3. Administrator opens the actions menu for the Program
4. Administrator selects "Publish" option
5. System changes the Program status to Published
6. System displays a success notification: "Status updated - '{name}' is now Published"
7. System updates the Program card to show a green Published badge

### Requirement 2

**Use case:** Archive a Care Pathway

#### Primary Actor

Healthcare Program Administrator

#### Secondary Actors

- System Database
- Notification Service

#### Preconditions

1. Administrator is authenticated and has permission to manage Care Pathways
2. The Care Pathway exists in the system
3. The Care Pathway is not currently assigned to any active Program

#### Trigger

Administrator decides to archive an outdated or unused Care Pathway to declutter the dashboard

#### Normal Flow

1. Administrator navigates to the Dashboard Management Hub
2. Administrator locates the Care Pathway to archive in the Care Pathways table
3. Administrator clicks on the actions menu (three-dot icon) for the Care Pathway row (see A2)
4. System displays available actions including "Archive"
5. Administrator selects "Archive" option (see E1)
6. System displays a confirmation dialog: "Are you sure you want to archive '{name}'? Archived items can be restored later."
7. Administrator confirms the action by clicking "Archive" (see A1)
8. System changes the Care Pathway status to Archived (see E2)
9. System removes the Care Pathway from the default dashboard view
10. System displays a success notification: "'{name}' has been archived"

#### Alternative Flows

**A1: Administrator cancels archiving**
1. At step 7, Administrator clicks "Cancel" instead of "Archive"
2. System closes the confirmation dialog
3. Care Pathway remains unchanged
4. Flow ends

**A2: Administrator archives from detail view**
1. At step 3, Administrator clicks on the Care Pathway name to open detail view
2. Administrator clicks "Archive" button in the detail view header
3. Flow continues from step 6

#### Exceptions

**E1: Care Pathway is assigned to active Program**
1. At step 5, System detects the Care Pathway is used in one or more active Programs
2. System displays error message: "Cannot archive '{name}'. It is currently used in the following active Programs: {program_list}. Remove it from these Programs first."
3. Flow ends

**E2: Network or system failure**
1. At step 8, System fails to update the database
2. System displays error message: "Failed to archive Care Pathway. Please try again."
3. Care Pathway status remains unchanged
4. Flow ends

#### Postconditions

1. Care Pathway status is set to "Archived"
2. Care Pathway no longer appears in the default dashboard view
3. Care Pathway can be found using the "Show Archived" filter option
4. Care Pathway can be restored to active status at any time
5. Dashboard statistics are updated to reflect the change in active Care Pathways count

#### Functional Requirements

1. The system shall provide an "Archive" action for each Care Pathway in the actions menu
2. The system shall prevent archiving of Care Pathways that are assigned to active Programs
3. The system shall display a confirmation dialog before archiving
4. The system shall maintain archived Care Pathways in the database with an "Archived" status
5. The system shall provide a filter option to display archived items
6. The system shall allow restoration of archived Care Pathways to active status
