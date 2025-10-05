# user_module/service.py
from .schemas import UserBase
from fastapi import HTTPException
from fastapicomponents.user_module.config import user_config
from fastapicomponents.auth.security import hash_password
from fastapicomponents.user_module.models import User



def create_user(db,auth_subject:str) -> User:
    user_data = {
        "auth_subject": auth_subject,
    }

    # Add field dynamically only if model actually has it
    if hasattr(User, user_config.USER_IDENTIFIER_FIELD):
        user_data[user_config.USER_IDENTIFIER_FIELD] = auth_subject
    else:
        user_data["user_id"] = auth_subject  # fallback

    new_user = User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
