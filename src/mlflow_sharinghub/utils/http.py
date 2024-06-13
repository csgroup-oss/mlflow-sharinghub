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

"""HTTP module (utils).

Utilities related to HTTP requests and URLs.
"""

from typing import Literal
from urllib.parse import parse_qsl, quote, urlencode, urlparse, urlunparse

from flask import Response, make_response

HTTP_ERROR_RANGE = (400, 600)
HTTP_NOT_FOUND = 404
HTTP_UNAUTHORIZED = 401
HTTP_OK = 200

HttpMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
AuthType = Literal["Basic", "Bearer"]


def is_error(status_code: int) -> bool:
    """Return True if status_code is for an error, False otherwise."""
    return HTTP_ERROR_RANGE[0] < status_code < HTTP_ERROR_RANGE[1]


def clean_url(url: str, trailing_slash: bool = False) -> str:
    """Clean URL, ensure trailing slash or not."""
    u = urlparse(url)
    if u.scheme in ["http", "https"] and u.netloc:
        return url.removesuffix("/") + ("/" if trailing_slash else "")
    msg = f"Not a valid URL: '{url}'"
    raise ValueError(msg)


def url_add_query_params(url: str, query_params: dict) -> str:
    """Return URL with added query params from mapping."""
    url_parts = list(urlparse(url))
    url_parts[4] = urlencode(dict(parse_qsl(url_parts[4])) | query_params)
    return urlunparse(url_parts)


def urlsafe_path(path: str) -> str:
    """Quote path characters for safe URL parameter."""
    return quote(path, safe="")


def make_auth_response(auth_type: AuthType, /, realm: str = "mlflow") -> Response:
    """Returns HTTP 401 response with WWWW-Authenticate header."""
    res = make_response(
        "You are not authenticated. "
        "Please use the Authorization header for bearer auth, "
        "if you are using the MLflow client set MLFLOW_TRACKING_TOKEN."
    )
    res.status_code = 401
    res.headers["WWW-Authenticate"] = f'{auth_type} realm="{realm}"'
    return res


def make_forbidden_response() -> Response:
    """Returns HTTP 403 response."""
    res = make_response("Permission denied.")
    res.status_code = 403
    return res


def make_internal_error_response() -> Response:
    """Returns HTTP 500 response."""
    res = make_response("Internal server error, something wrong happened.")
    res.status_code = 500
    return res
