"""Permissions module."""

from dataclasses import dataclass

from mlflow.entities import Experiment
from mlflow.entities.model_registry import RegisteredModel

from mlflow_sharinghub._internal.server import get_project_path
from mlflow_sharinghub.auth import get_request_token
from mlflow_sharinghub.config import AppConfig
from mlflow_sharinghub.utils.gitlab import (
    DEVELOPER,
    GUEST,
    MAINTAINER,
    MINIMAL,
    NO_ACCESS,
    OWNER,
    REPORTER,
    GitlabClient,
    GitlabREST_Project,
    GitlabRole,
)
from mlflow_sharinghub.utils.session import TimedSessionStore

_session_projects_access_level = TimedSessionStore[str, int](
    "projects", timeout=AppConfig.CACHE_TIMEOUT
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
        priority=40, can_create=True, can_read=True, can_update=True, can_delete=False
    ),
    MAINTAINER: Permission(
        priority=50, can_create=True, can_read=True, can_update=True, can_delete=True
    ),
    OWNER: Permission(
        priority=60, can_create=True, can_read=True, can_update=True, can_delete=True
    ),
}


def session_save_access_level(project: GitlabREST_Project | None, /) -> GitlabRole:
    """Store GitLab role access level for the project in the session."""
    user_role = NO_ACCESS
    if project:
        user_role = GitlabRole.from_project(project)
    _session_projects_access_level.set(
        project["path_with_namespace"], user_role.access_level
    )
    return user_role


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
        gitlab_client = GitlabClient(
            url=AppConfig.GITLAB_URL, token=get_request_token()
        )
        project = gitlab_client.get_project(project_path)
        user_role = session_save_access_level(project)
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
