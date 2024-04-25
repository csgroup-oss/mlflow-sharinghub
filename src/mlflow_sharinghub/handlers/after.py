"""After request hooks handlers."""

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

from mlflow_sharinghub import filters, initializers
from mlflow_sharinghub.utils.http import is_error

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
    return resp
