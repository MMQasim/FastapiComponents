from typing import Protocol,TypeVar,Optional

UserType = TypeVar("UserType")

class UserProvider(Protocol[UserType]):
    def get_user(self, **filters) -> Optional[UserType]:
        ...


class UserRegistrar(Protocol[UserType]):
    def create_user(self, user_data) -> UserType:
        ...

class SSOProvider(Protocol[UserType]):
    def authenticate(self, token: str, provider: str) -> UserType:
        ...