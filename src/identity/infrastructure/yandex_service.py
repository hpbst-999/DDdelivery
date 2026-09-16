import urllib.parse
import httpx

from src.core.config import settings
from src.identity.application.dtos.oauth_user import OAuthUser
from src.identity.application.interfaces import IOAuthService


class YandexOAuthService(IOAuthService):
    AUTH_URL = "https://oauth.yandex.ru/authorize"
    TOKEN_URL = "https://oauth.yandex.ru/token"
    USERINFO_URL = "https://login.yandex.ru/info"

    def __init__(
        self,
        client_id: str = settings.YANDEX_CLIENT_ID,
        client_secret: str = settings.YANDEX_CLIENT_SECRET,
    ):
        self._client_id = client_id
        self._client_secret = client_secret

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        params = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "force_confirm": "yes"
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

    async def get_user_info(self, code: str, redirect_uri: str) -> OAuthUser:
        async with httpx.AsyncClient(timeout=10.0) as client:
            token_response = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret
                }
            )
            token_response.raise_for_status()
            access_token = token_response.json().get("access_token")

            user_response = await client.get(
                self.USERINFO_URL,
                headers={"Authorization": f"OAuth {access_token}"},
                params={"format": "json"},
            )
            user_response.raise_for_status()
            user_data = user_response.json()

            email = user_data.get("default_email")
            if not email:
                raise ValueError("Email has not been provided")

            name = (
                user_data.get("real_name")
                or user_data.get("display_name")
                or user_data.get("first_name")
            )

            return OAuthUser(email=email, name=name)