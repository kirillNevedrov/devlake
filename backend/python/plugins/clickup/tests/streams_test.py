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

import pytest

import pydevlake.domain_layer.ticket as ticket
from pydevlake.context import Context

import clickup.streams.tasks as tasks_module
from clickup.models import ClickUpConnection, ClickUpFolder, ClickUpScopeConfig, ClickUpTask
from clickup.streams.tasks import (
    ClickupTasks,
    ONE_DAY_MS,
    classify_type,
    compute_lead_time_minutes,
    map_status,
)


CONNECTION_ID = 1
FOLDER_ID = "457"
SPACE_ID = "s1"
TEAM_ID = "t1"

# Epoch-ms timestamps used across the tests.
CREATED_MS = "1693526400000"   # 2023-09-01T00:00:00Z
UPDATED_MS = "1693612800000"   # 2023-09-02T00:00:00Z
DONE_MS = "1693699200000"      # 2023-09-03T00:00:00Z

CREATED_DT = datetime.datetime(2023, 9, 1, tzinfo=datetime.timezone.utc)
UPDATED_DT = datetime.datetime(2023, 9, 2, tzinfo=datetime.timezone.utc)
DONE_DT = datetime.datetime(2023, 9, 3, tzinfo=datetime.timezone.utc)


def make_context(**scope_config_kwargs):
    connection = ClickUpConnection(id=CONNECTION_ID, name="conn", token="pk_test")
    scope = ClickUpFolder(
        id=FOLDER_ID, name="My Folder", connection_id=CONNECTION_ID,
        space_id=SPACE_ID, space_name="Space", team_id=TEAM_ID,
    )
    scope_config = ClickUpScopeConfig(id=1, name="cfg", **scope_config_kwargs)
    return Context(engine=None, connection=connection, scope=scope, scope_config=scope_config)


def default_patterns():
    return dict(
        issue_type_incident="incident",
        issue_type_bug="bug",
        issue_type_requirement="story|feature",
    )


def sample_task_json(**overrides):
    raw = {
        "id": "abc123",
        "custom_id": "GH-7",
        "name": "Login is broken",
        "text_content": "details",
        "description": "Users cannot log in",
        "status": {"status": "in progress", "type": "custom"},
        "date_created": CREATED_MS,
        "date_updated": UPDATED_MS,
        "date_closed": None,
        "date_done": None,
        "creator": {"id": "42", "username": "jane"},
        "priority": {"priority": "urgent"},
        "url": "https://app.clickup.com/t/abc123",
        "parent": None,
        "list": {"id": "900"},
        "folder": {"id": FOLDER_ID},
        "tags": [{"name": "incident"}],
        "assignees": [{"id": "42", "username": "jane"}],
    }
    raw.update(overrides)
    return raw


def convert(raw, ctx):
    stream = ClickupTasks('clickup')
    task = stream.extract(raw)
    task.connection_id = ctx.connection.id
    return list(stream.convert(task, ctx))


def first(results, cls):
    return next(r for r in results if isinstance(r, cls))


def all_of(results, cls):
    # Incident is not a subclass of Issue, but guard against any future overlap.
    return [r for r in results if type(r) is cls]


# --- extract -----------------------------------------------------------------

def test_extract_builds_tool_model_from_clickup_json():
    task = ClickupTasks('clickup').extract(sample_task_json())

    assert task.id == "abc123"
    assert task.custom_id == "GH-7"
    assert task.status == "in progress"
    assert task.status_type == "custom"
    assert task.creator_id == "42"
    assert task.creator_name == "jane"
    assert task.priority == "urgent"
    assert task.list_id == "900"
    assert task.folder_id == FOLDER_ID
    assert task.date_created == CREATED_DT
    assert task.date_updated == UPDATED_DT
    assert task.tags == [{"name": "incident"}]
    assert task.assignees == [{"id": "42", "username": "jane"}]


# --- type classification (REQ-4) ---------------------------------------------

def test_classification_precedence_incident_wins():
    config = make_context(**default_patterns()).scope_config
    tags = [{"name": "bug"}, {"name": "incident"}, {"name": "feature"}]
    assert classify_type(tags, config) == ticket.INCIDENT


def test_classification_bug_beats_requirement():
    config = make_context(**default_patterns()).scope_config
    tags = [{"name": "feature"}, {"name": "bug"}]
    assert classify_type(tags, config) == ticket.BUG


def test_classification_requirement_match():
    config = make_context(**default_patterns()).scope_config
    assert classify_type([{"name": "feature"}], config) == ticket.REQUIREMENT


def test_classification_is_case_insensitive():
    config = make_context(**default_patterns()).scope_config
    assert classify_type([{"name": "INCIDENT"}], config) == ticket.INCIDENT
    assert classify_type([{"name": "Bug"}], config) == ticket.BUG


def test_classification_no_match_defaults_to_requirement():
    config = make_context(**default_patterns()).scope_config
    assert classify_type([{"name": "chore"}], config) == ticket.REQUIREMENT


def test_classification_empty_patterns_default_to_requirement():
    # No patterns configured -> all tasks REQUIREMENT, no incidents (REQ-4 alt-4a).
    config = make_context().scope_config
    assert classify_type([{"name": "incident"}], config) == ticket.REQUIREMENT
    assert config.issue_type_incident is None


# --- status mapping (REQ-3.3) ------------------------------------------------

@pytest.mark.parametrize("status_type,expected", [
    ("open", ticket.TODO),
    ("custom", ticket.IN_PROGRESS),
    ("closed", ticket.DONE),
    ("done", ticket.DONE),
    ("something_else", ticket.OTHER),
    (None, ticket.OTHER),
])
def test_status_mapping_table(status_type, expected):
    status, original = map_status(status_type, "Original Name")
    assert status == expected
    assert original == "Original Name"


# --- lead time (REQ-3.4) -----------------------------------------------------

def test_lead_time_computed_when_resolved():
    # 2 days = 2880 minutes.
    assert compute_lead_time_minutes(CREATED_DT, DONE_DT) == 2880


def test_lead_time_none_when_unresolved():
    assert compute_lead_time_minutes(CREATED_DT, None) is None


# --- convert -----------------------------------------------------------------

def test_convert_incident_yields_issue_and_incident_with_matching_ids():
    ctx = make_context(**default_patterns())
    raw = sample_task_json(date_done=DONE_MS, status={"status": "done", "type": "done"})
    results = convert(raw, ctx)

    issue = first(results, ticket.Issue)
    board_issue = first(results, ticket.BoardIssue)
    issue_assignee = first(results, ticket.IssueAssignee)
    incident = first(results, ticket.Incident)
    incident_assignee = first(results, ticket.IncidentAssignee)

    expected_issue_id = "clickup:ClickUpTask:1:abc123"
    expected_board_id = "clickup:ClickUpFolder:1:457"

    assert issue.type == ticket.INCIDENT
    assert issue.issue_key == "GH-7"
    assert issue.title == "Login is broken"
    assert issue.description == "Users cannot log in"
    assert issue.url == "https://app.clickup.com/t/abc123"
    assert issue.status == ticket.DONE
    assert issue.original_status == "done"
    assert issue.created_date == CREATED_DT
    assert issue.updated_date == UPDATED_DT
    assert issue.resolution_date == DONE_DT
    assert issue.lead_time_minutes == 2880
    assert issue.creator_id == "42"
    assert issue.creator_name == "jane"
    assert issue.assignee_id == "42"
    assert issue.assignee_name == "jane"
    assert issue.priority == "urgent"
    assert issue.is_subtask is False

    # BoardIssue links the issue to the Folder's board.
    assert board_issue.board_id == expected_board_id
    assert board_issue.issue_id == expected_issue_id

    assert issue_assignee.issue_id == expected_issue_id
    assert issue_assignee.assignee_id == "42"
    assert issue_assignee.assignee_name == "jane"

    # Incident shares the issue's domain id and is scoped to the board.
    assert incident.incident_key == "GH-7"
    assert incident.status == ticket.DONE
    assert incident.resolution_date == DONE_DT
    assert incident.lead_time_minutes == 2880
    assert incident.table == "boards"
    assert incident.scope_id == expected_board_id

    assert incident_assignee.incident_id == expected_issue_id
    assert incident_assignee.assignee_id == "42"


def test_convert_non_incident_yields_no_incident():
    ctx = make_context(**default_patterns())
    raw = sample_task_json(tags=[{"name": "feature"}])
    results = convert(raw, ctx)

    assert first(results, ticket.Issue).type == ticket.REQUIREMENT
    assert all_of(results, ticket.Incident) == []
    assert all_of(results, ticket.IncidentAssignee) == []


def test_convert_issue_key_falls_back_to_task_id():
    ctx = make_context(**default_patterns())
    raw = sample_task_json(custom_id=None)
    issue = first(convert(raw, ctx), ticket.Issue)
    assert issue.issue_key == "abc123"


def test_convert_subtask_sets_parent_and_flag():
    ctx = make_context(**default_patterns())
    raw = sample_task_json(parent="parent999", tags=[{"name": "feature"}])
    issue = first(convert(raw, ctx), ticket.Issue)
    assert issue.is_subtask is True
    assert issue.parent_issue_id == "clickup:ClickUpTask:1:parent999"


def test_convert_emits_one_assignee_row_per_assignee():
    ctx = make_context(**default_patterns())
    raw = sample_task_json(
        tags=[{"name": "incident"}],
        assignees=[{"id": "1", "username": "a"}, {"id": "2", "username": "b"}],
    )
    results = convert(raw, ctx)
    assert {a.assignee_id for a in all_of(results, ticket.IssueAssignee)} == {"1", "2"}
    assert {a.assignee_id for a in all_of(results, ticket.IncidentAssignee)} == {"1", "2"}


# --- incremental collection (REQ-6) ------------------------------------------

def test_incremental_cutoff_subtracts_one_day():
    last_updated = 1_700_000_000_000
    cutoff = ClickupTasks.incremental_cutoff({'last_updated': last_updated}, incremental=True)
    assert cutoff == last_updated - ONE_DAY_MS


def test_incremental_cutoff_none_on_first_sync():
    assert ClickupTasks.incremental_cutoff({}, incremental=True) is None


def test_incremental_cutoff_none_on_full_resync():
    # Even with a stored high-water mark, a non-incremental run collects everything.
    state = {'last_updated': 1_700_000_000_000}
    assert ClickupTasks.incremental_cutoff(state, incremental=False) is None


class _FakeResponse:
    def __init__(self, tasks):
        self._tasks = tasks

    def get_url_with_query_string(self):
        return "https://api.clickup.com/api/v2/list/900/task"

    def __iter__(self):
        return iter(self._tasks)


class _FakeListResponse:
    def __init__(self, lists):
        self.json = {'lists': lists}


class _FakeAPI:
    def __init__(self, connection, tasks, captured):
        self._tasks = tasks
        self._captured = captured

    def lists(self, folder_id):
        return _FakeListResponse([{'id': '900'}])

    def tasks(self, list_id, date_updated_gt=None):
        self._captured['date_updated_gt'] = date_updated_gt
        return _FakeResponse(self._tasks)


def _patch_api(monkeypatch, tasks):
    captured = {}
    monkeypatch.setattr(
        tasks_module, 'ClickUpAPI',
        lambda connection: _FakeAPI(connection, tasks, captured),
    )
    return captured


def test_collect_tracks_high_water_mark(monkeypatch):
    ctx = make_context(**default_patterns())
    ctx.options = {'incremental': False}
    raw_tasks = [
        sample_task_json(id="t1", date_updated="100"),
        sample_task_json(id="t2", date_updated="300"),
        sample_task_json(id="t3", date_updated="200"),
    ]
    _patch_api(monkeypatch, raw_tasks)

    stream = ClickupTasks('clickup')
    emitted = list(stream.collect({}, ctx))

    assert [data['id'] for data, _ in emitted] == ["t1", "t2", "t3"]
    # Final state carries the maximum date_updated seen so far.
    assert [state['last_updated'] for _, state in emitted] == [100, 300, 300]
    # Collector adds the request url marker consumed by the framework.
    assert all('x_request_url' in data for data, _ in emitted)


def test_collect_passes_cutoff_when_incremental(monkeypatch):
    ctx = make_context(**default_patterns())
    ctx.options = {'incremental': True}
    last_updated = 1_700_000_000_000
    captured = _patch_api(monkeypatch, [sample_task_json(id="t1", date_updated="1700000100000")])

    stream = ClickupTasks('clickup')
    list(stream.collect({'last_updated': last_updated}, ctx))

    assert captured['date_updated_gt'] == last_updated - ONE_DAY_MS


def test_collect_full_sync_sends_no_date_filter(monkeypatch):
    ctx = make_context(**default_patterns())
    ctx.options = {'incremental': False}
    captured = _patch_api(monkeypatch, [sample_task_json(id="t1", date_updated="100")])

    stream = ClickupTasks('clickup')
    list(stream.collect({'last_updated': 999}, ctx))

    assert captured['date_updated_gt'] is None
