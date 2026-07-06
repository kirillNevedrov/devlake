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

from typing import Optional

from pydevlake.api import API, Paginator, Request, Response, request_hook


class ClickUpPaginator(Paginator):
    """
    ClickUp `GET tasks` pagination: 0-indexed `page` query param, 100 tasks per
    page, and a `last_page: bool` flag in the response body. Non-task responses
    (teams/spaces/folders/lists) have no `tasks` key, so `get_items` returns None
    and the framework treats them as unpaginated.
    """
    def get_items(self, response) -> Optional[list[object]]:
        return response.json.get('tasks')

    def get_next_page_id(self, response) -> Optional[int]:
        if response.json.get('last_page', True):
            return None
        current_page = int(response.request.query_args.get('page', 0))
        return current_page + 1

    def set_next_page_param(self, request, next_page_id):
        request.query_args['page'] = next_page_id


class ClickUpAPI(API):
    paginator = ClickUpPaginator()

    def __init__(self, connection):
        super().__init__(connection)

    @property
    def base_url(self):
        return self.connection.endpoint.rstrip('/')

    @request_hook
    def authenticate(self, request: Request):
        # ClickUp expects the personal token in the Authorization header
        # with no `Bearer` prefix (tech design §1.4).
        request.headers['Authorization'] = self.connection.token.get_secret_value()

    def teams(self):
        return self.get('team')

    def spaces(self, team_id: str):
        return self.get('team', team_id, 'space')

    def folders(self, space_id: str):
        return self.get('space', space_id, 'folder')

    def lists(self, folder_id: str):
        return self.get('folder', folder_id, 'list')

    def custom_items(self, team_id: str):
        # Custom task types for the workspace (team). No `tasks` key in the body,
        # so the paginator treats it as a single unpaginated response.
        return self.get('team', team_id, 'custom_item')

    def tasks(self, list_id: str, page: int = 0, date_updated_gt: Optional[int] = None):
        query_args = {
            'order_by': 'updated',
            'reverse': 'true',
            'include_closed': 'true',
            'subtasks': 'true',
            'page': page,
        }
        if date_updated_gt is not None:
            query_args['date_updated_gt'] = date_updated_gt
        return self.get('list', list_id, 'task', **query_args)
