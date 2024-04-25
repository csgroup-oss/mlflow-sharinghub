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
    SESSION_TYPE = "cachelib"
    SESSION_SERIALIZATION_FORMAT = "json"
    SESSION_CACHELIB = FileSystemCache(threshold=500, cache_dir="_sessions")
    # Extras conf
    CACHE_TIMEOUT = float(os.getenv("CACHE_TIMEOUT", "300"))
    PROJECT_TAG = os.getenv("PROJECT_TAG", "project")
    LOGIN_AUTO_REDIRECT = os.getenv("LOGIN_AUTO_REDIRECT", "false").lower().strip() in [
        "1",
        "true",
    ]
    GITLAB_URL = os.getenv("GITLAB_URL", "https://gitlab.com")
    GITLAB_OAUTH_CLIENT_ID = os.getenv("GITLAB_OAUTH_CLIENT_ID", "")
    GITLAB_OAUTH_CLIENT_SECRET = os.getenv("GITLAB_OAUTH_CLIENT_SECRET", "")
