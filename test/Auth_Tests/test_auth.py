
from requests import Session
from fastapicomponents.auth.services import get_auth_user_by_subject
from datetime import datetime, timezone, timedelta
import pytest



#======================================================================
# Test Helper Functions

def registertion_test_case(client, credentials:dict):
    response = client.post("/auth/register", json=credentials)
    assert response.status_code == 201
    data = response.json()

def login_test_case(client,credentials:dict):
    response = client.post("/auth/login", json=credentials)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    return data

def invalid_login_test_case(client,credentials:dict):
    response = client.post("/auth/login", json=credentials)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["message"] == "Invalid login credentials."

def refresh_token_test_case(client,refresh_token:str):
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {refresh_token}"}
    response = client.post("/auth/refresh", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    return data

def invalid_refresh_token_test_case(client,invalid_refresh_token:str):
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {invalid_refresh_token}"}
    response = client.post("/auth/refresh", headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    return data

def ensure_utc(dt):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def new_account_verification_test_case(client,db_session: Session,subject:str):
    authuser=get_auth_user_by_subject(db=db_session,subject=subject)
    assert authuser.is_verified == False
    created_at = ensure_utc(authuser.created_at)
    now = datetime.now(timezone.utc)
    assert now - timedelta(seconds=5) <=  created_at <= now + timedelta(seconds=5)
#====================================================================
# Test Cases

AUTH_CASES = [
    ("email", "test@example.com"),
    ("username", "testuser"),
    ("phone", "+49123456789"),
    ("google", "google-sub-123"),
]
INVALID_AUTH_CASES = [
    ("email", "Test@exaple.com"),
    ("username", "tEStus"),
    ("phone", "+491256789"),
    ("google", "google-su-123"),
]
PASSWORD="Secret@123"


@pytest.mark.parametrize(
    "identifier_type,identifier",
    AUTH_CASES,
)
def test_register_route(client,identifier_type, identifier):
    payload = {
        "identifier": identifier,
        "identifier_type": identifier_type,
        "password": PASSWORD if identifier_type != "google" else None,
    }
    registertion_test_case(client,payload)

@pytest.mark.parametrize(
    "identifier_type,identifier",
    AUTH_CASES,
)
def test_login_route(client,identifier_type, identifier):
    payload = {
        "identifier": identifier,
        "identifier_type": identifier_type,
        "password": PASSWORD if identifier_type != "google" else None,
    }
    login_test_case(client,payload)

@pytest.mark.parametrize(
    "identifier_type,identifier",
    INVALID_AUTH_CASES
)
def test_invalid_login_route(client,identifier_type, identifier):
    payload = {
        "identifier": identifier,
        "identifier_type": identifier_type,
        "password": PASSWORD+'lks' if identifier_type != "google" else None,
    }
    invalid_login_test_case(client,payload)


@pytest.mark.parametrize(
    "identifier_type,identifier",
    AUTH_CASES
)
def test_refresh_route(client,identifier_type, identifier):
    payload = {
        "identifier": identifier,
        "identifier_type": identifier_type,
        "password": PASSWORD if identifier_type != "google" else None,
    }

    login_data = login_test_case(client,payload)
    refresh_token = login_data['refresh_token']
    refresh_token_test_case(client,refresh_token)


@pytest.mark.parametrize(
    "identifier_type,identifier",
    AUTH_CASES
)
def test_account_verification(client,db_session: Session,identifier_type, identifier):
    new_account_verification_test_case(client,db_session,identifier)


def test_invalid_refresh_route(client):
    invalid_refresh_token_test_case(client,"invalidtoken1234567890")
#======================================================================

