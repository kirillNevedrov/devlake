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

from pydevlake.api import APIException, Request, Response

from clickup.api import ClickUpAPI, ClickUpPaginator
from clickup.models import ClickUpConnection


def make_connection():
    return ClickUpConnection(name="test", token="pk_test_token")


def make_response(body: dict, status: int = 200, query_args=None):
    request = Request("https://api.clickup.com/api/v2/list/1/task", query_args=query_args or {})
    return Response(request=request, status=status, body=json.dumps(body).encode())


def test_base_url_strips_trailing_slash():
    connection = make_connection()
    connection.endpoint = "https://api.clickup.com/api/v2/"
    api = ClickUpAPI(connection)
    assert api.base_url == "https://api.clickup.com/api/v2"


def test_authenticate_sets_token_without_bearer_prefix():
    api = ClickUpAPI(make_connection())
    request = Request("https://api.clickup.com/api/v2/team")

    api.authenticate.apply(request, api)

    assert request.headers["Authorization"] == "pk_test_token"
    assert "Bearer" not in request.headers["Authorization"]


def test_handle_error_raises_on_4xx():
    api = ClickUpAPI(make_connection())
    response = make_response({"err": "Token invalid", "ECODE": "OAUTH_017"}, status=401)

    with pytest.raises(APIException):
        api.handle_error.apply(response, api)


def test_handle_error_passes_on_2xx():
    api = ClickUpAPI(make_connection())
    response = make_response({"tasks": []}, status=200)

    # Should not raise
    api.handle_error.apply(response, api)


def test_paginator_extracts_tasks():
    paginator = ClickUpPaginator()
    response = make_response({"tasks": [{"id": "1"}, {"id": "2"}], "last_page": False})

    assert paginator.get_items(response) == [{"id": "1"}, {"id": "2"}]


def test_paginator_returns_none_items_for_non_task_responses():
    paginator = ClickUpPaginator()
    response = make_response({"teams": [{"id": "1"}]})

    assert paginator.get_items(response) is None


def test_paginator_advances_page():
    paginator = ClickUpPaginator()
    response = make_response({"tasks": [], "last_page": False}, query_args={"page": 0})

    assert paginator.get_next_page_id(response) == 1


def test_paginator_stops_on_last_page():
    paginator = ClickUpPaginator()
    response = make_response({"tasks": [], "last_page": True}, query_args={"page": 3})

    assert paginator.get_next_page_id(response) is None


def test_paginator_stops_when_last_page_flag_missing():
    paginator = ClickUpPaginator()
    response = make_response({"tasks": []}, query_args={"page": 0})

    assert paginator.get_next_page_id(response) is None


def test_paginator_sets_next_page_param():
    paginator = ClickUpPaginator()
    request = Request("https://api.clickup.com/api/v2/list/1/task", query_args={"page": 0})

    paginator.set_next_page_param(request, 2)

    assert request.query_args["page"] == 2
