import logging
from fastapi import APIRouter, HTTPException
from fastapicomponents.auth import security
from fastapicomponents.auth.interfaces import SSOProvider
from fastapicomponents.user_module.config import get_user_config#user_config
from fastapicomponents.auth.schemas import UserLogin,UserRegister,RegisteredUser, IdentifierFieldEnum
from fastapicomponents.db_module.database import get_db
from fastapicomponents.auth.services import get_auth_user_by_subject,create_auth_user, update_logged_in_at, update_verification_code
from fastapi import Depends
from fastapicomponents.auth.models import UserAuth
from fastapicomponents.auth.security import renew_access_token,validate_user 
from fastapicomponents.user_module.services import create_user, get_user_by_identifire
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from test.Auth_Tests.test_auth import ensure_utc



user_config = get_user_config()

def get_auth_router(sso_provider: SSOProvider | None = None):
    router = APIRouter()

    @router.post("/login")
    def login(user_credentials: UserLogin,db:Session=Depends(get_db)):
        #get user from auth db table
        user:UserAuth | None  = get_auth_user_by_subject(db=db,subject=user_credentials.identifier.lower())
        if not user:
            raise HTTPException(status_code=401,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid login credentials.",
            })
        
        if (user_credentials.identifier_type == IdentifierFieldEnum.email) or (user_credentials.identifier_type == IdentifierFieldEnum.username) or (user_credentials.identifier_type == IdentifierFieldEnum.phone):    
            if not user or not security.verify_password(user_credentials.password, user.hashed_password):
                raise HTTPException(status_code=401,
                detail={
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid login credentials.",
                })
        else:
            # check SSO or other non-password based login
            if not user:
                raise HTTPException(status_code=401,
                detail={
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid login credentials.",
                })

        access = security.create_access_token(
            user.subject,
            getattr(user, "roles", [])
        )
        refresh = security.create_refresh_token(user.subject,roles=getattr(user, "roles", []))
        update_logged_in_at(db=db,user=user)
        return {"access_token": access, "refresh_token": refresh}

    @router.post("/register",status_code=201,response_model=RegisteredUser)
    def register(user_data: UserRegister,db=Depends(get_db)):
        

        subject=user_data.identifier
        # check user in auth table
        auth_user=get_auth_user_by_subject(db=db,subject=subject.lower())

        # check user in user table
        user=get_user_by_identifire(db=db,identifier=subject.lower(),identifier_type=user_data.identifier_type)

        if auth_user or user:
            raise HTTPException(status_code=409, detail={
        "code": "USER_ALREADY_EXISTS",
        "message": "A user with this email or phone already exists.",
        "details": {"field": "email"},
    })
        subject=subject.lower()
        if (IdentifierFieldEnum.email==user_data.identifier_type) or (IdentifierFieldEnum.username==user_data.identifier_type) or (IdentifierFieldEnum.phone==user_data.identifier_type):
            new_auth_user = create_auth_user(
                db=db,
                subject=subject,
                is_verified=False,
                hashed_password=security.hash_password(user_data.password),
                roles=user_data.roles
            )
        else:
            new_auth_user = create_auth_user(
                db=db,
                subject=subject,
                is_verified=True,
                hashed_password=None,
                roles=user_data.roles
            )

        new_user = create_user(db=db,auth_subject=subject,identifier_type=user_data.identifier_type)
        output={'roles':new_auth_user.roles,'identifier':subject,'identifier_type': user_data.identifier_type}
        return RegisteredUser(**output)

    @router.put("/verify-account/{verification_code}")
    def verify_account(verification_code: int,current_user = Depends(validate_user),db: Session = Depends(get_db)):
        if current_user.is_verified:
            raise HTTPException(status_code=400, detail="Account already verified")
        else:
            verification_code_expires_at = ensure_utc(current_user.verification_code_expires_at)
            now = datetime.now(timezone.utc)
            if (verification_code == current_user.verification_code) and \
            (verification_code_expires_at > now):
                update_verification_code(db=db,user=current_user,account_verified=True)
                return {"message": "Account verified successfully"}
            else:
                raise HTTPException(status_code=400, detail="Invalid verification code")


    @router.post("/sso-login")
    def sso_login(provider: str, token: str):
        return
        if not sso_provider:
            raise HTTPException(status_code=501, detail="SSO not supported")

        user = sso_provider.authenticate(token, provider)
        access = security.create_access_token(user.username, getattr(user, "roles", []))
        refresh = security.create_refresh_token(user.username)
        return {"access_token": access, "refresh_token": refresh}


    @router.post("/refresh")
    def refresh_token(newToken = Depends(renew_access_token),db: Session = Depends(get_db)):
        return newToken

    return router
