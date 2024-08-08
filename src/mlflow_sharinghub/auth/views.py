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

"""Auth views module.

Declare the blueprint for the views related to the authentication process.
"""

from flask import Blueprint, Response, redirect, request

from mlflow_sharinghub._internal.server import url_for
from mlflow_sharinghub.config import AppConfig
from mlflow_sharinghub.utils.http import (
    clean_url,
    make_internal_error_response,
    url_add_query_params,
)

from .api import clear_auth_cache, get_session_auth, make_login_page
from .client import GITLAB_CLIENT, oauth

bp = Blueprint("auth", __name__, template_folder="templates")

_REDIRECT_PROJECT_SESSION_KEY = "_redirect_project"


@bp.route("/")
def index() -> str:
    """Returns the login page, regardless of our login state.

    The login page offer a login button if not already authenticated,
    and a logout button if authenticated.
    """
    return make_login_page()


@bp.route("/login")
def login() -> Response:
    """Login redirect to OpenID provider."""
    clear_auth_cache()
    session_auth = get_session_auth()
    project = request.args.get("project")

    if project:
        session_auth[_REDIRECT_PROJECT_SESSION_KEY] = project
    else:
        session_auth.pop(_REDIRECT_PROJECT_SESSION_KEY, None)

    if AppConfig.GITLAB_URL and (client := oauth.create_client(GITLAB_CLIENT)):
        redirect_uri = url_for("auth.authorize", _root=True, _external=True)
        return client.authorize_redirect(redirect_uri)

    if AppConfig.SHARINGHUB_URL:
        redirect_uri = clean_url(AppConfig.SHARINGHUB_URL + "/api/auth/login")
        redirect_uri = url_add_query_params(
            redirect_uri,
            {"redirect_uri": url_for("serve", _project=project, _external=True)},
        )
        return redirect(redirect_uri)

    return make_internal_error_response()


@bp.route("/authorize")
def authorize() -> Response:
    """Login callback view, retrieve the token and redirect to mlflow view."""
    token = oauth.gitlab.authorize_access_token()

    session_auth = get_session_auth()
    session_auth["access_token"] = token.get("access_token")
    session_auth["refresh_token"] = token.get("refresh_token")
    session_auth["userinfo"] = token.get("userinfo")

    return redirect(
        url_for("serve", _project=session_auth.get(_REDIRECT_PROJECT_SESSION_KEY))
    )


@bp.route("/logout")
def logout() -> Response:
    """Remove the token from the auth session."""
    session_auth = get_session_auth()
    session_auth.clear()
    if AppConfig.LOGIN_AUTO_REDIRECT:
        return redirect(url_for("auth.index"))
    return redirect(url_for("serve"))
