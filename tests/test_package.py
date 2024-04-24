"""Basic package test."""


def test_package_import():
    """Import package."""
    import mlflow_sharinghub


def test_package_version_is_defined():
    """Check imported package have __version__ defined."""
    import mlflow_sharinghub

    assert mlflow_sharinghub.__version__ != "undefined"
