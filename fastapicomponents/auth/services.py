
from fastapicomponents.auth.models import UserAuth


def get_auth_user_by_subject(db, subject: str):
    return db.query(UserAuth).filter(UserAuth.subject == subject).first()

def create_auth_user(db, subject: str, hashed_password: str, roles: list = []):
    auth_user = UserAuth(
        subject=subject,
        hashed_password=hashed_password,
        roles=roles
    )
    db.add(auth_user)
    db.commit()
    db.refresh(auth_user)
    return auth_user

