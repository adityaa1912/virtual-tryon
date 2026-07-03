import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

_STORAGE_ROOT = Path(tempfile.mkdtemp(prefix="vt-tests-"))
os.environ["STORAGE_DIR"] = str(_STORAGE_ROOT)


@pytest.fixture(scope="session")
def storage_root() -> Path:
    return _STORAGE_ROOT


@pytest.fixture(scope="session")
def client() -> Iterator["object"]:
    from fastapi.testclient import TestClient

    from app.api.dependencies import get_gemini_provider, get_video_provider
    from app.main import create_app
    from app.services.gemini_provider import FakeGeminiProvider
    from app.services.video_provider import FakeVideoProvider

    application = create_app()
    application.dependency_overrides[get_gemini_provider] = lambda: FakeGeminiProvider()
    application.dependency_overrides[get_video_provider] = lambda: FakeVideoProvider()

    with TestClient(application) as test_client:
        yield test_client
