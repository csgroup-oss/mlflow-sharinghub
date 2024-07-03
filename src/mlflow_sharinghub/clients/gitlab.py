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

"""GitLab module (clients).

Contains GitLab project client.
"""

import requests

from mlflow_sharinghub.auth import RequestAuth
from mlflow_sharinghub.config import AppConfig
from mlflow_sharinghub.utils.gitlab import GitlabREST_Project, GitlabRole
from mlflow_sharinghub.utils.http import (
    HTTP_NOT_FOUND,
    clean_url,
    urlsafe_path,
)

from .base import ProjectClient, ProjectInfo

_TOPICS = [*AppConfig.GITLAB_MANDATORY_TOPICS]


class GitlabClient(ProjectClient):
    """Small GitLab client to interact with GitLab API."""

    def __init__(self, url: str, request_auth: RequestAuth) -> None:
        self.url = clean_url(url)
        self.request_auth = request_auth

        self.api_url = f"{self.url}/api"
        self.rest_url = f"{self.api_url}/v4"
        self.headers = request_auth.headers
        self.cookies = request_auth.cookies

    def get_project(self, path: str) -> ProjectInfo | None:
        """Retrieve the project from its path (with namespace) or None."""
        path = urlsafe_path(path)
        url = self._resolve_rest_api_url(f"/projects/{path}?simple=true")
        try:
            response = requests.get(
                url=url, headers=self.headers, cookies=self.cookies, timeout=30
            )
            response.raise_for_status()
            project_data: GitlabREST_Project = response.json()
            if _TOPICS and not set(_TOPICS).issubset(project_data["topics"]):
                return None
            return ProjectInfo(
                id=project_data["id"],
                path=path,
                role=GitlabRole.from_gitlab_project(project_data),
            )
        except requests.HTTPError as err:
            if err.response.status_code == HTTP_NOT_FOUND:
                return None
            raise

    def _resolve_rest_api_url(self, endpoint: str) -> str:
        endpoint = endpoint.removeprefix("/")
        return f"{self.rest_url}/{endpoint}"
