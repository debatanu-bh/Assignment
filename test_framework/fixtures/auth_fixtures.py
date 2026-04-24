import pytest
from services.auth_service import AuthService


@pytest.fixture(scope="session")
def cloud_token():
    """Fixture providing cloud authentication token"""
    auth_service = AuthService()
    token = auth_service.get_cloud_token()
    yield token
    # Cleanup after tests
    auth_service.clear_tokens()


@pytest.fixture(scope="session")
def device_token():
    """Fixture providing device authentication token"""
    auth_service = AuthService()
    token = auth_service.get_device_token()
    yield token


@pytest.fixture
def auth_service():
    """Fixture providing auth service instance"""
    return AuthService()


@pytest.fixture(autouse=True)
def reset_tokens_between_tests():
    """Reset tokens between tests to ensure isolation"""
    auth_service = AuthService()
    auth_service.clear_tokens()
    yield
    auth_service.clear_tokens()