# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pydevlake.migration import MIGRATION_SCRIPTS, CreateTable

# Importing the module registers the migration into MIGRATION_SCRIPTS.
import clickup.migrations  # noqa: F401


INIT_VERSION = 20260625000001

EXPECTED_TOOL_TABLES = {
    "_tool_clickup_clickupconnections",
    "_tool_clickup_clickupscopeconfigs",
    "_tool_clickup_clickupfolders",
    "_tool_clickup_clickuptasks",
}

# Domain tables are owned by the Go core; the plugin migration must never touch them.
FORBIDDEN_DOMAIN_TABLES = {
    "issues",
    "incidents",
    "boards",
    "board_issues",
    "issue_assignees",
    "incident_assignees",
}


def get_init_migration():
    scripts = [s for s in MIGRATION_SCRIPTS if s.version == INIT_VERSION]
    assert len(scripts) == 1, "ClickUp init migration should be registered exactly once"
    return scripts[0]


def test_init_migration_is_registered():
    script = get_init_migration()
    assert script.name == "initialize schemas for ClickUp"


def test_init_migration_creates_only_tool_tables():
    script = get_init_migration()
    created_tables = {
        op.model_info.table_name
        for op in script.operations
        if isinstance(op, CreateTable)
    }
    assert created_tables == EXPECTED_TOOL_TABLES


def test_init_migration_creates_no_domain_tables():
    script = get_init_migration()
    created_tables = {
        op.model_info.table_name
        for op in script.operations
        if isinstance(op, CreateTable)
    }
    assert created_tables.isdisjoint(FORBIDDEN_DOMAIN_TABLES)
