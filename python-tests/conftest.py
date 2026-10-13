"""Session-wide JVM fixture for the Snake concurrency lab."""

from __future__ import annotations

import pytest

from helpers.jvm import ensure_jvm, project_root


@pytest.fixture(scope="session")
def jvm():
    try:
        return ensure_jvm()
    except Exception as exc:
        pytest.exit(f"JVM fixture failed: {exc}", returncode=3)


@pytest.fixture
def concurrency(jvm):
    from helpers import concurrency as helpers

    return helpers


@pytest.fixture
def project_dir():
    return project_root()
