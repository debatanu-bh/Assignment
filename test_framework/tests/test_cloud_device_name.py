import pytest
from unittest.mock import MagicMock
from requests.exceptions import HTTPError
from services.device_service import DeviceService
from services.auth_service import AuthService
from pydantic import ValidationError


class TestCloudDeviceName:

    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        AuthService._cloud_token = None
        AuthService._device_token = None

        self.device_service = DeviceService()
        self.auth_service = AuthService()

        self.mock_cloud_login = mocker.patch.object(
            self.device_service.cloud_client, 'login',
            return_value="mock_cloud_token"
        )
        self.mock_cloud_set_name = mocker.patch.object(
            self.device_service.cloud_client, 'set_device_name',
            return_value={"name": ""}
        )
        self.mock_device_login = mocker.patch.object(
            self.device_service.device_client, 'login',
            return_value="mock_device_token"
        )
        self.mock_device_get_name = mocker.patch.object(
            self.device_service.device_client, 'get_device_name',
            return_value=""
        )
        mocker.patch.object(self.auth_service, 'cloud_client',
                            self.device_service.cloud_client)
        mocker.patch.object(self.auth_service, 'device_client',
                            self.device_service.device_client)

    def _set_expected_name(self, name):
        self.mock_cloud_set_name.return_value = {"name": name}
        self.mock_device_get_name.return_value = name

    def test_set_device_name_success(self):
        new_name = "Living Room Camera"
        self._set_expected_name(new_name)

        response = self.device_service.change_device_name_via_cloud(new_name)

        assert response.name == new_name
        self.mock_cloud_set_name.assert_called_once()

        assert self.device_service.verify_device_name_on_device(new_name)

    def test_set_device_name_empty_string(self):
        with pytest.raises(ValidationError) as exc_info:
            self.device_service.change_device_name_via_cloud("")

        error_text = str(exc_info.value)
        assert "at least 1 character" in error_text or \
               "Device name cannot be empty" in error_text

    def test_set_device_name_max_min_length(self):
        long_name = "A" * 100
        short_name = "A" 
        self._set_expected_name(long_name)
        self._set_expected_name(short_name)

        response = self.device_service.change_device_name_via_cloud(long_name)
        response_short = self.device_service.change_device_name_via_cloud(short_name)
        assert response.name == long_name
        assert response_short.name == short_name

    def test_set_device_name_exceeds_max_length(self):
        with pytest.raises(ValidationError):
            self.device_service.change_device_name_via_cloud("A" * 101)

    @pytest.mark.parametrize("special_name", [
        "Device@123",
        "My-Device_Name",
        "Camera #1",
        "Device (Living Room)",
        "温度センサー",
    ])
    def test_set_device_name_special_characters(self, special_name):
        self._set_expected_name(special_name)

        response = self.device_service.change_device_name_via_cloud(special_name)
        assert response.name == special_name

    def test_set_device_name_unauthorized(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.json.return_value = {"error": "UNAUTHORIZED"}
        self.mock_cloud_set_name.side_effect = HTTPError(response=mock_resp)

        with pytest.raises(HTTPError) as exc_info:
            self.device_service.change_device_name_via_cloud("Test Name")

        assert exc_info.value.response.status_code == 401

    def test_set_device_name_whitespace_only(self):
        with pytest.raises(ValidationError) as exc_info:
            self.device_service.change_device_name_via_cloud("   ")

        assert "Device name cannot be empty" in str(exc_info.value)
