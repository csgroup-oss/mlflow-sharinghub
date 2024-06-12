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

Contains GitLab API client and data types.
"""

from typing import Any

import requests

from mlflow_sharinghub.utils.gitlab import GitlabREST_Project
from mlflow_sharinghub.utils.http import (
    HTTP_NOT_FOUND,
    HttpMethod,
    clean_url,
    url_add_query_params,
    urlsafe_path,
)


class GitlabClient:
    """Small GitLab client to interact with GitLab API."""

    def __init__(
        self,
        url: str,
        token: str,
        *,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.url = clean_url(url, trailing_slash=False)
        self.api_url = f"{self.url}/api"
        self.rest_url = f"{self.api_url}/v4"
        self.graphql_url = f"{self.api_url}/graphql"
        self.headers = {"Authorization": f"Bearer {token}"}
        if headers:
            self.headers |= headers

    def get_project(
        self, path: str, topics: list[str] | None = None
    ) -> GitlabREST_Project | None:
        """Retrieve the project from its path (with namespace) or None."""
        path = urlsafe_path(path)
        url = self._resolve_rest_api_url(
            f"/projects/{path}?simple=true",
        )
        try:
            project: GitlabREST_Project = self._request(url=url)
            if topics and not set(topics).issubset(project["topics"]):
                return None
            return project  # noqa: TRY300
        except requests.HTTPError as err:
            if err.response.status_code == HTTP_NOT_FOUND:
                return None
            raise

    def _resolve_rest_api_url(self, endpoint: str) -> str:
        endpoint = endpoint.removeprefix("/")
        return f"{self.rest_url}/{endpoint}"

    def _request(
        self,
        url: str,
        media_type: str = "json",
        **params: Any,
    ) -> dict[str, Any] | list[Any] | str | None:
        response = self._send_request(url, **params)
        match media_type:
            case "json":
                return response.json()
            case "text" | _:
                return response.text

    def _send_request(  # noqa: PLR0913
        self,
        url: str,
        *,
        method: HttpMethod = "GET",
        headers: dict[str, str] | None = None,
        query: dict[str, Any] | None = None,
        body: str | bytes | dict | None = None,
        timeout: int | None = None,
    ) -> requests.Response:
        if query is None:
            query = {}
        if headers is None:
            headers = {}

        remove_headers = ["host", "cookie"]
        headers = {
            k: v
            for k, v in headers.items()
            if k not in remove_headers and not k.startswith("x-")
        }

        url = url_add_query_params(url, query)
        method = method.upper()
        headers = self.headers | headers
        response = requests.request(
            method=method, url=url, headers=headers, data=body, timeout=timeout
        )
        response.raise_for_status()
        return response
