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

from typing import Iterable, Optional

import pydevlake.domain_layer.ticket as ticket
from pydevlake import Context, DomainType, Stream, domain_id, logger

from clickup.api import ClickUpAPI
from clickup.models import ClickUpFolder, ClickUpScopeConfig, ClickUpTask

# One day in epoch milliseconds; the incremental overlap window (REQ-6, tech design §1.3).
ONE_DAY_MS = 86_400_000


class ClickupTasks(Stream):
    tool_model = ClickUpTask
    domain_types = [DomainType.TICKET, DomainType.CROSS]
    domain_models = [
        ticket.Issue,
        ticket.BoardIssue,
        ticket.IssueAssignee,
        ticket.Incident,
        ticket.IncidentAssignee,
    ]

    def collect(self, state, context: Context) -> Iterable[tuple[object, dict]]:
        api = ClickUpAPI(context.connection)
        folder: ClickUpFolder = context.scope

        cutoff = self.incremental_cutoff(state, context.incremental)
        if cutoff is not None:
            logger.info(
                f'ClickUp incremental collection for folder {folder.id}: '
                f'date_updated_gt={cutoff} (last_updated - 1 day overlap)'
            )
        else:
            logger.info(f'ClickUp full collection for folder {folder.id}')

        # High-water mark tracked across all lists of the folder; persisted in state.
        high_water_mark = state.get('last_updated')

        lists = api.lists(folder.id).json.get('lists', [])
        logger.info(f'ClickUp folder {folder.id} has {len(lists)} list(s)')

        for lst in lists:
            list_id = lst['id']
            response = api.tasks(list_id, date_updated_gt=cutoff)
            request_url = response.get_url_with_query_string()
            for raw_task in response:
                date_updated = raw_task.get('date_updated')
                if date_updated is not None and date_updated != "":
                    date_updated = int(date_updated)
                    if high_water_mark is None or date_updated > high_water_mark:
                        high_water_mark = date_updated
                raw_task['x_request_url'] = request_url
                yield raw_task, {'last_updated': high_water_mark}

    @staticmethod
    def incremental_cutoff(state: dict, incremental: bool) -> Optional[int]:
        """
        Compute the `date_updated_gt` filter (epoch ms) for an incremental run:
        last seen `date_updated` minus a one-day overlap window. Returns None for
        a first sync or a full re-sync, which collects everything (tech design §1.3).
        """
        last_updated = state.get('last_updated')
        if not incremental or last_updated is None:
            return None
        return int(last_updated) - ONE_DAY_MS

    def convert(self, task: ClickUpTask, ctx: Context) -> Iterable[object]:
        config: ClickUpScopeConfig = ctx.scope_config

        board_id = ctx.scope.domain_id()
        issue_id = task.domain_id()

        issue_type = classify_type(task.tags, config)
        status, original_status = map_status(task.status_type, task.status)
        resolution_date = task.date_done or task.date_closed
        lead_time_minutes = compute_lead_time_minutes(task.date_created, task.date_done)
        issue_key = task.custom_id or task.id
        parent_issue_id = (
            domain_id(ClickUpTask, ctx.connection.id, task.parent)
            if task.parent else None
        )

        assignee_id, assignee_name = _primary_assignee(task.assignees)

        yield ticket.Issue(
            url=task.url,
            issue_key=issue_key,
            title=task.name,
            description=task.description or task.text_content,
            type=issue_type,
            status=status,
            original_status=original_status,
            created_date=task.date_created,
            updated_date=task.date_updated,
            resolution_date=resolution_date,
            lead_time_minutes=lead_time_minutes,
            creator_id=task.creator_id,
            creator_name=task.creator_name,
            assignee_id=assignee_id,
            assignee_name=assignee_name,
            parent_issue_id=parent_issue_id,
            priority=task.priority,
            is_subtask=task.parent is not None,
        )

        yield ticket.BoardIssue(board_id=board_id, issue_id=issue_id)

        for aid, aname in _assignees(task.assignees):
            yield ticket.IssueAssignee(
                issue_id=issue_id,
                assignee_id=aid,
                assignee_name=aname,
            )

        if issue_type != ticket.INCIDENT:
            return

        yield ticket.Incident(
            url=task.url,
            incident_key=issue_key,
            title=task.name,
            description=task.description or task.text_content,
            status=status,
            original_status=original_status,
            created_date=task.date_created,
            updated_date=task.date_updated,
            resolution_date=resolution_date,
            lead_time_minutes=lead_time_minutes,
            creator_id=task.creator_id,
            creator_name=task.creator_name,
            assignee_id=assignee_id,
            assignee_name=assignee_name,
            parent_incident_id=parent_issue_id,
            priority=task.priority,
            table="boards",
            scope_id=board_id,
        )

        for aid, aname in _assignees(task.assignees):
            yield ticket.IncidentAssignee(
                incident_id=issue_id,
                assignee_id=aid,
                assignee_name=aname,
            )


def classify_type(tags: list[dict], config: ClickUpScopeConfig) -> str:
    """
    Classify a task into an issue type by matching its tag names against the
    INCIDENT/BUG/REQUIREMENT patterns from the scope config. Precedence is fixed
    (INCIDENT > BUG > REQUIREMENT) and the default — including when no pattern is
    configured — is REQUIREMENT (REQ-4). Matching is case-insensitive: the
    patterns are compiled with re.IGNORECASE by the scope config model.
    """
    tag_names = [tag.get('name', '') for tag in (tags or [])]
    for pattern, issue_type in (
        (config.issue_type_incident, ticket.INCIDENT),
        (config.issue_type_bug, ticket.BUG),
        (config.issue_type_requirement, ticket.REQUIREMENT),
    ):
        if pattern is not None and any(pattern.search(name) for name in tag_names):
            return issue_type
    return ticket.REQUIREMENT


def map_status(status_type: Optional[str], original_status: Optional[str]) -> tuple[str, Optional[str]]:
    """
    Map a ClickUp `status.type` to a normalized DevLake status, preserving the
    original ClickUp status name (REQ-3.3, tech design §1.3).
    """
    normalized = (status_type or '').lower()
    if normalized == 'open':
        status = ticket.TODO
    elif normalized == 'custom':
        status = ticket.IN_PROGRESS
    elif normalized in ('closed', 'done'):
        status = ticket.DONE
    else:
        status = ticket.OTHER
    return status, original_status


def compute_lead_time_minutes(date_created, date_done) -> Optional[int]:
    """Lead time in minutes from creation to resolution, when resolved (REQ-3.4)."""
    if date_created is None or date_done is None:
        return None
    return int((date_done - date_created).total_seconds() / 60)


def _primary_assignee(assignees: list[dict]) -> tuple[Optional[str], Optional[str]]:
    for aid, aname in _assignees(assignees):
        return aid, aname
    return None, None


def _assignees(assignees: list[dict]) -> Iterable[tuple[str, Optional[str]]]:
    for assignee in (assignees or []):
        aid = assignee.get('id')
        if aid is None:
            continue
        yield str(aid), assignee.get('username')
