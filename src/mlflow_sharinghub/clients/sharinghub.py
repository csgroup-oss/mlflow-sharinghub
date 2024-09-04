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
from mlflow_sharinghub.utils.gitlab import (
    DEVELOPER,
    GUEST,
    MAINTAINER,
    NO_ACCESS,
)
from mlflow_sharinghub.utils.http import (
    HTTP_NOT_FOUND,
    clean_url,
    urlsafe_path,
)

from .base import ProjectClient, ProjectInfo

_CATEGORY = AppConfig.SHARINGHUB_STAC_COLLECTION

_ACCESS_LEVEL_MAPPING = {
    0: NO_ACCESS,
    1: GUEST,
    2: DEVELOPER,
    3: MAINTAINER,
}


class SharinghubClient(ProjectClient):
    """Small SharingHub client to interact with SharingHub API."""

    def __init__(self, url: str, request_auth: RequestAuth) -> None:
        self.url = clean_url(url)
        self.request_auth = request_auth

        self.api_url = f"{self.url}/api"
        self.checker_url = f"{self.api_url}/check"
        self.headers = request_auth.headers
        self.cookies = request_auth.cookies

    def get_project(self, path: str) -> ProjectInfo | None:
        """Retrieve the project from its path (with namespace) or None."""
        path = urlsafe_path(path)
        url = self._resolve_check_url(stac_id=path)
        try:
            response = requests.get(
                url=url, headers=self.headers, cookies=self.cookies, timeout=30
            )
            response.raise_for_status()
            project_data: dict = response.json()

            if _CATEGORY not in project_data["categories"]:
                return None

            return ProjectInfo(
                id=project_data["id"],
                path=path,
                role=_ACCESS_LEVEL_MAPPING.get(project_data["access_level"], NO_ACCESS),
            )
        except requests.HTTPError as err:
            if err.response.status_code == HTTP_NOT_FOUND:
                return None
            raise

    def _resolve_check_url(self, stac_id: str) -> str:
        return f"{self.checker_url}/{stac_id}?info=true"
