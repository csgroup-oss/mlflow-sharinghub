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

"""Auth client module.

Expose the authlib app client.
"""

from authlib.integrations.flask_client import OAuth

from mlflow_sharinghub.config import AppConfig

_MANDATORY_KEYS = ["client_id", "client_secret", "server_metadata_url"]


def _init_oauth() -> OAuth:
    oauth = OAuth()

    gitlab_openid_url = (
        (f"{AppConfig.GITLAB_URL.removesuffix('/')}/.well-known/openid-configuration")
        if AppConfig.GITLAB_URL
        else None
    )
    gitlab_oauth_conf = {
        "client_id": AppConfig.GITLAB_OAUTH_CLIENT_ID,
        "client_secret": AppConfig.GITLAB_OAUTH_CLIENT_SECRET,
        "server_metadata_url": gitlab_openid_url,
    }
    gitlab_oauth_conf = {k: v for k, v in gitlab_oauth_conf.items() if v}
    if all(k in gitlab_oauth_conf for k in _MANDATORY_KEYS):
        oauth.register(
            name="gitlab",
            client_kwargs={
                "scope": "openid email read_user profile api",
                "timeout": 10.0,
            },
            **gitlab_oauth_conf,
        )
    else:
        msg = "GitLab authentication not configured"
        raise ValueError(msg)
    return oauth


oauth = _init_oauth()
