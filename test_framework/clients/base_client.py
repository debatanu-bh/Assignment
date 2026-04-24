import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from settings import config
from utils.retry_decorator import retry
from utils.logger import setup_logger


class BaseAPIClient(ABC):
    """Base client following Template Method pattern for API interactions"""
    
    def __init__(self):
        self.session = requests.Session()
        self.logger = setup_logger(self.__class__.__name__)
        self.timeout = config.REQUEST_TIMEOUT
        
    @abstractmethod
    def get_base_url(self) -> str:
        """Abstract method to be implemented by subclasses"""
        pass
    
    def _build_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """Build standard headers with optional authorization"""
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    @retry(max_attempts=config.RETRY_COUNT, delay=config.RETRY_DELAY)
    def post(self, endpoint: str, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        """Perform POST request with retry logic"""
        url = f"{self.get_base_url()}/{endpoint.lstrip('/')}"
        headers = self._build_headers(token)
        self.logger.debug(f"POST {url} - Data: {data}")
        response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json() if response.content else {}
    
    @retry(max_attempts=config.RETRY_COUNT, delay=config.RETRY_DELAY)
    def get(self, endpoint: str, token: Optional[str] = None) -> Dict[str, Any]:
        """Perform GET request with retry logic"""
        url = f"{self.get_base_url()}/{endpoint.lstrip('/')}"
        headers = self._build_headers(token)
        
        self.logger.debug(f"GET {url}")
        response = self.session.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json() if response.content else {}
    
    # @retry(max_attempts=config.RETRY_COUNT, delay=config.RETRY_DELAY)
    # def put(self, endpoint: str, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
    #     """Perform PUT request with retry logic"""
    #     url = f"{self.get_base_url()}/{endpoint.lstrip('/')}"
    #     headers = self._build_headers(token)
        
    #     self.logger.debug(f"PUT {url} - Data: {data}")
    #     response = self.session.put(url, json=data, headers=headers, timeout=self.timeout)
    #     response.raise_for_status()
        
    #     return response.json() if response.content else {}