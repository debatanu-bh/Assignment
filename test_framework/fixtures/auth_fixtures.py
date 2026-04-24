import pytest
from services.auth_service import AuthService

@pytest.fixture(scope="session")
def cloud_token():
    auth_service = AuthService()
    token = auth_service.get_cloud_token()
    yield token
    auth_service.clear_tokens()


@pytest.fixture(scope="session")
def device_token():
    auth_service = AuthService()
    token = auth_service.get_device_token()
    yield token


@pytest.fixture
def auth_service():
    return AuthService()


@pytest.fixture(autouse=True)
def reset_tokens_between_tests():
    auth_service = AuthService()
    auth_service.clear_tokens()
    yield
    auth_service.clear_tokens()