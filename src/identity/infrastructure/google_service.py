import urllib.parse
import httpx

from src.core.config import settings
from src.identity.application.interfaces import IOAuthService
from src.identity.application.dtos.oauth_user import OAuthUser


class GoogleOAuthService(IOAuthService):
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    def __init__(
            self,
            client_id : str= settings.GOOGLE_CLIENT_ID,
            client_secret: str = settings.GOOGLE_CLIENT_SECRET):
        self._client_id = client_id
        self._client_secret = client_secret

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        params = {
        "client_id": self._client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state, #сделать хранилище и проверку
        "prompt": "select_account",
    }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

    async def get_user_info(self, code, redirect_uri) -> OAuthUser:
        async with httpx.AsyncClient(timeout=10) as client:
            token_response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri
                }
            )
            if token_response.is_error:
                print("GOOGLE TOKEN ERROR BODY:", token_response.text)
            token_response.raise_for_status()
            access_token = token_response.json().get("access_token")

            user_response = await client.get(
                self.USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_response.raise_for_status()
            user_data = user_response.json()

            email = user_data.get("email")
            if not email:
                raise ValueError("Email has not been provided")

            return OAuthUser(email=email, name = user_data.get("name"))



        
