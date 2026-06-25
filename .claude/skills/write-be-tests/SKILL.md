---
name: write-be-tests
description: Rules on how to write backend integration tests in the fehap mono repository. Follow these rules when writing the backend integration tests.
---

## Test structure

- Organize every test into three sections: **Arrange**, **Act**, **Assert**.
  - **Arrange**: Set up test data and configure fake dependencies. Initialize data using GraphQL API or existing application layer commands so initialization logic is aligned with real application logic.
  - **Act**: Execute the logic under test (e.g., GraphQL mutation or query). Pass full model with all fields so the mutation is fully covered. If there are multiple payload variations, cover all the main variations.
  - **Assert**: Verify the expected response and application state.
- Cover only the happy path in integration tests.

## Test data initialization

- Initialize shared read-only data for the test session with the `init-test-env` command so tests run faster without recreating shared data.
- Use existing application layer commands for initialization so the logic is aligned with real application behavior.
- Use the `system_tags` field in database models to mark shared test models for reuse. For example, the `User` model has a `system_tags` field; the `init_test_env` CLI command uses the `TEST_USER` constant to mark a created distributor admin, and the `distributor_admin` pytest fixture uses `TEST_USER` to query that object.
- Every test must run successfully regardless of current database state. For example, if a mutation validates name uniqueness, the test must pass a unique value on every run. If a test needs specific data in the database, initialize it in the Arrange section or in the `init-test-env` command.

## Assertion rules

- Assert the full response and database models so the mutation/query is fully covered.
- Assert fields one by one instead of comparing full models in a single assert, so model changes do not break all assertions at once.
- Assert all side effects: database state changes, scheduled Celery tasks (with fake services), changes in external services state (with fake services).

## Mocking policy

- **Do not** use `unittest.mock` helpers (`patch`, `Mock`, `MagicMock`). They make tests less reliable and less maintainable because changing or moving the mocked function can silently break the test or make assertions useless.

## Naming convention

Test name consists of up to 4 elements:
1. `test_` prefix
2. Name of the function under test (skip if similar to test file name)
3. Precondition (skip for happy path)
4. Expected result

Examples: `test_create_client_mutation_creates_client`, `test_create_client_mutation_returns_error_response_if_payload_is_not_valid`

## Code reuse

- Extract reusable GraphQL requests into shared functions to reduce duplication. For example, the `client { createClient }` mutation is extracted to `be\modules\client\infrastructure\tests\gql\shared.py` as the `create_client` function.

## File structure

Test file paths must mirror the mutations/queries file paths:

```
distributor
└── infrastructure
    ├── gql
    |   └── mutations
    |       └── create_client.py
    └── tests
        └── gql
            └── mutations
                └── test_create_client.py
```

### Examples

- `be\modules\client\infrastructure\tests\gql\mutations\test_create_client.py`
- `be\modules\client\infrastructure\tests\gql\queries\test_get_clients.py`
