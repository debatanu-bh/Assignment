import pytest
from typing import Dict, Any
from settings import config


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "real: mark test as requiring real device/cloud"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--real",
        action="store_true",
        default=False,
        help="Run real device/cloud tests (requires actual hardware)"
    )
    parser.addoption(
        "--device-ip",
        action="store",
        default=None,
        help="Override device IP address (e.g. --device-ip=192.168.0.50)"
    )


def pytest_collection_modifyitems(config, items):
    """Skip real tests unless --real flag is provided"""
    if not config.getoption("--real"):
        skip_real = pytest.mark.skip(reason="Need --real option to run")
        for item in items:
            if "real" in item.keywords:
                item.add_marker(skip_real)


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Provide test configuration to tests"""
    return {
        "cloud_url": config.CLOUD_BASE_URL,
        "device_url": config.DEVICE_BASE_URL,
        "username": config.USERNAME,
        "timeout": config.REQUEST_TIMEOUT,
    }


@pytest.fixture(scope="session")
def device_service_real(request):
    """
    Provide a real (un-mocked) DeviceService for integration tests.
    Supports --device-ip override from the command line.
    """
    from services.device_service import DeviceService

    # Override device IP if provided via CLI
    device_ip = request.config.getoption("--device-ip")
    if device_ip:
        config.DEVICE_BASE_URL = f"http://{device_ip}"

    service = DeviceService()
    return service