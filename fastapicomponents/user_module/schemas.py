from pydantic import BaseModel, EmailStr
from typing import List,Optional

class UserBase(BaseModel):
    email:Optional[EmailStr] 
    username:Optional[str]
    phone:Optional[str]
    user_id:Optional[str]

