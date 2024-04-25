"""Session module (utils).

Utilities related to Flask session.
"""

from datetime import UTC, datetime
from typing import cast

from flask import session


class TimedSessionStore[K, V]:
    """TimedSessionStore stores data in session with expiration timeout."""

    def __init__(self, name: str, timeout: float) -> None:
        """TimedSessionStore constructor.

        Args:
            name: Name of the session first-level key. If name="example",
                  the store will be a dict located in session["example"].
            timeout: lifespan for the stored values.
        """
        self._name = name
        self._timeout = timeout

    def _get_store(self) -> dict[K, V | None]:
        return session.setdefault(self._name, {})

    def get(self, key: K, default: V | None = None) -> V | None:
        """Get key from session store, return default if not found."""
        store = self._get_store()
        val = cast(tuple[float, V | None] | None, store.get(key, default))
        if val:
            dt, val = val
            if datetime.now(tz=UTC).timestamp() - dt < self._timeout:
                return val
            store.pop(key)
        return default

    def set(self, key: K, val: V | None) -> None:
        """Set val for key in session store."""
        store = self._get_store()
        store[key] = (datetime.now(tz=UTC).timestamp(), val)

    def refresh(self, key: K) -> None:
        """Refresh key timestamp in session if present."""
        store = self._get_store()
        val = cast(tuple[float, V | None] | None, store.get(key))
        if val:
            _, val = val
            self.set(key, val)
