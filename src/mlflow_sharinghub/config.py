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

"""Config module."""

import os
import secrets

from cachelib import FileSystemCache
from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    """Flask app config object."""

    # Flask conf
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(16))
    SESSION_COOKIE_NAME = "mlflow-session"
    PERMANENT_SESSION_LIFETIME = int(os.getenv("PERMANENT_SESSION_LIFETIME", "7200"))
    SESSION_TYPE = "cachelib"
    SESSION_SERIALIZATION_FORMAT = "json"
    SESSION_CACHELIB = FileSystemCache(threshold=500, cache_dir="_sessions")
    # Project conf
    PROJECT_CACHE_TIMEOUT = float(os.getenv("PROJECT_CACHE_TIMEOUT", "300"))
    PROJECT_TAG = os.getenv("PROJECT_TAG", "project")
    # Auth conf
    LOGIN_AUTO_REDIRECT = os.getenv("LOGIN_AUTO_REDIRECT", "false").lower().strip() in [
        "1",
        "true",
    ]
    # SharingHub conf
    SHARINGHUB_URL = os.getenv("SHARINGHUB_URL", None)
    SHARINGHUB_SESSION_COOKIE = os.getenv(
        "SHARINGHUB_SESSION_COOKIE", "sharinghub-session"
    )
    SHARINGHUB_AUTH_DEFAULT_TOKEN = os.getenv(
        "SHARINGHUB_AUTH_DEFAULT_TOKEN", "false"
    ).lower().strip() in [
        "1",
        "true",
    ]
    SHARINGHUB_AUTH_CACHE_TIMEOUT = float(
        os.getenv("SHARINGHUB_AUTH_CACHE_TIMEOUT", "60")
    )
    SHARINGHUB_STAC_COLLECTION = os.getenv("SHARINGHUB_STAC_COLLECTION", "ai-model")
    # GitLab conf
    GITLAB_URL = os.getenv("GITLAB_URL", None)
    GITLAB_OAUTH_CLIENT_ID = os.getenv("GITLAB_OAUTH_CLIENT_ID", "")
    GITLAB_OAUTH_CLIENT_SECRET = os.getenv("GITLAB_OAUTH_CLIENT_SECRET", "")
    GITLAB_MANDATORY_TOPICS = tuple(
        t for t in os.getenv("GITLAB_MANDATORY_TOPICS", "").strip().split(",") if t
    )
