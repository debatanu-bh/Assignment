"""
REAL Integration Tests — Cloud API: Set Device Name

These tests make ACTUAL HTTP calls to the cloud service and device.
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
class TestCloudDeviceNameReal:
    """Real integration tests for cloud Set Device Name"""

    @pytest.fixture(autouse=True)
    def setup(self, device_service_real):
        """Use the real (un-mocked) device service"""
        self.device_service = device_service_real
        # Reset cached tokens so each test class gets fresh auth
        AuthService._cloud_token = None
        AuthService._device_token = None

    # TC_REAL_CLOUD_01: Set name via cloud, verify on device
    def test_set_and_verify_device_name(self):
        """
        Set a device name via cloud API, then read it back from the
        device's local API to confirm end-to-end sync.
        """
        new_name = "Integration Test Camera"

        response = self.device_service.change_device_name_via_cloud(new_name)
        assert response.name == new_name

        # Read back from device
        assert self.device_service.verify_device_name_on_device(new_name)

    # TC_REAL_CLOUD_02: Update name twice
    def test_update_device_name_twice(self):
        """
        Change the device name twice in sequence; device should
        always reflect the latest value.
        """
        first_name = "First Name"
        second_name = "Second Name"

        self.device_service.change_device_name_via_cloud(first_name)
        self.device_service.change_device_name_via_cloud(second_name)

        device_name = self.device_service.get_device_name_from_device()
        assert device_name == second_name

    # TC_REAL_CLOUD_03: Special characters round-trip
    def test_special_characters_round_trip(self):
        """
        Set a name with special characters via cloud; device must
        return the exact same string.
        """
        special_name = "Camera #1 — 温度センサー"

        self.device_service.change_device_name_via_cloud(special_name)

        device_name = self.device_service.get_device_name_from_device()
        assert device_name == special_name
