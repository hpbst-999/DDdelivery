from typing import Protocol


class ITokenPair(Protocol):
    @property
    def access_token(self) -> str: ...

    @property
    def refresh_token(self) -> str: ...
