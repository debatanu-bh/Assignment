import pytest
from services.device_service import DeviceService
from services.auth_service import AuthService


@pytest.mark.real
class TestDeviceDeviceNameReal:

    @pytest.fixture(autouse=True)
    def setup(self, device_service_real):
        self.device_service = device_service_real
        AuthService._cloud_token = None
        AuthService._device_token = None

    def test_get_device_name(self):
        device_name = self.device_service.get_device_name_from_device()

        assert device_name is not None
        assert isinstance(device_name, str)
        assert len(device_name) > 0

    def test_device_name_matches_cloud_set(self):
        expected = "Real Test Device"

        self.device_service.change_device_name_via_cloud(expected)
        actual = self.device_service.get_device_name_from_device()

        assert actual == expected

    def test_concurrent_reads_consistent(self):
        from concurrent.futures import ThreadPoolExecutor

        expected = "Concurrent Real Test"
        self.device_service.change_device_name_via_cloud(expected)

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self.device_service.get_device_name_from_device)
                for _ in range(5)
            ]
            results = [f.result() for f in futures]

        assert all(name == expected for name in results)
