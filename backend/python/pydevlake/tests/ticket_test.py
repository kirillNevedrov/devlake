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

from pydevlake.domain_layer import ticket


def test_constants():
    assert ticket.BUG == "BUG"
    assert ticket.REQUIREMENT == "REQUIREMENT"
    assert ticket.INCIDENT == "INCIDENT"
    assert ticket.TASK == "TASK"
    assert ticket.SUBTASK == "SUBTASK"
    assert ticket.TODO == "TODO"
    assert ticket.IN_PROGRESS == "IN_PROGRESS"
    assert ticket.DONE == "DONE"
    assert ticket.OTHER == "OTHER"


def test_board():
    board = ticket.Board(
        id="clickup:Board:1:42",
        name="Sprint Board",
        description="desc",
        url="https://app.clickup.com/42",
        created_date=datetime(2026, 1, 1),
        type="scrum",
    )
    assert ticket.Board.__tablename__ == "boards"
    assert board.id == "clickup:Board:1:42"
    assert board.name == "Sprint Board"
    assert board.type == "scrum"


def test_issue():
    issue = ticket.Issue(
        id="clickup:Issue:1:abc",
        issue_key="abc",
        title="Fix login",
        type=ticket.BUG,
        status=ticket.IN_PROGRESS,
        original_status="in progress",
    )
    assert ticket.Issue.__tablename__ == "issues"
    assert issue.issue_key == "abc"
    assert issue.title == "Fix login"
    assert issue.type == "BUG"
    assert issue.status == "IN_PROGRESS"
    # default value for is_subtask
    assert issue.is_subtask is False


def test_board_issue():
    board_issue = ticket.BoardIssue(board_id="b1", issue_id="i1")
    assert ticket.BoardIssue.__tablename__ == "board_issues"
    assert board_issue.board_id == "b1"
    assert board_issue.issue_id == "i1"


def test_issue_assignee():
    assignee = ticket.IssueAssignee(
        issue_id="i1", assignee_id="a1", assignee_name="Alice"
    )
    assert ticket.IssueAssignee.__tablename__ == "issue_assignees"
    assert assignee.issue_id == "i1"
    assert assignee.assignee_id == "a1"
    assert assignee.assignee_name == "Alice"


def test_incident():
    incident = ticket.Incident(
        id="clickup:Incident:1:xyz",
        incident_key="xyz",
        title="Outage",
        status=ticket.DONE,
        scope_id="42",
    )
    assert ticket.Incident.__tablename__ == "incidents"
    assert incident.incident_key == "xyz"
    assert incident.title == "Outage"
    assert incident.status == "DONE"
    assert incident.scope_id == "42"
    # default value for table
    assert incident.table == "boards"


def test_incident_assignee():
    assignee = ticket.IncidentAssignee(
        incident_id="inc1", assignee_id="a1", assignee_name="Bob"
    )
    assert ticket.IncidentAssignee.__tablename__ == "incident_assignees"
    assert assignee.incident_id == "inc1"
    assert assignee.assignee_id == "a1"
    assert assignee.assignee_name == "Bob"
