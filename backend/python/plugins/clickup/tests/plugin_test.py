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

import json

import pytest

import pydevlake.domain_layer.ticket as ticket
from pydevlake.api import APIException, Request, Response
from pydevlake.testing import assert_valid_plugin

import clickup.main as main_module
from clickup.models import ClickUpConnection, ClickUpFolder
from clickup.main import ClickUpPlugin


CONNECTION_ID = 1


def make_connection():
    return ClickUpConnection(id=CONNECTION_ID, name="test", token="pk_test_token")


def make_response(body: dict, status: int = 200):
    request = Request("https://api.clickup.com/api/v2/team")
    return Response(request=request, status=status, body=json.dumps(body).encode())


class _FakeAPI:
    """Stand-in for ClickUpAPI returning recorded responses (tech design §1.6)."""

    def __init__(self, connection, *, teams=None, spaces=None, folders=None, error=None):
        self.connection = connection
        self._teams = teams or {}
        self._spaces = spaces or {}
        self._folders = folders or {}
        self._error = error

    def teams(self):
        if self._error is not None:
            raise self._error
        return make_response(self._teams)

    def spaces(self, team_id):
        return make_response(self._spaces.get(team_id, {"spaces": []}))

    def folders(self, space_id):
        return make_response(self._folders.get(space_id, {"folders": []}))


def patch_api(monkeypatch, **kwargs):
    monkeypatch.setattr(
        main_module, "ClickUpAPI",
        lambda connection: _FakeAPI(connection, **kwargs),
    )


# --- plugin validity -------------------------------------------------------

def test_valid_plugin():
    assert_valid_plugin(ClickUpPlugin())


def test_streams_expose_clickup_tasks():
    plugin = ClickUpPlugin()
    assert [s.__name__ for s in plugin.streams] == ["ClickupTasks"]


# --- test_connection -------------------------------------------------------

def test_test_connection_success(monkeypatch):
    patch_api(monkeypatch, teams={"teams": [{"id": "t1", "name": "Workspace"}]})

    result = ClickUpPlugin().test_connection(make_connection())

    assert result.success is True
    assert result.status == 200


def test_test_connection_invalid_token(monkeypatch):
    response = make_response({"err": "Token invalid", "ECODE": "OAUTH_017"}, status=401)
    patch_api(monkeypatch, error=APIException(response))

    result = ClickUpPlugin().test_connection(make_connection())

    assert result.success is False
    assert result.status == 401
    assert result.message == "Invalid ClickUp personal API token"


# --- remote_scope_groups ---------------------------------------------------

def test_remote_scope_groups_parses_teams_and_spaces(monkeypatch):
    patch_api(
        monkeypatch,
        teams={"teams": [{"id": "t1", "name": "Workspace"}]},
        spaces={"t1": {"spaces": [
            {"id": "s1", "name": "Space One"},
            {"id": "s2", "name": "Space Two"},
        ]}},
    )

    groups = list(ClickUpPlugin().remote_scope_groups(make_connection()))

    assert [(g.id, g.name) for g in groups] == [
        ("t1/s1", "Space One"),
        ("t1/s2", "Space Two"),
    ]


# --- remote_scopes ---------------------------------------------------------

def test_remote_scopes_parses_folders(monkeypatch):
    patch_api(
        monkeypatch,
        folders={"s1": {"folders": [
            {"id": "f1", "name": "Folder One", "space": {"id": "s1", "name": "Space One"}},
            {"id": "f2", "name": "Folder Two", "space": {"id": "s1", "name": "Space One"}},
        ]}},
    )

    folders = list(ClickUpPlugin().remote_scopes(make_connection(), "t1/s1"))

    assert all(isinstance(f, ClickUpFolder) for f in folders)
    assert [(f.id, f.name, f.space_id, f.space_name, f.team_id) for f in folders] == [
        ("f1", "Folder One", "s1", "Space One", "t1"),
        ("f2", "Folder Two", "s1", "Space One", "t1"),
    ]


# --- domain_scopes ---------------------------------------------------------

def test_domain_scopes_yields_board_per_folder():
    folder = ClickUpFolder(
        id="f1", name="Folder One", connection_id=CONNECTION_ID,
        space_id="s1", space_name="Space One", team_id="t1",
    )

    boards = list(ClickUpPlugin().domain_scopes(folder))

    assert len(boards) == 1
    board = boards[0]
    assert isinstance(board, ticket.Board)
    assert board.name == "Folder One"


def test_domain_scope_board_id_matches_stream_board_id():
    # The framework assigns board.id = folder.domain_id(); the stream uses the
    # same value for BoardIssue / Incident.scope_id (tech design §1.5).
    folder = ClickUpFolder(
        id="f1", name="Folder One", connection_id=CONNECTION_ID,
        space_id="s1", space_name="Space One", team_id="t1",
    )
    board = next(iter(ClickUpPlugin().domain_scopes(folder)))
    board.id = folder.domain_id()

    assert board.id == "clickup:ClickUpFolder:1:f1"
