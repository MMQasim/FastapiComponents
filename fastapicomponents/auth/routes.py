import logging
from fastapi import APIRouter, HTTPException
from fastapicomponents.auth import security
from fastapicomponents.auth.interfaces import SSOProvider
from fastapicomponents.user_module.config import get_user_config#user_config
from fastapicomponents.auth.schemas import UserLogin,UserRegister,RegisteredUser, IdentifierFieldEnum
from fastapicomponents.db_module.database import get_db
from fastapicomponents.auth.services import get_auth_user_by_subject,create_auth_user
from fastapi import Depends
from fastapicomponents.auth.models import UserAuth
from fastapicomponents.auth.security import renew_access_token
from fastapicomponents.user_module.services import create_user
from sqlalchemy.orm import Session



user_config = get_user_config()

def get_auth_router(sso_provider: SSOProvider | None = None):
    router = APIRouter()

    @router.post("/login")
    def login(user_credentials: UserLogin,db:Session=Depends(get_db)):
        
        
        identifier_field = user_config.USER_IDENTIFIER_FIELD
        
        if not identifier_field:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_REQUEST",
                    "message": f"Missing required field: {identifier_field}",
                    "details": {"field": identifier_field},
                },
            )

        #get user from auth db table
        user:UserAuth | None  = get_auth_user_by_subject(db=db,subject=user_credentials.model_dump()[identifier_field].lower())
        if not user or not security.verify_password(user_credentials.password, user.hashed_password):
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
        return {"access_token": access, "refresh_token": refresh}

    @router.post("/register",status_code=201,response_model=RegisteredUser)
    def register(user_data: UserRegister,db=Depends(get_db)):
        

        subject=user_data.identifier#user_data.model_dump()[user_config.USER_IDENTIFIER_FIELD]

        auth_user=get_auth_user_by_subject(db=db,subject=subject.lower())
        if auth_user:
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
                hashed_password=security.hash_password(user_data.password),
                roles=user_data.roles
            )
        else:
            new_auth_user = create_auth_user(
                db=db,
                subject=subject,
                hashed_password=None,
                roles=user_data.roles
            )

        new_user = create_user(db=db,auth_subject=subject,identifier_type=user_data.identifier_type)

        output={'roles':new_auth_user.roles,'identifier':subject,'identifier_type': user_data.identifier_type}
        return RegisteredUser(**output)
    
    

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
    def refresh_token(newToken = Depends(renew_access_token),db: Session = Depends(get_db),):
        return newToken

    return router
