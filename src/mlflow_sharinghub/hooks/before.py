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

"""Before request hooks handlers."""

from collections.abc import Callable
from typing import Any

from flask import Response, request
from mlflow.protos.model_registry_pb2 import (
    CreateModelVersion,
    CreateRegisteredModel,
    DeleteModelVersion,
    DeleteModelVersionTag,
    DeleteRegisteredModel,
    DeleteRegisteredModelAlias,
    DeleteRegisteredModelTag,
    GetLatestVersions,
    GetModelVersion,
    GetModelVersionByAlias,
    GetModelVersionDownloadUri,
    GetRegisteredModel,
    RenameRegisteredModel,
    SetModelVersionTag,
    SetRegisteredModelAlias,
    SetRegisteredModelTag,
    TransitionModelVersionStage,
    UpdateModelVersion,
    UpdateRegisteredModel,
)
from mlflow.protos.service_pb2 import (
    CreateExperiment,
    CreateRun,
    DeleteExperiment,
    DeleteRun,
    DeleteTag,
    GetExperiment,
    GetExperimentByName,
    GetMetricHistory,
    GetMetricHistoryBulkInterval,
    GetRun,
    ListArtifacts,
    LogBatch,
    LogInputs,
    LogMetric,
    LogModel,
    LogParam,
    RestoreExperiment,
    RestoreRun,
    SetExperimentTag,
    SetTag,
    UpdateExperiment,
    UpdateRun,
)
from mlflow.server.handlers import catch_mlflow_exception, get_endpoints

from mlflow_sharinghub._internal.server import (
    is_proxy_artifact_path,
    is_unprotected_route,
)
from mlflow_sharinghub.auth.api import get_request_token, make_unauthorized_response
from mlflow_sharinghub.utils.http import make_forbidden_response

from .handlers import validators

BEFORE_REQUEST_HANDLERS = {
    # Routes for experiments
    CreateExperiment: validators.can_create_for_project,
    GetExperiment: validators.can_read_experiment,
    GetExperimentByName: validators.can_read_experiment_by_name,
    DeleteExperiment: validators.can_delete_experiment,
    RestoreExperiment: validators.can_delete_experiment,
    UpdateExperiment: validators.can_update_experiment,
    SetExperimentTag: validators.can_update_experiment_tag,
    # Routes for runs
    CreateRun: validators.can_update_experiment,
    GetRun: validators.can_read_run,
    DeleteRun: validators.can_delete_run,
    RestoreRun: validators.can_delete_run,
    UpdateRun: validators.can_update_run,
    LogMetric: validators.can_update_run,
    LogBatch: validators.can_update_run,
    LogModel: validators.can_update_run,
    LogInputs: validators.can_update_run,
    SetTag: validators.can_update_run,
    DeleteTag: validators.can_update_run,
    LogParam: validators.can_update_run,
    GetMetricHistory: validators.can_read_run,
    GetMetricHistoryBulkInterval: validators.can_read_run,
    ListArtifacts: validators.can_read_run,
    # Routes for model registry
    GetRegisteredModel: validators.can_read_registered_model,
    DeleteRegisteredModel: validators.can_delete_registered_model,
    UpdateRegisteredModel: validators.can_update_registered_model,
    RenameRegisteredModel: validators.can_update_registered_model,
    GetLatestVersions: validators.can_read_registered_model,
    CreateModelVersion: validators.can_update_registered_model,
    CreateRegisteredModel: validators.can_create_for_project,
    GetModelVersion: validators.can_read_registered_model,
    DeleteModelVersion: validators.can_delete_registered_model,
    UpdateModelVersion: validators.can_update_registered_model,
    TransitionModelVersionStage: validators.can_update_registered_model,
    GetModelVersionDownloadUri: validators.can_read_registered_model,
    SetRegisteredModelTag: validators.can_update_registered_model_tag,
    DeleteRegisteredModelTag: validators.can_update_registered_model_tag,
    SetModelVersionTag: validators.can_update_registered_model,
    DeleteModelVersionTag: validators.can_delete_registered_model,
    SetRegisteredModelAlias: validators.can_update_registered_model,
    DeleteRegisteredModelAlias: validators.can_delete_registered_model,
    GetModelVersionByAlias: validators.can_read_registered_model,
}


def _get_before_request_handler(request_class: Any) -> Callable[[], bool] | None:
    return BEFORE_REQUEST_HANDLERS.get(request_class)


BEFORE_REQUEST_VALIDATORS = {
    (http_path, method): handler
    for http_path, handler, methods in get_endpoints(_get_before_request_handler)
    for method in methods
}


def _get_proxy_artifact_validator(
    method: str, view_args: dict[str, Any] | None
) -> Callable[[], bool] | None:
    if view_args is None:
        return validators.can_read_experiment_artifact_proxy  # List

    return {
        "GET": validators.can_read_experiment_artifact_proxy,  # Download
        "PUT": validators.can_update_experiment_artifact_proxy,  # Upload
        "DELETE": validators.can_delete_experiment_artifact_proxy,  # Delete
    }.get(method)


@catch_mlflow_exception
def before_request_hook() -> Response | None:
    """Execute handler (if exists) before mlflow processing of the request."""
    if is_unprotected_route(request.path):
        return None

    if not get_request_token():
        return make_unauthorized_response()

    if validator := BEFORE_REQUEST_VALIDATORS.get((request.path, request.method)):
        if not validator():
            return make_forbidden_response()
    elif is_proxy_artifact_path(request.path):
        validator = _get_proxy_artifact_validator(request.method, request.view_args)
        if validator and not validator():
            return make_forbidden_response()

    return None
