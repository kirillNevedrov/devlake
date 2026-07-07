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


from datetime import datetime
from typing import Optional

from sqlmodel import Field

from pydevlake.model import DomainModel, DomainScope, NoPKModel


# Issue type constants
BUG, REQUIREMENT, INCIDENT, TASK, SUBTASK = "BUG", "REQUIREMENT", "INCIDENT", "TASK", "SUBTASK"
# Issue/Incident status constants
TODO, IN_PROGRESS, DONE, OTHER = "TODO", "IN_PROGRESS", "DONE", "OTHER"


class Board(DomainScope, table=True):
    __tablename__ = "boards"
    name: str
    description: Optional[str]
    url: Optional[str]
    created_date: Optional[datetime]
    type: Optional[str]


class Issue(DomainModel, table=True):
    __tablename__ = "issues"
    url: Optional[str]
    issue_key: str
    title: str
    description: Optional[str]
    type: str                         # INCIDENT | BUG | REQUIREMENT
    original_type: Optional[str]
    status: str                       # TODO | IN_PROGRESS | DONE | OTHER
    original_status: Optional[str]
    created_date: Optional[datetime]
    updated_date: Optional[datetime]
    resolution_date: Optional[datetime]
    lead_time_minutes: Optional[int]
    creator_id: Optional[str]
    creator_name: Optional[str]
    assignee_id: Optional[str]
    assignee_name: Optional[str]
    parent_issue_id: Optional[str]
    priority: Optional[str]
    is_subtask: bool = False


class BoardIssue(NoPKModel, table=True):
    __tablename__ = "board_issues"
    board_id: str = Field(primary_key=True)
    issue_id: str = Field(primary_key=True)


class IssueAssignee(NoPKModel, table=True):
    __tablename__ = "issue_assignees"
    issue_id: str = Field(primary_key=True)
    assignee_id: str = Field(primary_key=True)
    assignee_name: Optional[str]


class Incident(DomainModel, table=True):
    __tablename__ = "incidents"
    url: Optional[str]
    incident_key: str
    title: str
    description: Optional[str]
    status: str
    original_status: Optional[str]
    created_date: Optional[datetime]
    updated_date: Optional[datetime]
    resolution_date: Optional[datetime]
    lead_time_minutes: Optional[int]    # MTTR input for DORA
    creator_id: Optional[str]
    creator_name: Optional[str]
    assignee_id: Optional[str]
    assignee_name: Optional[str]
    parent_incident_id: Optional[str]
    priority: Optional[str]
    table: str = Field(default="boards")   # incident.table -> "boards"
    scope_id: str                          # board id (Folder)


class IncidentAssignee(NoPKModel, table=True):
    __tablename__ = "incident_assignees"
    incident_id: str = Field(primary_key=True)
    assignee_id: str = Field(primary_key=True)
    assignee_name: Optional[str]
