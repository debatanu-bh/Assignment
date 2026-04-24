from typing import Optional
from clients.cloud_client import CloudAPIClient
from clients.device_client import DeviceAPIClient
from services.auth_service import AuthService
from models.device import DeviceNameRequest, DeviceNameResponse
from utils.logger import setup_logger


class DeviceService:
    """Orchestrates cloud + device APIs for device management."""

    
    def __init__(self):
        self.cloud_client = CloudAPIClient()
        self.device_client = DeviceAPIClient()
        self.auth_service = AuthService()
        self.logger = setup_logger("DeviceService")

    def change_device_name_via_cloud(self, new_name: str) -> DeviceNameResponse:
        request = DeviceNameRequest(name=new_name)
        token = self.auth_service.get_cloud_token()

        self.logger.info(f"Changing device name to '{request.name}' via cloud")
        response = self.cloud_client.set_device_name(token, request.name)

        return DeviceNameResponse(
            name=request.name,
            updated_at=response.get("updated_at")
        )
    
    def get_device_name_from_device(self) -> str:
        token = self.auth_service.get_device_token()
        
        self.logger.info("Getting device name directly from device")
        device_name = self.device_client.get_device_name(token)
        
        return device_name
    
    def verify_device_name_on_device(self, expected_name: str) -> bool:
        """Check that the device's local API returns the expected name."""
        device_name = self.get_device_name_from_device()

        self.logger.info(f"Expected: '{expected_name}', Device reports: '{device_name}'")

        return device_name == expected_name