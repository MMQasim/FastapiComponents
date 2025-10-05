from pydantic import BaseModel, EmailStr,create_model
from typing import List
from fastapicomponents.user_module.config import user_config
from enum import Enum

class RoleEnum(str,Enum):
    admin="admin"
    user="user"
    guest="guest"
    shopkeeper="owner"



class CoreUserBase(BaseModel):
    password: str
    #roles: List[str] = []



def make_user_login_model(identifier_field: str):
    """Dynamically create UserLogin model depending on config."""
    field_map = {
        "email": {"email": (EmailStr, ...)},
        "username": {"username": (str, ...)},
        "phone": {"phone": (str, ...)},
        "user_id": {"user_id": (str, ...)},
    }

    extra_fields = field_map.get(identifier_field, {"user_id": (str, ...)})

    return create_model(
        "UserLogin",
        **extra_fields,
        __base__=CoreUserBase
    )

# Build it dynamically based on config
UserLogin = make_user_login_model(user_config.USER_IDENTIFIER_FIELD)

class UserRegister(UserLogin):
    roles: List[RoleEnum] = [RoleEnum.user.value]

class BaseRegisteredUser(BaseModel):
    roles: List[RoleEnum] = [RoleEnum.user.value]

def make_user_registered_user(identifier_field: str):
    """Dynamically create RegisteredUser model depending on config."""
    field_map = {
        "email": {"email": (EmailStr, ...)},
        "username": {"username": (str, ...)},
        "phone": {"phone": (str, ...)},
        "user_id": {"user_id": (str, ...)},
    }

    extra_fields = field_map.get(identifier_field, {"user_id": (str, ...)})

    return create_model(
        "RegisteredUser",
        **extra_fields,
        __base__=BaseRegisteredUser
    )

RegisteredUser= make_user_registered_user(user_config.USER_IDENTIFIER_FIELD)