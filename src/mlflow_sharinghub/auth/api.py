"""Auth API module.

Authentication-related functions.
"""

from flask import Response, make_response, redirect, render_template, request, session

from mlflow_sharinghub import __version__ as plugin_version
from mlflow_sharinghub._internal.server import get_project_path, url_for
from mlflow_sharinghub.config import AppConfig
from mlflow_sharinghub.utils.http import make_auth_response


def get_session_auth() -> dict:
    """Returns the auth-related session data."""
    return session.setdefault("auth", {})


def get_request_token() -> str | None:
    """Retrieves the auth token, from authorization header or session."""
    if request.authorization and request.authorization.type == "bearer":
        token = request.authorization.token
        if token:
            return token

    session_token = get_session_auth().get("token")
    if session_token:
        return session_token

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
        project_path=get_project_path(),
        authenticated=bool(get_request_token()),
    )
