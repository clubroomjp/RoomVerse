from abc import ABC, abstractmethod
import requests
from typing import List, Dict, Optional
import json

class DiscoveryClient(ABC):
    @abstractmethod
    def announce(self, uuid: str, url: str, metadata: Dict) -> bool:
        pass

    @abstractmethod
    def list_rooms(self) -> List[Dict]:
        pass

class MockDiscoveryClient(DiscoveryClient):
    """
    A temporary mock client that just prints to console and returns static data.
    Useful for testing without a real backend.
    """
    def announce(self, uuid: str, url: str, metadata: Dict) -> bool:
        print(f"[Discovery] Announcing presence: {uuid} @ {url} | {metadata}")
        return True

    def list_rooms(self) -> List[Dict]:
        # Return a dummy list for testing
        return [
            {"uuid": "dummy-1", "url": "https://example-room-1.trycloudflare.com", "name": "Test Room 1"},
            {"uuid": "dummy-2", "url": "https://example-room-2.trycloudflare.com", "name": "Test Room 2"}
        ]

class HttpDiscoveryClient(DiscoveryClient):
    """
    Client for a simple HTTP Discovery Service.
    Expected API:
    - POST /announce {uuid, url, metadata}
    - GET /rooms
    """
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip("/")

    def announce(self, uuid: str, url: str, metadata: Dict) -> bool:
        try:
            payload = {
                "uuid": uuid,
                "url": url,
                "name": metadata.get("name", "Unknown Room"),
                "metadata": metadata
            }
            resp = requests.post(f"{self.api_url}/announce", json=payload, timeout=5)
            return resp.status_code == 200
        except Exception as e:
            print(f"[Discovery] Failed to announce: {e}")
            return False

    def list_rooms(self) -> List[Dict]:
        try:
            resp = requests.get(f"{self.api_url}/rooms", timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"[Discovery] Failed to list rooms: {e}")
        return []

def get_discovery_client(config) -> DiscoveryClient:
    """Factory to get the appropriate client based on config."""
    # Check config.room.discovery_api_url
    if hasattr(config, 'room') and config.room and config.room.discovery_api_url:
        return HttpDiscoveryClient(config.room.discovery_api_url)
    return MockDiscoveryClient()
