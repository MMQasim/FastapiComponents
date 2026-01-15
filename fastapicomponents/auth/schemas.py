from pydantic import BaseModel, EmailStr,create_model,field_validator
from typing import List
from fastapicomponents.user_module.config import get_user_config#user_config
from enum import Enum
import re
user_config = get_user_config()
class RoleEnum(str,Enum):
    admin="admin"
    user="user"
    guest="guest"
    shopkeeper="owner"



class CoreUserBase(BaseModel):
    password: str
    #roles: List[str] = []

    @field_validator("password")
    def validate_password_strength(cls, v: str):
        """
        Enforce strong password policy:
        - ≥8 chars
        - at least one lowercase, uppercase, digit
        - at least one special character (except ' and ")
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit.")

        # Require a special character that is *not* ' or "
        # This class allows punctuation and symbols excluding quotes
        if not re.search(r"[^\w\s'\"\\]", v):
            raise ValueError("Password must contain at least one special character (excluding ' and \").")

        # Explicitly reject if contains single or double quotes
        if "'" in v or '"' in v:
            raise ValueError("Password cannot contain ' or \" characters.")

        return v



def make_user_login_model(identifier_field: str):
    """Dynamically create UserLogin model depending on config."""
    field_map = {
        "email": {"email": (EmailStr, ...)},
        "username": {"username": (str, ...)},
        "phone": {"phone": (str, ...)},
        "user_id": {"user_id": (str, ...)},
    }

    extra_fields = field_map.get(identifier_field, {"user_id": (str, ...)})

    model= create_model(
        "UserLogin",
        **extra_fields,
        __base__=CoreUserBase
    )

    if identifier_field == "phone":
        @field_validator("phone")
        def validate_phone(cls, v):
            if not re.match(r"^\+?[1-9]\d{7,15}$", v):
                raise ValueError("Invalid phone number format.")
            return v
        model.validate_phone = validate_phone

    elif identifier_field == "username":
        @field_validator("username")
        def validate_username(cls, v):
            if len(v) < 3:
                raise ValueError("Username too short.")
            return v
        model.validate_username = validate_username

    # Ensure the model rebuilds internal schema
    model.model_rebuild()
    return model

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

    model = create_model(
        "RegisteredUser",
        **extra_fields,
        __base__=BaseRegisteredUser
    )

    if identifier_field == "phone":
        @field_validator("phone")
        def validate_phone(cls, v):
            if not re.match(r"^\+?[1-9]\d{7,15}$", v):
                raise ValueError("Invalid phone number format.")
            return v
        model.validate_phone = validate_phone

    elif identifier_field == "username":
        @field_validator("username")
        def validate_username(cls, v):
            if len(v) < 3:
                raise ValueError("Username too short.")
            return v
        model.validate_username = validate_username

    # Ensure the model rebuilds internal schema
    model.model_rebuild()
    return model

RegisteredUser= make_user_registered_user(user_config.USER_IDENTIFIER_FIELD)