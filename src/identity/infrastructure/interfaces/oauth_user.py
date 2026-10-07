from typing import Protocol


class IAuthUser(Protocol):
    @property
    def email(self) -> str: ...

    @property
    def name(self) -> str: ...
