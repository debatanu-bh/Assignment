import pytest
from typing import Dict, Any
from settings import config


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "real: mark test as requiring real device/cloud"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_addoption(parser):
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
    if not config.getoption("--real"):
        skip_real = pytest.mark.skip(reason="Need --real option to run")
        for item in items:
            if "real" in item.keywords:
                item.add_marker(skip_real)


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    return {
        "cloud_url": config.CLOUD_BASE_URL,
        "device_url": config.DEVICE_BASE_URL,
        "username": config.USERNAME,
        "timeout": config.REQUEST_TIMEOUT,
    }


@pytest.fixture(scope="session")
def device_service_real(request):
    from services.device_service import DeviceService

    device_ip = request.config.getoption("--device-ip")
    if device_ip:
        config.DEVICE_BASE_URL = f"http://{device_ip}"

    service = DeviceService()
    return service