"""Auth views module.

Declare the blueprint for the views related to the authentication process.
"""

from flask import Blueprint, Response, redirect, request
from flask import url_for as flask_url_for

from mlflow_sharinghub._internal.server import url_for

from .api import get_session_auth, make_login_page
from .client import oauth

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
    session_auth = get_session_auth()

    if project := request.args.get("project"):
        session_auth[_REDIRECT_PROJECT_SESSION_KEY] = project
    else:
        session_auth.pop(_REDIRECT_PROJECT_SESSION_KEY, None)
    redirect_uri = flask_url_for("auth.authorize", _external=True)
    return oauth.gitlab.authorize_redirect(redirect_uri)


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
    return redirect(url_for("serve"))
