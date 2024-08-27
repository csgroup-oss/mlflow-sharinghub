# Copyright 2024, CS GROUP - France, https://www.csgroup.eu/
#
# This file is part of SharingHub project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Permissions module."""

from dataclasses import dataclass

from mlflow.entities import Experiment
from mlflow.entities.model_registry import RegisteredModel

from mlflow_sharinghub._internal.server import get_project_path
from mlflow_sharinghub.auth import get_request_auth
from mlflow_sharinghub.clients import create_client
from mlflow_sharinghub.config import AppConfig
from mlflow_sharinghub.utils.gitlab import (
    DEVELOPER,
    GUEST,
    MAINTAINER,
    MINIMAL,
    NO_ACCESS,
    OWNER,
    REPORTER,
    GitlabRole,
)
from mlflow_sharinghub.utils.session import TimedSessionStore

_session_projects_access_level = TimedSessionStore[str, int](
    "projects", timeout=AppConfig.PROJECT_CACHE_TIMEOUT
)


@dataclass(unsafe_hash=True)
class Permission:
    """Represent simple CRUD permission with priority value."""

    priority: int
    can_create: bool
    can_read: bool
    can_update: bool
    can_delete: bool


_ROLES_PERMISSIONS = {
    NO_ACCESS: Permission(
        priority=0, can_create=False, can_read=False, can_update=False, can_delete=False
    ),
    MINIMAL: Permission(
        priority=10,
        can_create=False,
        can_read=False,
        can_update=False,
        can_delete=False,
    ),
    GUEST: Permission(
        priority=20, can_create=False, can_read=True, can_update=False, can_delete=False
    ),
    REPORTER: Permission(
        priority=30, can_create=False, can_read=True, can_update=False, can_delete=False
    ),
    DEVELOPER: Permission(
        priority=40, can_create=True, can_read=True, can_update=True, can_delete=True
    ),
    MAINTAINER: Permission(
        priority=50, can_create=True, can_read=True, can_update=True, can_delete=True
    ),
    OWNER: Permission(
        priority=60, can_create=True, can_read=True, can_update=True, can_delete=True
    ),
}


def session_save_access_level(project_path: str, role: GitlabRole) -> None:
    """Store GitLab role access level for the project in the session."""
    _session_projects_access_level.set(project_path, role.access_level)


def _get_permission_from_tags(obj: Experiment | RegisteredModel) -> Permission:
    project_path = get_project_path()
    obj_project_path = obj.tags.get(AppConfig.PROJECT_TAG, "").strip()
    if not obj_project_path or (project_path and project_path != obj_project_path):
        return _ROLES_PERMISSIONS[NO_ACCESS]
    return get_permission_for_project(obj_project_path)


def get_permission_for_project(project_path: str) -> Permission:
    """Return permission for project corresponding to given project_path."""
    project_access_level = _session_projects_access_level.get(project_path)
    if project_access_level is None:
        client = create_client(request_auth=get_request_auth())
        project = client.get_project(path=project_path)
        user_role = project.role if project else NO_ACCESS
        session_save_access_level(project_path, user_role)
    else:
        user_role = GitlabRole.from_access_level(project_access_level)
    return _ROLES_PERMISSIONS[user_role]


def get_permission_for_experiment(experiment: Experiment) -> Permission:
    """Return permission for experiment."""
    return _get_permission_from_tags(experiment)


def get_permission_for_registered_model(
    registered_model: RegisteredModel,
) -> Permission:
    """Return permission for registered model."""
    return _get_permission_from_tags(registered_model)
