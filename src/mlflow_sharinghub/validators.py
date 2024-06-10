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

"""Validators module."""

import re

from flask import request
from mlflow.entities import Experiment, Run
from mlflow.entities.model_registry import RegisteredModel

from mlflow_sharinghub._internal.server import get_project_path, get_request_param
from mlflow_sharinghub._internal.store import (
    get_experiment_by_name,
    get_model_registry_store,
    get_tracking_store,
)
from mlflow_sharinghub.auth import get_request_token
from mlflow_sharinghub.config import AppConfig
from mlflow_sharinghub.permissions import (
    get_permission_for_experiment,
    get_permission_for_project,
    get_permission_for_registered_model,
    session_save_access_level,
)
from mlflow_sharinghub.utils.gitlab import GitlabClient

_PROJECT_SUFFIX_PATTERN = re.compile(r"\s+\(.+\)$")
_EXPERIMENT_ID_PATTERN = re.compile(r"^(\d+)/")


def _get_experiment_from_experiment_id_request_param() -> Experiment:
    experiment_id = get_request_param("experiment_id")
    return get_tracking_store().get_experiment(experiment_id)


def _get_run_from_run_id_request_param() -> Run:
    run_id = get_request_param("run_id")
    return get_tracking_store().get_run(run_id)


def _get_registered_model_from_registered_model_name_request_param() -> RegisteredModel:
    registered_model_name = get_request_param("name")
    return get_model_registry_store().get_registered_model(registered_model_name)


def _can_change_name(new_name: str, old_name: str) -> bool:
    _m = _PROJECT_SUFFIX_PATTERN.search(new_name)
    new_name_suffix = _m.group().strip() if _m else None
    _m = _PROJECT_SUFFIX_PATTERN.search(old_name)
    old_name_suffix = _m.group().strip() if _m else None
    return new_name_suffix and new_name_suffix == old_name_suffix


def _get_experiment_from_experiment_id_artifact_proxy() -> Experiment | None:
    if experiment_id := _get_experiment_id_from_view_args():
        experiment = get_tracking_store().get_experiment(experiment_id)
        return experiment
    return None


def _get_experiment_id_from_view_args() -> str | None:
    if artifact_path := request.view_args.get("artifact_path"):  # noqa: SIM102
        if m := _EXPERIMENT_ID_PATTERN.match(artifact_path):
            return m.group(1)
    return None


def can_create_for_project() -> bool:
    """Assert if user have create permission for current project."""
    project_path = get_project_path()
    if not project_path:
        return False

    gitlab_client = GitlabClient(url=AppConfig.GITLAB_URL, token=get_request_token())
    project = gitlab_client.get_project(project_path)
    if not project:
        return False

    # Will prevent sending a second request in _get_permission_for_project
    session_save_access_level(project)

    suffix = f"({project['id']})"
    if _m := _PROJECT_SUFFIX_PATTERN.search(request.json["name"]):
        if _m.group().strip() != suffix:
            # Experiment name was given a suffix not corresponding to the project
            return False
    else:
        # Suffix is mandatory
        return False

    return get_permission_for_project(project_path).can_create


def can_read_experiment() -> bool:
    """Assert if user have read permission for experiment."""
    experiment = _get_experiment_from_experiment_id_request_param()
    return get_permission_for_experiment(experiment).can_read


def can_read_experiment_by_name() -> bool:
    """Assert if user have read permission for experiment by name."""
    experiment_name = get_request_param("experiment_name")
    experiment = get_experiment_by_name(experiment_name)
    return get_permission_for_experiment(experiment).can_read


def can_update_experiment() -> bool:
    """Assert if user have update permission for experiment."""
    experiment = _get_experiment_from_experiment_id_request_param()
    if new_name := request.json.get("new_name"):  # noqa: SIM102
        if not _can_change_name(new_name, experiment.name):
            return False
    return get_permission_for_experiment(experiment).can_update


def can_update_experiment_tag() -> bool:
    """Assert if user have update permission for experiment tag."""
    experiment = _get_experiment_from_experiment_id_request_param()
    tag_key = request.get_json()["key"]
    return (
        tag_key != AppConfig.PROJECT_TAG
        and get_permission_for_experiment(experiment).can_update
    )


def can_delete_experiment() -> bool:
    """Assert if user have delete permission for experiment."""
    experiment = _get_experiment_from_experiment_id_request_param()
    return get_permission_for_experiment(experiment).can_delete


def can_read_experiment_artifact_proxy() -> bool:
    """Assert if user have read permission for experiment artifact proxy."""
    if experiment := _get_experiment_from_experiment_id_artifact_proxy():
        return get_permission_for_experiment(experiment).can_read
    return False


def can_update_experiment_artifact_proxy() -> bool:
    """Assert if user have update permission for experiment artifact proxy."""
    if experiment := _get_experiment_from_experiment_id_artifact_proxy():
        return get_permission_for_experiment(experiment).can_update
    return False


def can_delete_experiment_artifact_proxy() -> bool:
    """Assert if user have delete permission for experiment artifact proxy."""
    if experiment := _get_experiment_from_experiment_id_artifact_proxy():
        return get_permission_for_experiment(experiment).can_delete
    return False


def can_read_run() -> bool:
    """Assert if user have read permission for run (base on experiment)."""
    run = _get_run_from_run_id_request_param()
    experiment = get_tracking_store().get_experiment(run.info.experiment_id)
    return get_permission_for_experiment(experiment).can_read


def can_update_run() -> bool:
    """Assert if user have update permission for run (base on experiment)."""
    run = _get_run_from_run_id_request_param()
    experiment = get_tracking_store().get_experiment(run.info.experiment_id)
    return get_permission_for_experiment(experiment).can_update


def can_delete_run() -> bool:
    """Assert if user have delete permission for run (base on experiment)."""
    run = _get_run_from_run_id_request_param()
    experiment = get_tracking_store().get_experiment(run.info.experiment_id)
    return get_permission_for_experiment(experiment).can_delete


def can_read_registered_model() -> bool:
    """Assert if user have read permission for registered model."""
    registered_model = _get_registered_model_from_registered_model_name_request_param()
    return get_permission_for_registered_model(registered_model).can_read


def can_update_registered_model() -> bool:
    """Assert if user have update permission for registered model."""
    registered_model = _get_registered_model_from_registered_model_name_request_param()
    return get_permission_for_registered_model(registered_model).can_update


def can_update_registered_model_tag() -> bool:
    """Assert if user have update permission for registered model tag."""
    registered_model = _get_registered_model_from_registered_model_name_request_param()
    tag_key = request.get_json()["key"]
    return (
        tag_key != AppConfig.PROJECT_TAG
        and get_permission_for_registered_model(registered_model).can_update
    )


def can_delete_registered_model() -> bool:
    """Assert if user have delete permission for registered model."""
    registered_model = _get_registered_model_from_registered_model_name_request_param()
    return get_permission_for_registered_model(registered_model).can_delete
