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

"""Base protocol for project clients."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from mlflow_sharinghub.auth import RequestAuth
from mlflow_sharinghub.utils.gitlab import GitlabRole


@dataclass
class ProjectInfo:
    """User project info."""

    id: int
    path: str
    role: GitlabRole


@runtime_checkable
class ProjectClient(Protocol):
    """Project client with request methods."""

    def __init__(self, url: str, request_auth: RequestAuth) -> None: ...

    def get_project(self, path: str) -> ProjectInfo | None:
        """Retrieve the project from its path (with namespace) or None."""
