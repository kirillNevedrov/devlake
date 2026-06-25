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

from pydantic import SecretStr, validator
from sqlalchemy import Column, JSON

from pydevlake import ScopeConfig, Field
from pydevlake.model import ToolScope, ToolModel, Connection

# needed to be able to run migrations
from clickup.migrations import *


DEFAULT_ENDPOINT = "https://api.clickup.com/api/v2"


class ClickUpConnection(Connection):
    token: SecretStr                            # personal API token
    endpoint: Optional[str] = DEFAULT_ENDPOINT
    rate_limit_per_hour: Optional[int] = 6000   # ~100/min default

    @validator('endpoint', pre=True, always=True)
    def default_endpoint(cls, value):
        """
        The config UI only carries `endpoint` as an initial value, not an editable
        field, so the connection is often persisted with an empty/missing endpoint.
        Pydantic's field default only fills absent/None keys, so an empty string
        would slip through and make `ClickUpAPI.base_url` empty, producing the bare
        request URL 'team' (MissingSchema). Coerce empty/missing back to the default.
        """
        if value is None or value == "":
            return DEFAULT_ENDPOINT
        return value


class ClickUpScopeConfig(ScopeConfig):
    # domain_types inherited (alias "entities"); defaults to all domain types
    issue_type_incident: Optional[re.Pattern]
    issue_type_bug: Optional[re.Pattern]
    issue_type_requirement: Optional[re.Pattern]

    @validator('issue_type_incident', 'issue_type_bug', 'issue_type_requirement', pre=True)
    def compile_case_insensitive(cls, value):
        """
        Compile the classification patterns with re.IGNORECASE so tag matching is
        case-insensitive (REQ-4.2, tech design §1.3). Empty/missing patterns stay
        None, which makes the corresponding type effectively unconfigured.
        """
        if value is None or value == "":
            return None
        if isinstance(value, re.Pattern):
            value = value.pattern
        return re.compile(value, re.IGNORECASE)


class ClickUpFolder(ToolScope, table=True):
    # ToolScope provides: id (pk), name, scope_config_id, connection_id (pk)
    space_id: str
    space_name: Optional[str]
    team_id: str


class ClickUpTask(ToolModel, table=True):
    id: str = Field(primary_key=True)
    custom_id: Optional[str]
    name: str
    text_content: Optional[str]
    description: Optional[str]
    status: Optional[str]            = Field(source='/status/status')
    status_type: Optional[str]       = Field(source='/status/type')
    date_created: Optional[datetime.datetime]
    date_updated: Optional[datetime.datetime]
    date_closed: Optional[datetime.datetime]
    date_done: Optional[datetime.datetime]
    creator_id: Optional[str]        = Field(source='/creator/id')
    creator_name: Optional[str]      = Field(source='/creator/username')
    priority: Optional[str]          = Field(source='/priority/priority')
    url: Optional[str]
    parent: Optional[str]            # parent task id (subtasks)
    list_id: str                     = Field(source='/list/id')
    folder_id: str                   = Field(source='/folder/id')
    tags: list[dict] = Field(default=[], sa_column=Column(JSON))            # [{"name": ...}, ...]
    assignees: list[dict] = Field(default=[], sa_column=Column(JSON))       # [{"id":..., "username":...}, ...]

    @validator('date_created', 'date_updated', 'date_closed', 'date_done', pre=True)
    def parse_epoch_millis(cls, value):
        """
        ClickUp date fields arrive as epoch-millisecond strings (or ints).
        Convert them to a timezone-aware datetime. Missing/empty values pass
        through as None.
        """
        if value is None or value == "":
            return None
        if isinstance(value, datetime.datetime):
            return value
        millis = int(value)
        return datetime.datetime.fromtimestamp(millis / 1000, tz=datetime.timezone.utc)
