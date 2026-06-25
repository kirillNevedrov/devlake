---
name: run-be-tests
description: Run backend tests in the fehap mono repository. Use to run backend tests.
allowed-tools: Bash
---

## Instructions

Run backend tests using docker compose. Execute the following steps sequentially from the monorepo root directory.

### Step 1: Start test docker compose project

```bash
docker compose -p fehap-server-local-test --profile test -f docker-compose.base.yaml -f docker-compose.local-test-override.yaml up --build
```

### Step 2: Initialize test environment

```bash
docker compose -p fehap-server-local-test --profile test -f docker-compose.base.yaml -f docker-compose.local-test-override.yaml run --rm backend python main_cli.py init-test-env --recreate-fehap-database
```

### Step 3: Run pytest tests

```bash
docker compose -p fehap-server-local-test --profile test -f docker-compose.base.yaml -f docker-compose.local-test-override.yaml run --rm backend pytest
```

### Step 4: Stop test docker compose project

```bash
docker compose -p fehap-server-local-test --profile test -f docker-compose.base.yaml -f docker-compose.local-test-override.yaml stop
```
