from dataclasses import dataclass


@dataclass(frozen=True)
class TokenPairData:
    access_token: str
    refresh_token: str