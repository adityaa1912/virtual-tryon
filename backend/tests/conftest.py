import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

_STORAGE_ROOT = Path(tempfile.mkdtemp(prefix="vt-tests-"))
os.environ["STORAGE_DIR"] = str(_STORAGE_ROOT)


@pytest.fixture(scope="session")
def storage_root() -> Path:
    return _STORAGE_ROOT


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    from app.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client
