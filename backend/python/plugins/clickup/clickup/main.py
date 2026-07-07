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

from typing import Iterable

from pydevlake import Plugin, RemoteScopeGroup, TestConnectionResult
from pydevlake.api import APIException
import pydevlake.domain_layer.ticket as ticket

from clickup.api import ClickUpAPI
from clickup.models import ClickUpConnection, ClickUpFolder, ClickUpScopeConfig
from clickup.streams.tasks import ClickupTasks


class ClickUpPlugin(Plugin):

    @property
    def connection_type(self):
        return ClickUpConnection

    @property
    def tool_scope_type(self):
        return ClickUpFolder

    @property
    def scope_config_type(self):
        return ClickUpScopeConfig

    def domain_scopes(self, folder: ClickUpFolder) -> Iterable[ticket.Board]:
        # One DevLake Board per ClickUp Folder (REQ-2). The framework assigns
        # `id = folder.domain_id()`, matching the board id the stream uses for
        # BoardIssue / Incident.scope_id (tech design §1.5).
        yield ticket.Board(
            name=folder.name,
            url=f"{self._space_url(folder)}",
            type="clickup",
        )

    @staticmethod
    def _space_url(folder: ClickUpFolder) -> str:
        return f"https://app.clickup.com/{folder.team_id}/v/f/{folder.id}"

    def remote_scope_groups(self, connection: ClickUpConnection) -> Iterable[RemoteScopeGroup]:
        # Each (team, space) pair is a selectable group; its folders are the scopes
        # (tech design §1.2-A). Group id encodes `team_id/space_id`.
        api = ClickUpAPI(connection)
        for team in api.teams().json.get('teams', []):
            team_id = team['id']
            for space in api.spaces(team_id).json.get('spaces', []):
                yield RemoteScopeGroup(
                    id=f"{team_id}/{space['id']}",
                    name=space.get('name', space['id']),
                )

    def remote_scopes(self, connection: ClickUpConnection, group_id: str) -> Iterable[ClickUpFolder]:
        team_id, space_id = group_id.split('/')
        api = ClickUpAPI(connection)
        space_name = None
        for folder in api.folders(space_id).json.get('folders', []):
            space = folder.get('space') or {}
            space_name = space.get('name', space_name)
            yield ClickUpFolder(
                id=folder['id'],
                name=folder['name'],
                space_id=space_id,
                space_name=space.get('name', space_name),
                team_id=team_id,
            )

    def test_connection(self, connection: ClickUpConnection) -> TestConnectionResult:
        api = ClickUpAPI(connection)
        message = None
        try:
            res = api.teams()
        except APIException as e:
            res = e.response
            if res.status == 401:
                message = "Invalid ClickUp personal API token"
        return TestConnectionResult.from_api_response(res, message)

    @property
    def streams(self):
        return [ClickupTasks]


if __name__ == '__main__':
    ClickUpPlugin.start()
