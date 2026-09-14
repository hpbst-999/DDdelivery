from dataclasses import dataclass

@dataclass(frozen=True)
class OAuthUser:
    email: str
    name: str | None = None
