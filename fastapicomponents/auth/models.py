from sqlalchemy import Boolean, Column, DateTime, Integer, String, JSON, func
from sqlalchemy.orm import declarative_base
from fastapicomponents.db_module.database import Base
import uuid

class UserAuth(Base):
    __tablename__ = "auth_users"

    id = Column(String(36),primary_key=True,default=lambda: str(uuid.uuid4()),index=True,nullable=False) # UUID primary key
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False,) # Timestamp when created
    is_verified = Column(Boolean,default=False,nullable=False) # Email/SSO verified
    last_login_at = Column(DateTime(timezone=True),nullable=True) # Nullable until first login
    verification_code = Column(Integer,nullable=True) # NULL once verified or when no active code
    verification_code_expires_at = Column(DateTime(timezone=True),nullable=True) # NULL once verified or when no active code

    # 🧩 Identity fields
    subject = Column(String, unique=True, index=True, nullable=False)

    # 🔐 Authentication
    hashed_password = Column(String, nullable=True)

    # 🧠 Roles and permissions
    # Use JSON instead of ARRAY for better cross-database support (SQLite, MySQL, PostgreSQL)
    roles = Column(JSON, default=list)

    def __repr__(self):
        return f"<User(id={self.id}, subject={self.subject})>"