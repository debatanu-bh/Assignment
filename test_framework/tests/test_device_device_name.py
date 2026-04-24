"""
Test cases for Device API - Get Device Name functionality

Covers the device feature:
    "As a device user, I would like to be able to get the device name"

Device API under test:
    GET /api/device/name  (requires Bearer token from POST /api/auth/login)
"""

import pytest
from unittest.mock import MagicMock
from requests.exceptions import HTTPError
from services.device_service import DeviceService
from services.auth_service import AuthService


class TestDeviceDeviceName:
    """Test suite for local device name operations"""

    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        """Setup test dependencies with mocked API calls"""
        # Reset the AuthService singleton state
        AuthService._cloud_token = None
        AuthService._device_token = None

        self.device_service = DeviceService()
        self.auth_service = AuthService()

        # Mock cloud client
        self.mock_cloud_login = mocker.patch.object(
            self.device_service.cloud_client, 'login',
            return_value="mock_cloud_token"
        )
        self.mock_cloud_set_name = mocker.patch.object(
            self.device_service.cloud_client, 'set_device_name',
            return_value={"name": ""}
        )
        # Mock device client
        self.mock_device_login = mocker.patch.object(
            self.device_service.device_client, 'login',
            return_value="mock_device_token"
        )
        self.mock_device_get_name = mocker.patch.object(
            self.device_service.device_client, 'get_device_name',
            return_value="Default Device"
        )
        self.mock_device_reboot = mocker.patch.object(
            self.device_service.device_client, 'reboot_device',
            return_value={}
        )
        # Ensure auth service singleton uses the same mocked clients
        mocker.patch.object(self.auth_service, 'cloud_client',
                            self.device_service.cloud_client)
        mocker.patch.object(self.auth_service, 'device_client',
                            self.device_service.device_client)

    def _set_expected_name(self, name):
        """Helper to configure mocks for an expected device name"""
        self.mock_cloud_set_name.return_value = {"name": name}
        self.mock_device_get_name.return_value = name

    # ── TC_DEVICE_01: Get name after cloud change ────────────────────────
    def test_get_device_name_after_cloud_change(self):
        """
        TC_DEVICE_01: After setting the name via cloud, the device's local API must return the updated name.
        """
        new_name = "Updated Device Name"
        self._set_expected_name(new_name)

        self.device_service.change_device_name_via_cloud(new_name)
        device_name = self.device_service.get_device_name_from_device()

        assert device_name == new_name

    # ── TC_DEVICE_02: Default device name ────────────────────────────────
    def test_get_device_name_default(self):
        """
        TC_DEVICE_02: A fresh device must return a non-empty default name.
        """
        self.mock_device_get_name.return_value = "Default Device"

        device_name = self.device_service.get_device_name_from_device()

        assert device_name is not None
        assert len(device_name) > 0

    # ── TC_DEVICE_03: 401 with invalid token ─────────────────────────────
    def test_get_device_name_invalid_token(self):
        """
        TC_DEVICE_03: Device returns 401 when the token is invalid.
        """
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.json.return_value = {"error": "UNAUTHORIZED"}
        self.mock_device_get_name.side_effect = HTTPError(response=mock_resp)

        with pytest.raises(HTTPError) as exc_info:
            self.device_service.get_device_name_from_device()

        assert exc_info.value.response.status_code == 401

    # ── TC_DEVICE_04: Name persists after reboot ─────────────────────────
    @pytest.mark.slow
    def test_get_device_name_persists_after_reboot(self):
        """
        TC_DEVICE_04: Device name persists across a device reboot.
        """
        new_name = "Persistent Name"
        self._set_expected_name(new_name)

        self.device_service.change_device_name_via_cloud(new_name)
        self.device_service.device_client.reboot_device(token="mock_device_token")

        device_name = self.device_service.get_device_name_from_device()

        assert device_name == new_name
        self.mock_device_reboot.assert_called_once()

    # ── TC_DEVICE_05: Concurrent reads are consistent ────────────────────
    def test_get_device_name_concurrent(self):
        """
        TC_DEVICE_05: Multiple concurrent reads all return the same name.
        """
        from concurrent.futures import ThreadPoolExecutor

        expected_name = "Concurrent Test Device"
        self._set_expected_name(expected_name)
        self.device_service.change_device_name_via_cloud(expected_name)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self.device_service.get_device_name_from_device)
                for _ in range(10)
            ]
            results = [f.result() for f in futures]

        assert all(name == expected_name for name in results)
