from typing import Optional
from clients.cloud_client import CloudAPIClient
from clients.device_client import DeviceAPIClient
from settings import config
from utils.logger import setup_logger


class AuthService:
    """Handles auth token caching for cloud and device APIs."""

    
    _instance = None
    _cloud_token: Optional[str] = None
    _device_token: Optional[str] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cloud_client = CloudAPIClient()
            cls._instance.device_client = DeviceAPIClient()
            cls._instance.logger = setup_logger("AuthService")
        return cls._instance
    
    def get_cloud_token(self, force_refresh: bool = False) -> str:
        if not self._cloud_token or force_refresh:
            self.logger.info("Authenticating with cloud service...")
            self._cloud_token = self.cloud_client.login(config.USERNAME, config.PASSWORD)
            self.logger.info("Cloud authentication successful")
        return self._cloud_token
    
    def get_device_token(self, force_refresh: bool = False) -> str:
        if not self._device_token or force_refresh:
            self.logger.info("Authenticating with device...")
            self._device_token = self.device_client.login(config.USERNAME, config.PASSWORD)
            self.logger.info("Device authentication successful")
        return self._device_token
    
    def clear_tokens(self):
        self._cloud_token = None
        self._device_token = None
        self.logger.debug("Tokens cleared")