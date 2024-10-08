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

"""Internal store module (private).

Utilities to interact with mlflow stores.
"""

from typing import cast

from mlflow import MlflowException
from mlflow.entities import Experiment
from mlflow.protos.databricks_pb2 import RESOURCE_DOES_NOT_EXIST
from mlflow.server.handlers import _get_model_registry_store, _get_tracking_store
from mlflow.store.model_registry.abstract_store import (
    AbstractStore as AbstractModelRegistryStore,
)
from mlflow.store.tracking.abstract_store import AbstractStore as AbstractTrackingStore

_tracking_store = cast(AbstractTrackingStore, _get_tracking_store())
_model_registry_store = cast(AbstractModelRegistryStore, _get_model_registry_store())


def get_tracking_store() -> AbstractTrackingStore:
    """Return mlflow tracking store."""
    return _tracking_store


def get_model_registry_store() -> AbstractModelRegistryStore:
    """Return mlflow model registry store."""
    return _model_registry_store


def get_experiment_by_name(name: str) -> Experiment:
    """Get experiment by name, throw error if not found.

    Raises:
        mlflow.MlflowException: If experiment was not found.
    """
    experiment = _tracking_store.get_experiment_by_name(name)
    if experiment is None:
        msg = f"Could not find experiment with name {name}"
        raise MlflowException(msg, error_code=RESOURCE_DOES_NOT_EXIST)
    return experiment
