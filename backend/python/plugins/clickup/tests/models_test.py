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

from pydevlake.extractor import autoextract

from clickup.models import ClickUpTask


def test_parses_epoch_millis_string_to_datetime():
    task = ClickUpTask(
        id="abc123",
        name="Some task",
        list_id="900",
        folder_id="457",
        date_created="1693526400000",
        date_updated="1693612800000",
    )

    assert task.date_created == datetime.datetime(
        2023, 9, 1, 0, 0, tzinfo=datetime.timezone.utc
    )
    assert task.date_updated == datetime.datetime(
        2023, 9, 2, 0, 0, tzinfo=datetime.timezone.utc
    )


def test_missing_optional_date_fields_stay_none():
    task = ClickUpTask(
        id="abc123",
        name="Some task",
        list_id="900",
        folder_id="457",
        date_closed=None,
        date_done="",
    )

    assert task.date_created is None
    assert task.date_updated is None
    assert task.date_closed is None
    assert task.date_done is None


def test_extract_resolves_source_pointers_and_dates():
    raw = {
        "id": "abc123",
        "custom_id": "GH-7",
        "custom_item_id": 1300,
        "name": "Login is broken",
        "text_content": "details",
        "status": {"status": "in progress", "type": "custom"},
        "date_created": "1693526400000",
        "date_updated": "1693612800000",
        "date_closed": None,
        "creator": {"id": "42", "username": "jane"},
        "priority": {"priority": "urgent"},
        "url": "https://app.clickup.com/t/abc123",
        "list": {"id": "900"},
        "folder": {"id": "457"},
        "tags": [{"name": "incident"}],
        "assignees": [{"id": "42", "username": "jane"}],
    }

    task = autoextract(raw, ClickUpTask)

    assert task.id == "abc123"
    assert task.custom_id == "GH-7"
    assert task.custom_item_id == 1300
    assert task.status == "in progress"
    assert task.status_type == "custom"
    assert task.creator_id == "42"
    assert task.creator_name == "jane"
    assert task.priority == "urgent"
    assert task.list_id == "900"
    assert task.folder_id == "457"
    assert task.date_created == datetime.datetime(
        2023, 9, 1, 0, 0, tzinfo=datetime.timezone.utc
    )
    assert task.date_updated == datetime.datetime(
        2023, 9, 2, 0, 0, tzinfo=datetime.timezone.utc
    )
    assert task.date_closed is None
    assert task.tags == [{"name": "incident"}]
    assert task.assignees == [{"id": "42", "username": "jane"}]
