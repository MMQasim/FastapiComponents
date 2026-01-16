# user_module/service.py
from fastapicomponents.user_module.models import User



def create_user(db,auth_subject:str,identifier_type:str) -> User:
    user_data = {
        "auth_subject": auth_subject,
    }
    # Add field dynamically only if model actually has it
    if hasattr(User, identifier_type):
        user_data[identifier_type] = auth_subject
    else:
        user_data["user_id"] = auth_subject  # fallback

    new_user = User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_by_identifire(db, identifier: str, identifier_type: str)-> User | None:
    user_data = {}
    if hasattr(User, identifier_type):
        user_data[identifier_type] = identifier
    else:
        user_data["user_id"] = identifier

    return db.query(User).filter_by(**user_data).first()