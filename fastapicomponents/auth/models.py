from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import declarative_base
from fastapicomponents.db_module.database import Base

class UserAuth(Base):
    __tablename__ = "auth_users"

    id = Column(Integer, primary_key=True, index=True)

    # 🧩 Identity fields
    subject = Column(String, unique=True, index=True, nullable=False)

    # 🔐 Authentication
    hashed_password = Column(String, nullable=True)

    # 🧠 Roles and permissions
    # Use JSON instead of ARRAY for better cross-database support (SQLite, MySQL, PostgreSQL)
    roles = Column(JSON, default=list)

    def __repr__(self):
        return f"<User(id={self.id}, subject={self.subject})>"