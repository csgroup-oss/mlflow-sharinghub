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

"""Factory module.

Define factory method used to instantiate project client based
on configured auth mode.
"""

from mlflow_sharinghub.auth import RequestAuth
from mlflow_sharinghub.config import AppConfig

from .base import ProjectClient
from .gitlab import GitlabClient
from .sharinghub import SharinghubClient


def create_client(request_auth: RequestAuth) -> ProjectClient:
    """Returns project client based on configuration."""
    if AppConfig.GITLAB_URL:
        return GitlabClient(url=AppConfig.GITLAB_URL, request_auth=request_auth)

    if AppConfig.SHARINGHUB_URL:
        return SharinghubClient(url=AppConfig.SHARINGHUB_URL, request_auth=request_auth)

    msg = "Invalid server config."
    raise RuntimeError(msg)
