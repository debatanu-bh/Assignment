from typing import Dict, Any
from clients.base_client import BaseAPIClient
from settings import config


class DeviceAPIClient(BaseAPIClient):
    """Client for the local device REST API."""

    
    def get_base_url(self) -> str:
        return config.DEVICE_BASE_URL
    
    def login(self, username: str, password: str) -> str:
        endpoint = "/api/auth/login"
        data = {"username": username, "password": password}
        
        response = self.post(endpoint, data)
        return response.get("access_token")
    
    def get_device_name(self, token: str) -> str:
        endpoint = "/api/device/name"
        
        response = self.get(endpoint, token=token)
        return response.get("name")
    
    def reboot_device(self, token: str) -> Dict[str, Any]:
        endpoint = "/api/device/reboot"
        
        return self.post(endpoint, {}, token=token)
    
    def get_device_info(self, token: str) -> Dict[str, Any]:
        endpoint = "/api/device/info"
        
        return self.get(endpoint, token=token)