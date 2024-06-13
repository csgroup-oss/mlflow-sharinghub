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

"""SharingHub module (clients).

Contains SharingHub project client.
"""

import requests

from mlflow_sharinghub.auth import RequestAuth
from mlflow_sharinghub.config import AppConfig
from mlflow_sharinghub.utils.gitlab import GitlabRole
from mlflow_sharinghub.utils.http import (
    HTTP_NOT_FOUND,
    clean_url,
    urlsafe_path,
)

from .base import ProjectClient, ProjectInfo

_COLLECTION = AppConfig.SHARINGHUB_STAC_COLLECTION


class SharinghubClient(ProjectClient):
    """Small SharingHub client to interact with SharingHub API."""

    def __init__(self, url: str, request_auth: RequestAuth) -> None:
        self.url = clean_url(url)
        self.request_auth = request_auth

        self.api_url = f"{self.url}/api"
        self.stac_url = f"{self.api_url}/stac"
        self.headers = request_auth.headers
        self.cookies = request_auth.cookies

    def get_project(self, path: str) -> ProjectInfo | None:
        """Retrieve the project from its path (with namespace) or None."""
        path = urlsafe_path(path)
        url = self._resolve_stac_url(stac_id=path)
        try:
            response = requests.get(
                url=url, headers=self.headers, cookies=self.cookies, timeout=30
            )
            response.raise_for_status()
            project_data: dict = response.json()
            project_properties = project_data.get("properties", {})
            return ProjectInfo(
                id=project_properties.get("sharinghub:id"),
                path=path,
                role=GitlabRole.from_access_level(
                    project_properties.get("sharinghub:access-level")
                ),
            )
        except requests.HTTPError as err:
            if err.response.status_code == HTTP_NOT_FOUND:
                return None
            raise

    def _resolve_stac_url(self, stac_id: str) -> str:
        return f"{self.stac_url}/collections/{_COLLECTION}/items/{stac_id}"
