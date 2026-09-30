from typing import Any


class OAuthServiceFactory:

    def __init__(self, services: dict[str, Any]):
        self._services = services

    def get_service(self, provider: str) -> Any:
        service = self._services.get(provider)
        if not service:
            raise ValueError("Unknown provider")
        return service
