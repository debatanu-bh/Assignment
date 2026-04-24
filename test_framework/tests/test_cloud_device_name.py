"""
Test cases for Cloud API - Set Device Name functionality

Covers the cloud feature:
    "As a cloud user, I would like to be able to change the device name"

Cloud API under test:
    POST /api/device/name  (requires Bearer token from POST /api/auth/login)
"""

import pytest
from unittest.mock import MagicMock
from requests.exceptions import HTTPError
from services.device_service import DeviceService
from services.auth_service import AuthService
from pydantic import ValidationError


class TestCloudDeviceName:
    """Test suite for cloud-based device name operations"""

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
            return_value=""
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

    # ── TC_CLOUD_01: Successful name change ──────────────────────────────
    def test_set_device_name_success(self):
        """
        TC_CLOUD_01: Set a valid device name via cloud and verify the device reports the new name.
        """
        new_name = "Living Room Camera"
        self._set_expected_name(new_name)

        response = self.device_service.change_device_name_via_cloud(new_name)

        assert response.name == new_name
        self.mock_cloud_set_name.assert_called_once()

        # End-to-end check: device should now report the new name
        assert self.device_service.verify_device_name_on_device(new_name)

    # ── TC_CLOUD_02: Empty name rejected ─────────────────────────────────
    def test_set_device_name_empty_string(self):
        """
        TC_CLOUD_02: An empty device name must be rejected by validation.
        """
        with pytest.raises(ValidationError) as exc_info:
            self.device_service.change_device_name_via_cloud("")

        error_text = str(exc_info.value)
        assert "at least 1 character" in error_text or \
               "Device name cannot be empty" in error_text

    # ── TC_CLOUD_03: Maximum length (100 chars) ─────────────────────────
    def test_set_device_name_max_min_length(self):
        """
        TC_CLOUD_03: A Max & Min character name is within the allowed limit.
        """
        long_name = "A" * 100
        short_name = "A" 
        self._set_expected_name(long_name)
        self._set_expected_name(short_name)

        response = self.device_service.change_device_name_via_cloud(long_name)
        response_short = self.device_service.change_device_name_via_cloud(short_name)
        assert response.name == long_name
        assert response_short.name == short_name

    # ── TC_CLOUD_04: Exceeding max length rejected ──────────────────────
    def test_set_device_name_exceeds_max_length(self):
        """
        TC_CLOUD_04: A 101-character name must be rejected by validation.
        """
        with pytest.raises(ValidationError):
            self.device_service.change_device_name_via_cloud("A" * 101)

    # ── TC_CLOUD_05: Special / Unicode characters ────────────────────────
    @pytest.mark.parametrize("special_name", [
        "Device@123",
        "My-Device_Name",
        "Camera #1",
        "Device (Living Room)",
        "温度センサー",
    ])
    def test_set_device_name_special_characters(self, special_name):
        """
        TC_CLOUD_05: Device name with special or unicode characters is accepted and returned correctly.
        """
        self._set_expected_name(special_name)

        response = self.device_service.change_device_name_via_cloud(special_name)
        assert response.name == special_name

    # ── TC_CLOUD_06: 401 Unauthorized ────────────────────────────────────
    def test_set_device_name_unauthorized(self):
        """
        TC_CLOUD_06: Cloud returns 401 when the token is invalid / expired.
        """
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.json.return_value = {"error": "UNAUTHORIZED"}
        self.mock_cloud_set_name.side_effect = HTTPError(response=mock_resp)

        with pytest.raises(HTTPError) as exc_info:
            self.device_service.change_device_name_via_cloud("Test Name")

        assert exc_info.value.response.status_code == 401

    # ── TC_CLOUD_07: Whitespace-only name rejected ──────────────────────
    def test_set_device_name_whitespace_only(self):
        """
        TC_CLOUD_07: A name consisting only of spaces must be rejected.
        """
        with pytest.raises(ValidationError) as exc_info:
            self.device_service.change_device_name_via_cloud("   ")

        assert "Device name cannot be empty" in str(exc_info.value)
