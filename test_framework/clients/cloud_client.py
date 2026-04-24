from typing import Dict, Any
from clients.base_client import BaseAPIClient
from settings import config


class CloudAPIClient(BaseAPIClient):
    """Client for the cloud REST API (login, device management, etc.)"""


    def get_base_url(self) -> str:
        return config.CLOUD_BASE_URL

    def login(self, username: str, password: str) -> str:
        endpoint = "/api/auth/login"
        data = {"username": username, "password": password}

        response = self.post(endpoint, data)
        return response.get("access_token")

    def set_device_name(self, token: str, new_name: str) -> Dict[str, Any]:
        endpoint = "/api/device/name"
        data = {"name": new_name}

        return self.post(endpoint, data, token=token)