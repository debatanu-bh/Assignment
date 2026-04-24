import pytest
from services.device_service import DeviceService
from services.auth_service import AuthService


@pytest.mark.real
class TestCloudDeviceNameReal:

    @pytest.fixture(autouse=True)
    def setup(self, device_service_real):
        self.device_service = device_service_real
        AuthService._cloud_token = None
        AuthService._device_token = None

    def test_set_and_verify_device_name(self):
        new_name = "Integration Test Camera"

        response = self.device_service.change_device_name_via_cloud(new_name)
        assert response.name == new_name

        # Read back from device
        assert self.device_service.verify_device_name_on_device(new_name)

    def test_update_device_name_twice(self):
        first_name = "First Name"
        second_name = "Second Name"

        self.device_service.change_device_name_via_cloud(first_name)
        self.device_service.change_device_name_via_cloud(second_name)

        device_name = self.device_service.get_device_name_from_device()
        assert device_name == second_name

    def test_special_characters_round_trip(self):
        special_name = "Camera #1 — 温度センサー"

        self.device_service.change_device_name_via_cloud(special_name)

        device_name = self.device_service.get_device_name_from_device()
        assert device_name == special_name
