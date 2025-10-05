# user_module/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapicomponents.user_module.config import user_config
# -------------------------------------------------------------------
# 📦 DATABASE CONFIGURATION
# -------------------------------------------------------------------

# Example for SQLite
DATABASE_URL = user_config.DATABASE_URL

# Example for PostgreSQL
# DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/mydb"

# -------------------------------------------------------------------
# ⚙️ ENGINE & SESSION
# -------------------------------------------------------------------

# 'check_same_thread=False' is required for SQLite when used in FastAPI
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Factory that creates new Session objects per request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# -------------------------------------------------------------------
# 🧩 DEPENDENCY (for FastAPI routes)
# -------------------------------------------------------------------

def get_db():
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()