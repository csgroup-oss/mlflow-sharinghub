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

"""GitLab module (utils).

Contains GitLab utilities.
"""

from dataclasses import dataclass
from typing import TypedDict


class _GitlabREST_Project_Permissions_Access(TypedDict):  # noqa: N801
    access_level: int


class _GitlabREST_Project_Permissions(TypedDict):  # noqa: N801
    project_access: _GitlabREST_Project_Permissions_Access | None
    group_access: _GitlabREST_Project_Permissions_Access | None


class GitlabREST_Project(TypedDict):  # noqa: N801
    """Type for GitLab project data returned by GitLab REST API."""

    id: int
    description: str | None
    name: str
    name_with_namespace: str
    path: str
    path_with_namespace: str
    web_url: str
    created_at: str
    last_activity_at: str
    default_branch: str | None
    topics: list[str]
    star_count: int
    permissions: _GitlabREST_Project_Permissions


@dataclass
class GitlabRole:
    """Represents a GitLab role (member access)."""

    name: str
    access_level: int

    def __hash__(self) -> int:
        return hash(self.access_level)

    @staticmethod
    def from_gitlab_project(project: GitlabREST_Project) -> "GitlabRole":
        """Read the GitLab project and return a GitlabRole."""
        project_permissions = project.get("permissions", {})
        project_access = project_permissions.get("project_access")
        group_access = project_permissions.get("group_access")
        project_access = {} if project_access is None else project_access
        group_access = {} if group_access is None else group_access
        access_level = max(
            project_access.get("access_level", NO_ACCESS.access_level),
            group_access.get("access_level", NO_ACCESS.access_level),
        )
        return _ALL_ROLES.get(access_level, NO_ACCESS)

    @staticmethod
    def from_access_level(access_level: int) -> "GitlabRole":
        """Return the GitlabRole from an access_level, fallback to NO_ACCESS."""
        return _ALL_ROLES.get(access_level, NO_ACCESS)


NO_ACCESS = GitlabRole(
    name="No access",
    access_level=0,
)

MINIMAL = GitlabRole(
    name="Minimal",
    access_level=5,
)

GUEST = GitlabRole(
    name="Guest",
    access_level=10,
)

REPORTER = GitlabRole(
    name="Reporter",
    access_level=20,
)

DEVELOPER = GitlabRole(
    name="Developer",
    access_level=30,
)

MAINTAINER = GitlabRole(
    name="Maintainer",
    access_level=40,
)

OWNER = GitlabRole(
    name="Owner",
    access_level=50,
)


_ALL_ROLES = {
    NO_ACCESS.access_level: NO_ACCESS,
    MINIMAL.access_level: MINIMAL,
    GUEST.access_level: GUEST,
    REPORTER.access_level: REPORTER,
    DEVELOPER.access_level: DEVELOPER,
    MAINTAINER.access_level: MAINTAINER,
    OWNER.access_level: OWNER,
}
