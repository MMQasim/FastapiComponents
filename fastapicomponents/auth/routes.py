from fastapi import APIRouter, HTTPException
from fastapicomponents.auth import security
from fastapicomponents.auth.interfaces import SSOProvider
from fastapicomponents.user_module.config import user_config
from fastapicomponents.auth.schemas import UserLogin,UserRegister,RegisteredUser
from fastapicomponents.db_module.database import get_db
from fastapicomponents.auth.services import get_auth_user_by_subject,create_auth_user
from fastapi import Depends
from fastapicomponents.auth.models import UserAuth
from fastapicomponents.user_module.services import create_user



def get_auth_router(sso_provider: SSOProvider | None = None):
    router = APIRouter()

    @router.post("/login")
    def login(user_credentials: UserLogin,db=Depends(get_db)):
        
        #get user from auth db table
        user:UserAuth = get_auth_user_by_subject(db=db,subject=user_credentials.model_dump()[user_config.USER_IDENTIFIER_FIELD ])#user_provider.get_user()
        
        if not user or not security.verify_password(user_credentials.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access = security.create_access_token(
            user.subject,
            getattr(user, "roles", [])
        )
        refresh = security.create_refresh_token(user.subject)
        return {"access_token": access, "refresh_token": refresh}

    @router.post("/register",status_code=201)
    def register(user_data: UserRegister,db=Depends(get_db))-> RegisteredUser:
        subject=user_data.model_dump()[user_config.USER_IDENTIFIER_FIELD ]
        auth_user=get_auth_user_by_subject(db=db,subject=subject)
        if auth_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        new_auth_user = create_auth_user(
            db=db,
            subject=subject,
            hashed_password=security.hash_password(user_data.password),
            roles=user_data.roles
        )

        new_user = create_user(db=db,auth_subject=subject)

        output={'roles':new_auth_user.roles,user_config.USER_IDENTIFIER_FIELD:subject}
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

    return router