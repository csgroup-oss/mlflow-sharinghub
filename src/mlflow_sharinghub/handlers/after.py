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

"""After request hooks handlers."""

import re
from collections.abc import Callable
from typing import Any

from flask import Response, request
from mlflow.protos.model_registry_pb2 import (
    CreateRegisteredModel,
    SearchModelVersions,
    SearchRegisteredModels,
)
from mlflow.protos.service_pb2 import CreateExperiment, SearchExperiments, SearchRuns
from mlflow.server.handlers import catch_mlflow_exception, get_endpoints

from mlflow_sharinghub import filters, initializers, patch
from mlflow_sharinghub.utils.http import is_error

MAIN_JS_FILE_PATH = re.compile(r"/static-files/static/js/main.[a-z0-9]+.js")

AFTER_REQUEST_PATH_HANDLERS = {
    # Search filters
    SearchExperiments: filters.search_experiments,
    SearchRuns: filters.search_runs,
    SearchRegisteredModels: filters.search_registered_models,
    SearchModelVersions: filters.search_models_versions,
    # Creation initializers
    CreateExperiment: initializers.set_experiment_project_tag,
    CreateRegisteredModel: initializers.set_registered_model_project_tag,
}


def _get_after_request_handler(request_class: Any) -> Callable[[Response], None] | None:
    return AFTER_REQUEST_PATH_HANDLERS.get(request_class)


AFTER_REQUEST_HANDLERS = {
    (http_path, method): handler
    for http_path, handler, methods in get_endpoints(_get_after_request_handler)
    for method in methods
}


@catch_mlflow_exception
def after_request_hook(resp: Response) -> Response:
    """Execute handler (if exists) after mlflow response."""
    if is_error(resp.status_code):
        return resp
    if handler := AFTER_REQUEST_HANDLERS.get((request.path, request.method)):
        handler(resp)
    elif MAIN_JS_FILE_PATH.search(request.path):
        patch.alter_main_js(resp)
    return resp
