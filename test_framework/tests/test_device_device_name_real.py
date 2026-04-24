"""
REAL Integration Tests — Device API: Get Device Name

These tests make ACTUAL HTTP calls to the device and cloud service.
They are skipped by default and only run with:

    pytest tests/ --real -v

Prerequisites:
    - .env must contain valid credentials and URLs
    - Cloud service must be deployed and reachable
    - Device must be on the network and reachable
"""

import pytest
from services.device_service import DeviceService
from services.auth_service import AuthService


@pytest.mark.real
class TestDeviceDeviceNameReal:
    """Real integration tests for device Get Device Name"""

    @pytest.fixture(autouse=True)
    def setup(self, device_service_real):
        """Use the real (un-mocked) device service"""
        self.device_service = device_service_real
        AuthService._cloud_token = None
        AuthService._device_token = None

    # TC_REAL_DEVICE_01: Read current device name
    def test_get_device_name(self):
        """
        Authenticate with the device and read its current name.
        Must return a non-empty string.
        """
        device_name = self.device_service.get_device_name_from_device()

        assert device_name is not None
        assert isinstance(device_name, str)
        assert len(device_name) > 0

    # TC_REAL_DEVICE_02: Name matches after cloud set
    def test_device_name_matches_cloud_set(self):
        """
        Set a name via cloud, then confirm the device local API
        returns the same name.
        """
        expected = "Real Test Device"

        self.device_service.change_device_name_via_cloud(expected)
        actual = self.device_service.get_device_name_from_device()

        assert actual == expected

    # TC_REAL_DEVICE_03: Concurrent reads are consistent
    def test_concurrent_reads_consistent(self):
        """
        Multiple concurrent GET requests to the device should all
        return the same name.
        """
        from concurrent.futures import ThreadPoolExecutor

        # Set a known name first
        expected = "Concurrent Real Test"
        self.device_service.change_device_name_via_cloud(expected)

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self.device_service.get_device_name_from_device)
                for _ in range(5)
            ]
            results = [f.result() for f in futures]

        assert all(name == expected for name in results)
