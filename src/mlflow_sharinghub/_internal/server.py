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

"""Internal server module (private).

Utilities to interact with the server.
"""

from typing import Any
from urllib.parse import urlparse, urlunparse

from flask import request
from flask import url_for as flask_url_for
from mlflow import MlflowException
from mlflow.protos.databricks_pb2 import BAD_REQUEST, INVALID_PARAMETER_VALUE
from mlflow.utils.rest_utils import _REST_API_PATH_PREFIX


def is_unprotected_route(path: str) -> bool:
    """Assert if given path is not protected by authentication."""
    return path.startswith(
        (
            "/health",
            "/version",
            "/auth",
            "/static-files/static",
            "/static-files/favicon.ico",
        )
    )


def is_proxy_artifact_path(path: str) -> bool:
    """Assert if path is for a proxyfied artifact."""
    return path.startswith(f"{_REST_API_PATH_PREFIX}/mlflow-artifacts/artifacts/")


def get_request_param(param: str) -> str:
    """Get request param value.

    Raises:
        mlflow.MlflowException: If params is not found.
    """
    if request.method == "GET":
        args = request.args
    elif request.method in ("POST", "PATCH", "DELETE"):
        args = request.json
    else:
        msg = f"Unsupported HTTP method '{request.method}'"
        raise MlflowException(msg, BAD_REQUEST)

    if param not in args:
        # Special handling for run_id
        if param == "run_id":
            return get_request_param("run_uuid")
        msg = f"Missing value for required parameter '{param}'"
        raise MlflowException(msg, INVALID_PARAMETER_VALUE)
    return args[param]


def get_project_path() -> str | None:
    """Retrieve project path from environ.

    The current project path is stored in the request `environ` by
    `mlflow_sharinghub.app.SharingHubDispatcher`. It is None if we
    are in the global view.
    """
    return request.environ.get("_PROJECT_PATH")


def url_for(endpoint: str, _project: str | None = None, **kwargs: Any) -> str:
    """Fix url resolve for project tracking route.

    Because of our route dispatching for project view the `url_for` of Flask
    don't resolve the correct url when in a project route, and point to the
    global view. This method takes it into account.
    """
    url = flask_url_for(endpoint, **kwargs)
    url_parts = list(urlparse(url))

    if not _project:
        _project = get_project_path()

    if _project:
        prefix = f"/{_project}/tracking"
        url_parts[2] = prefix + url_parts[2]

    return urlunparse(url_parts)
