import pytest
from fastapi.testclient import TestClient
from main import app
from fastapicomponents.user_module.config import get_user_config
from fastapicomponents.db_module.database import Base, engine, SessionLocal
from fastapicomponents.db_module.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="module")
def db_session():
    """
    Creates a new in-memory SQLite database for each test.
    The poolclass=StaticPool keeps one shared connection
    so the app and the test share the same tables.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module", autouse=True)
def client(db_session):
    """
    Overrides FastAPI's get_db dependency so that every request
    inside tests uses the same in-memory session.
    """
    def override_get_db():
        yield db_session  # DO NOT close here

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()