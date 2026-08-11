from datetime import datetime
from typing import Self
from uuid import UUID

from training_systems.domain import Aggregate


class User(Aggregate):
    def __init__(
        self,
        name: str,
        email: str,
        picture_url: str | None = None,
        id: UUID | None = None,
        created_time: datetime | None = None,
    ) -> None:
        super().__init__(id=id, created_time=created_time)
        self._name = name
        self._email = email
        self._picture_url = picture_url

    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> str:
        return self._email

    @property
    def picture_url(self) -> str | None:
        return self._picture_url

    def update_profile(
        self, *, name: str | None = None, picture_url: str | None = None
    ) -> Self:
        if name is not None:
            self._name = name
        if picture_url is not None:
            self._picture_url = picture_url
        return self
