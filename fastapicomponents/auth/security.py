# auth_module/security.py
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapicomponents.db_module.database import get_db
from fastapicomponents.auth.services import get_auth_user_by_subject
from typing import Any, Dict
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapicomponents.auth.config import Settings
from datetime import timezone
# ---------------------------------------------------------------------------
# 🔐 CONFIGURATION
# ---------------------------------------------------------------------------

auth_scheme = HTTPBearer(auto_error=True)
settings = Settings()
SECRET_KEY = settings.AUTH_SECRET_KEY # you’ll load from env in production
ALGORITHM = settings.AUTH_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.AUTH_REFRESH_TOKEN_EXPIRE_DAYS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------------------------
# 🧂 PASSWORD HASHING UTILITIES
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)

# ---------------------------------------------------------------------------
# 🎟 TOKEN CREATION UTILITIES
# ---------------------------------------------------------------------------
def create_access_token(
    subject: str,
    roles: list[str] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a short-lived access token.
    - subject: usually username or user_id
    - roles: optional role list for RBAC
    """
    if roles is None:
        roles = []
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": subject, "roles": roles, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(subject: str) -> str:
    """
    Create a long-lived refresh token.
    """
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": subject, "type": "refresh", "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ---------------------------------------------------------------------------
# 🧩 TOKEN VALIDATION UTILITIES
# ---------------------------------------------------------------------------
def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    Raises JWTError if invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid or expired token: {e}")

def is_refresh_token(token: str) -> bool:
    """
    Check if a decoded token is a refresh token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("type") == "refresh"
    except JWTError:
        return False
    


def validate_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_db),
):
    """
    Dependency that:
    - Extracts JWT token from Authorization header
    - Decodes and validates it
    - Fetches the user dynamically based on USER_IDENTIFIER_FIELD
    - Returns the authenticated user
    """

    token = credentials.credentials

    # Step 1: Decode JWT
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # Step 2: Extract subject (sub)
    subject = payload.get("sub")
    if not subject:
        raise HTTPException(status_code=401, detail="Token missing subject claim")

    

    # Step 4: Query user
    auth_user = get_auth_user_by_subject(db=db,subject=subject)
    if not auth_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return auth_user
