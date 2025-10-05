from sqlalchemy import Column, Integer, String, JSON , ForeignKey
from sqlalchemy.orm import relationship
from fastapicomponents.db_module.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    auth_subject = Column(String, ForeignKey("auth_users.subject", ondelete="CASCADE"), unique=True, nullable=False)

    # 🧩 Flexible identity fields
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    user_id = Column(String, unique=True, index=True, nullable=True)  # For SSO / external users


    auth = relationship("UserAuth", backref="user", uselist=False)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"