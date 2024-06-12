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

"""App module.

Contains the `create_app` function declared as the "mlflow.app" entrypoint.
"""

from collections.abc import Callable
from wsgiref.types import StartResponse, WSGIEnvironment

from flask import Flask, Response
from flask_session import Session
from mlflow.server import app as mlflow_app

from mlflow_sharinghub import auth, config, hooks


class SharingHubDispatcher:
    """Flask dispatcher for project-path-based routing for SharingHub."""

    def __init__(self, app: Flask, path: str, project_path: str | None) -> None:
        self.app = app
        self.path = "/" + path
        self.project_path = project_path

    def __call__(
        self, environ: WSGIEnvironment, start_response: StartResponse
    ) -> Response:
        """Patch the request environment before each call."""
        # Patch PATH_INFO for correct dispatching behaviour
        environ["PATH_INFO"] = self.path
        # Store the project path in the request environ
        environ["_PROJECT_PATH"] = self.project_path
        # Fix http/https behind proxy
        if scheme := environ.get("HTTP_X_FORWARDED_PROTO"):
            environ["wsgi.url_scheme"] = scheme
        return self.app(environ, start_response)


def create_app(app: Flask = mlflow_app) -> Flask:
    """Create a wrapper flask app.

    Returns a flask app that handles root and project views routing
    and delegates the calls to the mlflow server app, while operating
    before and after requests hooks to alter the behavior.
    Also adds authentication routes.
    """
    # Configure
    app.config.from_object(config.AppConfig)

    # Requests hooks
    app.before_request(hooks.before_request_hook)
    app.after_request(hooks.after_request_hook)

    # Extra routes
    app.register_blueprint(auth.bp, url_prefix="/auth")

    # Setup session
    Session(app)

    # Setup oauth
    auth.oauth.init_app(app)

    wrapper_app = Flask(app.name + "+sharinghub")

    def _project_mlflow(
        project_path: str, path: str
    ) -> Callable[[WSGIEnvironment, StartResponse], Response]:
        return SharingHubDispatcher(app, path=path, project_path=project_path)

    def _main_mlflow(path: str) -> Callable[[WSGIEnvironment, StartResponse], Response]:
        return SharingHubDispatcher(app, path=path, project_path=None)

    wrapper_app.add_url_rule(
        "/<path:project_path>/tracking/",
        view_func=_project_mlflow,
        defaults={"path": ""},
    )
    wrapper_app.add_url_rule(
        "/<path:project_path>/tracking/<path:path>",
        view_func=_project_mlflow,
        methods=["GET", "POST", "PUT", "DELETE"],
    )
    wrapper_app.add_url_rule(
        "/",
        view_func=_main_mlflow,
        defaults={"path": ""},
    )
    wrapper_app.add_url_rule(
        "/<path:path>",
        view_func=_main_mlflow,
        methods=["GET", "POST", "PUT", "DELETE"],
    )

    return wrapper_app
