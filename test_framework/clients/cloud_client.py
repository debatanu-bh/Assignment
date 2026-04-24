from typing import Dict, Any
from clients.base_client import BaseAPIClient
from settings import config


class CloudAPIClient(BaseAPIClient):
    """
    Cloud API Client following Service Object Pattern.
    Handles all cloud-related API interactions.

    Cloud REST API (per spec):
      - POST /api/auth/login          -> {"access_token": "..."}
      - POST /api/device/name         -> sets device name
    """

    def get_base_url(self) -> str:
        return config.CLOUD_BASE_URL

    def login(self, username: str, password: str) -> str:
        """
        Authenticate with cloud service.
        POST /api/auth/login
        Returns access token.
        """
        endpoint = "/api/auth/login"
        data = {"username": username, "password": password}

        response = self.post(endpoint, data)
        return response.get("access_token")

    def set_device_name(self, token: str, new_name: str) -> Dict[str, Any]:
        """
        Set device name via cloud API.
        POST /api/device/name
        """
        endpoint = "/api/device/name"
        data = {"name": new_name}

        return self.post(endpoint, data, token=token)