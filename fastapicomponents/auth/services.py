
from fastapicomponents.auth.models import UserAuth
from sqlalchemy import func
from typing import Optional
import secrets
from datetime import datetime, timedelta, timezone

def generate_6_digit_code() -> int:
    return secrets.randbelow(900_000) + 100_000


def get_auth_user_by_subject(db, subject: str):
    return db.query(UserAuth).filter(UserAuth.subject == subject).first()

def update_logged_in_at(db, user: UserAuth):
    user.logged_in_at = func.now()
    db.commit()
    db.refresh(user)
    return user

def update_verification_code(db, user: UserAuth,account_verified:bool):
    if account_verified:
        user.is_verified = True
        user.verification_code = None
        user.verification_code_expires_at = None
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    else:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=60)
        user.verification_code = generate_6_digit_code()
        user.verification_code_expires_at = expires_at
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

def create_auth_user(db, subject: str, hashed_password: Optional[str],is_verified:bool, roles: list = [] ) -> UserAuth:

    if is_verified:
        auth_user = UserAuth(
            subject=subject,
            hashed_password=hashed_password,
            is_verified=is_verified,
            roles=roles
        )
    else:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=60)
        auth_user = UserAuth(
            subject=subject,
            hashed_password=hashed_password,
            roles=roles,
            is_verified=is_verified,
            verification_code=generate_6_digit_code(),
            verification_code_expires_at=expires_at
        )

    
    db.add(auth_user)
    db.commit()
    db.refresh(auth_user)
    return auth_user

