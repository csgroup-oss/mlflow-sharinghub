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

"""Auth API module.

Authentication-related functions.
"""

from dataclasses import dataclass, field

import requests
from flask import Response, make_response, redirect, render_template, request, session

from mlflow_sharinghub import __version__ as plugin_version
from mlflow_sharinghub._internal.server import get_project_path, url_for
from mlflow_sharinghub.config import AppConfig
from mlflow_sharinghub.utils.http import HTTP_OK, clean_url, make_auth_response
from mlflow_sharinghub.utils.session import TimedSessionStore

_AUTH_REQUEST_TIMEOUT = 10

_session_auth = TimedSessionStore[str, bool](
    "auth", timeout=AppConfig.SHARINGHUB_AUTH_CACHE_TIMEOUT
)


@dataclass
class RequestAuth:
    """Wrap request authentication info for clients."""

    headers: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, str] = field(default_factory=dict)


def get_session_auth() -> dict:
    """Returns the auth-related session data."""
    return session.setdefault("auth", {})


def clear_auth_cache() -> None:
    """Clear auth cache."""
    return _session_auth.clear()


def is_authenticated() -> bool:
    """Return True if user is authenticated."""
    request_auth = get_request_auth()
    if request_auth and AppConfig.GITLAB_URL:
        authenticated = _session_auth.get("gitlab")
        if authenticated is None:
            resp = requests.get(
                clean_url(AppConfig.GITLAB_URL) + "/api/v4/user",
                headers=request_auth.headers,
                timeout=_AUTH_REQUEST_TIMEOUT,
            )
            authenticated = resp.status_code == HTTP_OK
        return authenticated
    if (
        request_auth
        and AppConfig.SHARINGHUB_URL
        and not AppConfig.SHARINGHUB_AUTH_DEFAULT_TOKEN
    ):
        authenticated = _session_auth.get("sharinghub")
        if authenticated is None:
            resp = requests.get(
                clean_url(AppConfig.SHARINGHUB_URL) + "/api/auth/info",
                cookies=request_auth.cookies,
                timeout=_AUTH_REQUEST_TIMEOUT,
            )
            authenticated = resp.status_code == HTTP_OK
            _session_auth.set("sharinghub", authenticated)
        return authenticated
    return request_auth is not None


def get_request_auth() -> RequestAuth | None:
    """Return auth details if user is authenticated."""
    if bearer_token := _get_request_bearer_token():
        return RequestAuth(headers={"Authorization": f"Bearer {bearer_token}"})

    if AppConfig.GITLAB_URL and (
        session_token := get_session_auth().get("access_token")
    ):
        return RequestAuth(headers={"Authorization": f"Bearer {session_token}"})

    if AppConfig.SHARINGHUB_URL:
        if session_cookie := request.cookies.get(AppConfig.SHARINGHUB_SESSION_COOKIE):
            return RequestAuth(
                cookies={AppConfig.SHARINGHUB_SESSION_COOKIE: session_cookie}
            )

        if AppConfig.SHARINGHUB_AUTH_DEFAULT_TOKEN:
            return RequestAuth()

    return None


def _get_request_bearer_token() -> str | None:
    """Retrieves the token from authorization header bearer."""
    if request.authorization and request.authorization.type == "bearer":
        token = request.authorization.token
        if token:
            return token
    return None


def make_unauthorized_response() -> Response:
    """Create the response for unauthorized requests.

    - Request is sent from mlflow client: returns a simple HTTP 401 response
      with WWW-Authenticate header asking Bearer auth.
    - LOGIN_AUTO_REDIRECT is True: returns a HTTP 302 redirection to login view.
    """
    if "mlflow" in request.user_agent.string.lower():
        return make_auth_response("Bearer")
    if AppConfig.LOGIN_AUTO_REDIRECT:
        return redirect(url_for("auth.login", project=get_project_path()))
    return make_response(make_login_page(), 401)


def make_login_page() -> str:
    """Render the login page."""
    return render_template(
        "auth/index.html",
        url_for=url_for,
        plugin_version=plugin_version,
        gitlab=AppConfig.GITLAB_URL,
        sharinghub=AppConfig.SHARINGHUB_URL,
        session_auth=get_session_auth(),
        project_path=get_project_path(),
        authenticated=is_authenticated(),
    )
