import pytest
from fastapi.testclient import TestClient
from main import app
from fastapicomponents.db_module.database import Base, engine, SessionLocal
from fastapicomponents.db_module.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool



'''@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Recreate tables for a clean test environment
    Base.metadata.drop_all(bind=engine)
    # Create all tables before tests
    Base.metadata.create_all(bind=engine)

    yield  # run the tests

    # Optionally drop tables after tests
    Base.metadata.drop_all(bind=engine)'''

@pytest.fixture(scope="module", autouse=True)
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
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

client = TestClient(app)
def test_register_user():
    response = client.post("/auth/register", json={
        "username": "testur",
        "email": "tes@example.com",
        "password": "secret123",
        "roles": ["user"]
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testur"
    assert "hashed_password" in data

def test_login_with_username():
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "secret123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_login_with_wrong_password():
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"