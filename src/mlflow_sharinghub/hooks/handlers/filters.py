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

"""Filters module."""

from collections.abc import Callable
from typing import Any

from flask import Response
from mlflow.entities import Experiment, Run
from mlflow.entities.model_registry import ModelVersion, RegisteredModel
from mlflow.protos.model_registry_pb2 import SearchModelVersions, SearchRegisteredModels
from mlflow.protos.service_pb2 import SearchExperiments, SearchRuns
from mlflow.server.handlers import _get_request_message
from mlflow.store.entities import PagedList
from mlflow.utils.proto_json_utils import message_to_json, parse_dict
from mlflow.utils.search_utils import SearchUtils

from mlflow_sharinghub._internal.store import (
    get_experiment_by_name,
    get_model_registry_store,
    get_tracking_store,
)

from . import validators


def _filter_entities(
    resp: Response,
    search_view: Any,
    search_entities_attr: str,
    search_refetch: Callable[[Any, Any], PagedList[Any]],
    validate: Callable[[Any], bool],
) -> None:
    response_message = search_view.Response()
    parse_dict(resp.json, response_message)

    resp_entities = getattr(response_message, search_entities_attr)

    # filter out unreadable
    for e in list(resp_entities):
        if not validate(e):
            resp_entities.remove(e)

    request_message = _get_request_message(search_view())
    while (
        len(resp_entities) < request_message.max_results
        and response_message.next_page_token != ""
    ):
        refetched = search_refetch(request_message, response_message)
        refetched = refetched[: request_message.max_results - len(resp_entities)]
        if len(refetched) == 0:
            response_message.next_page_token = ""
            break

        refetched_readable_proto = [e.to_proto() for e in refetched if validate(e.name)]
        resp_entities.extend(refetched_readable_proto)

        # recalculate next page token
        start_offset = SearchUtils.parse_start_offset_from_page_token(
            response_message.next_page_token
        )
        final_offset = start_offset + len(refetched)
        response_message.next_page_token = SearchUtils.create_page_token(final_offset)

    resp.data = message_to_json(response_message)


def _search_refetch_experiments(req_msg: Any, resp_msg: Any) -> PagedList[Experiment]:
    return get_tracking_store().search_experiments(
        view_type=req_msg.view_type,
        max_results=req_msg.max_results,
        order_by=req_msg.order_by,
        filter_string=req_msg.filter,
        page_token=resp_msg.next_page_token,
    )


def _validate_experiment(experiment: Any) -> bool:
    return validators.get_permission_for_experiment(
        get_experiment_by_name(experiment.name)
    ).can_read


def search_experiments(resp: Response) -> None:
    """Patch SearchExperiments view."""
    _filter_entities(
        resp=resp,
        search_view=SearchExperiments,
        search_entities_attr="experiments",
        search_refetch=_search_refetch_experiments,
        validate=_validate_experiment,
    )


def _search_refetch_runs(req_msg: Any, resp_msg: Any) -> PagedList[Run]:
    return get_tracking_store().search_runs(
        experiment_ids=req_msg.experiment_ids,
        filter_string=req_msg.filter,
        run_view_type=req_msg.run_view_type,
        max_results=req_msg.max_results,
        order_by=req_msg.order_by,
        page_token=resp_msg.next_page_token,
    )


def _validate_run(run: Any) -> bool:
    return validators.get_permission_for_experiment(
        get_tracking_store().get_experiment(run.info.experiment_id)
    ).can_read


def search_runs(resp: Response) -> None:
    """Patch SearchRuns view."""
    _filter_entities(
        resp=resp,
        search_view=SearchRuns,
        search_entities_attr="runs",
        search_refetch=_search_refetch_runs,
        validate=_validate_run,
    )


def _search_refetch_registered_models(
    req_msg: Any, resp_msg: Any
) -> PagedList[RegisteredModel]:
    return get_model_registry_store().search_registered_models(
        filter_string=req_msg.filter,
        max_results=req_msg.max_results,
        order_by=req_msg.order_by,
        page_token=resp_msg.next_page_token,
    )


def _validate_registered_model(registered_model: Any) -> bool:
    return validators.get_permission_for_registered_model(
        get_model_registry_store().get_registered_model(registered_model.name)
    ).can_read


def search_registered_models(resp: Response) -> None:
    """Patch SearchRegisteredModels view."""
    _filter_entities(
        resp=resp,
        search_view=SearchRegisteredModels,
        search_entities_attr="registered_models",
        search_refetch=_search_refetch_registered_models,
        validate=_validate_registered_model,
    )


def _search_refetch_models_versions(
    req_msg: Any, resp_msg: Any
) -> PagedList[ModelVersion]:
    return get_model_registry_store().search_model_versions(
        filter_string=req_msg.filter,
        max_results=req_msg.max_results,
        order_by=req_msg.order_by,
        page_token=resp_msg.next_page_token,
    )


def _validate_model_version(model_version: Any) -> bool:
    _tracking_store = get_tracking_store()
    _model_registry_store = get_model_registry_store()
    return validators.get_permission_for_experiment(
        _tracking_store.get_experiment(
            _tracking_store.get_run(
                _model_registry_store.get_model_version(
                    model_version.name, model_version.version
                ).run_id
            ).info.experiment_id
        )
    ).can_read


def search_models_versions(resp: Response) -> None:
    """Patch SearchModelVersions view."""
    _filter_entities(
        resp=resp,
        search_view=SearchModelVersions,
        search_entities_attr="model_versions",
        search_refetch=_search_refetch_models_versions,
        validate=_validate_model_version,
    )
