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

"""Initializers module."""

from flask import Response, request
from mlflow.entities import ExperimentTag
from mlflow.entities.model_registry import RegisteredModelTag
from mlflow.protos.model_registry_pb2 import CreateRegisteredModel
from mlflow.protos.service_pb2 import CreateExperiment
from mlflow.utils.proto_json_utils import parse_dict

from mlflow_sharinghub._internal.server import get_project_path
from mlflow_sharinghub._internal.store import (
    get_model_registry_store,
    get_tracking_store,
)
from mlflow_sharinghub.config import AppConfig


def set_experiment_project_tag(resp: Response) -> None:
    """Set the experiment project tag after CreateExperiment."""
    response_message = CreateExperiment.Response()
    parse_dict(resp.json, response_message)
    experiment_id = response_message.experiment_id
    project_path = get_project_path()

    tag = ExperimentTag(AppConfig.PROJECT_TAG, project_path)
    get_tracking_store().set_experiment_tag(experiment_id, tag)


def set_registered_model_project_tag(resp: Response) -> None:
    """Set the registered model project tag after CreateRegisteredModel."""
    response_message = CreateRegisteredModel.Response()
    parse_dict(resp.json, response_message)
    name = (
        response_message.registered_model.name
        if response_message.registered_model.name
        else request.json["name"]
    )
    project_path = get_project_path()

    tag = RegisteredModelTag(AppConfig.PROJECT_TAG, project_path)
    get_model_registry_store().set_registered_model_tag(name, tag)
