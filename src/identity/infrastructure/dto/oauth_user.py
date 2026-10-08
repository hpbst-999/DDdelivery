from dataclasses import dataclass


@dataclass(frozen=True)
class OAuthUserData:
    email: str
    name: str | None = None
