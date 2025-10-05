# user_module/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from fastapicomponents.user_module.models import User
from fastapicomponents.user_module.schemas import UserBase
from fastapicomponents.db_module.database import get_db
from fastapicomponents.auth.security import validate_user 

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserBase)
def get_current_user(
    current_user = Depends(validate_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.auth_subject == current_user.subject).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user