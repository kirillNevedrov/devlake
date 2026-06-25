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

import datetime
import re
from typing import Optional

from pydantic import SecretStr
from sqlalchemy import Column, JSON

from pydevlake import ScopeConfig, Field
from pydevlake.migration import migration, MigrationScriptBuilder
from pydevlake.model import ToolScope, ToolModel, Connection


@migration(20260625000001, name="initialize schemas for ClickUp")
def init_schemas(b: MigrationScriptBuilder):
    # Tool tables only. The domain tables (issues, incidents, boards,
    # board_issues, issue_assignees, incident_assignees) are owned by the Go
    # core migrations and MUST NOT be created here (tech design §1.9).
    # Models are declared locally as the frozen schema snapshot for this
    # migration, mirroring the azuredevops convention (non-table classes so
    # they do not clash with the table=True models in clickup/models.py).

    class ClickUpConnection(Connection):
        token: SecretStr
        endpoint: Optional[str] = "https://api.clickup.com/api/v2"
        rate_limit_per_hour: Optional[int] = 6000

    class ClickUpScopeConfig(ScopeConfig):
        issue_type_incident: Optional[re.Pattern]
        issue_type_bug: Optional[re.Pattern]
        issue_type_requirement: Optional[re.Pattern]

    class ClickUpFolder(ToolScope):
        space_id: str
        space_name: Optional[str]
        team_id: str

    class ClickUpTask(ToolModel):
        id: str = Field(primary_key=True)
        custom_id: Optional[str]
        name: str
        text_content: Optional[str]
        description: Optional[str]
        status: Optional[str]
        status_type: Optional[str]
        date_created: Optional[datetime.datetime]
        date_updated: Optional[datetime.datetime]
        date_closed: Optional[datetime.datetime]
        date_done: Optional[datetime.datetime]
        creator_id: Optional[str]
        creator_name: Optional[str]
        priority: Optional[str]
        url: Optional[str]
        parent: Optional[str]
        list_id: str
        folder_id: str
        tags: list[dict] = Field(default=[], sa_column=Column(JSON))
        assignees: list[dict] = Field(default=[], sa_column=Column(JSON))

    b.create_tables(
        ClickUpConnection,
        ClickUpScopeConfig,
        ClickUpFolder,
        ClickUpTask,
    )
