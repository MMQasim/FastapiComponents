from pydantic import BaseModel, EmailStr,create_model,field_validator, model_validator
from typing import List, Optional
from fastapicomponents.user_module.config import get_user_config#user_config
from enum import Enum
import re
user_config = get_user_config()
class RoleEnum(str,Enum):
    admin="admin"
    user="user"
    guest="guest"
    shopkeeper="owner"

class IdentifierFieldEnum(str,Enum):
    email="email"
    username="username"
    phone="phone"
    user_id="user_id" # generic unique id for SSO or other methods
    google="google" # SSO via google



class CoreUserBase(BaseModel):
    #password: str
    identifier: str
    identifier_type: IdentifierFieldEnum
    password: Optional[str] = None
    #roles: List[str] = []

    @field_validator("password")
    def validate_password_strength(cls, v: str):
        """
        Enforce strong password policy:
        - ≥8 chars
        - at least one lowercase, uppercase, digit
        - at least one special character (except ' and ")
        """
        if v is None:
            return v 
        
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


    @model_validator(mode="after")
    def validate_auth_rules(self):
        # EMAIL
        if self.identifier_type == IdentifierFieldEnum.email:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", self.identifier):
                raise ValueError("Invalid email format")
            if not self.password:
                raise ValueError("Password required for email registration")

        # USERNAME
        elif self.identifier_type == IdentifierFieldEnum.username:
            if len(self.identifier) < 3:
                raise ValueError("Username too short")
            if not self.password:
                raise ValueError("Password required for username registration")

        # PHONE
        elif self.identifier_type == IdentifierFieldEnum.phone:
            if not re.match(r"^\+?[1-9]\d{7,15}$", self.identifier):
                raise ValueError("Invalid phone number format")
            # password optional (OTP flow)

        # GOOGLE SSO
        elif self.identifier_type == IdentifierFieldEnum.google:
            if self.password:
                raise ValueError("Password not allowed for Google SSO")

        return self

class UserLogin(CoreUserBase): 
    # UserLogin login input schema
    pass

class UserRegister(CoreUserBase): 
    # UserRegister registration input schema
    roles: List[RoleEnum] = [RoleEnum.user.value]

class BaseRegisteredUser(BaseModel):
    roles: List[RoleEnum] = [RoleEnum.user.value]
    identifier: str
    identifier_type: IdentifierFieldEnum

class RegisteredUser(BaseRegisteredUser): 
    # user registration output schema
    pass