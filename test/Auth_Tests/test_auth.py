
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

def new_account_verification_test_case(client,db_session: Session,subject:str,identifirer_type:str):
    authuser=get_auth_user_by_subject(db=db_session,subject=subject)
    
    created_at = ensure_utc(authuser.created_at)
    now = datetime.now(timezone.utc)
    assert now - timedelta(seconds=5) <=  created_at <= now + timedelta(seconds=5)

    if identifirer_type in ["email","username","phone"]:
        assert authuser.hashed_password is not None
        assert authuser.is_verified == False
        assert authuser.verification_code is not None
        assert authuser.verification_code_expires_at is not None
    else:
        assert authuser.hashed_password is None
        assert authuser.is_verified == True
        assert authuser.verification_code is None
        assert authuser.verification_code_expires_at is None
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
    new_account_verification_test_case(client,db_session,identifier,identifier_type)

@pytest.mark.parametrize(
    "identifier_type,identifier",
    AUTH_CASES
)
def test_account_verification_invalid_code(client,db_session: Session,identifier_type, identifier):

    authuser=get_auth_user_by_subject(db=db_session,subject=identifier)
    if authuser.is_verified:
        return  # Skip test if already verified
    invalid_code = authuser.verification_code + 1 if authuser.verification_code else 123456

    response = client.put(
        "/auth/verify-account/{verification_code}".format(verification_code=invalid_code),
        #payload={"verification_code": invalid_code},
        headers={"Authorization": f"Bearer {login_test_case(client,{'identifier': identifier,'identifier_type': identifier_type,'password': PASSWORD if identifier_type !='google' else None})['access_token']}"}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid verification code"


@pytest.mark.parametrize(
    "identifier_type,identifier",
    AUTH_CASES
)
def test_update_account_verification(client,db_session: Session,identifier_type, identifier):
    
    authuser=get_auth_user_by_subject(db=db_session,subject=identifier)
    if authuser.is_verified:
        return  # Skip test if already verified

    response = client.put(
        "/auth/verify-account/{verification_code}".format(verification_code=authuser.verification_code),
        headers={"Authorization": f"Bearer {login_test_case(client,{'identifier': identifier,'identifier_type': identifier_type,'password': PASSWORD if identifier_type !='google' else None})['access_token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Account verified successfully"

    # Verify in DB
    updated_authuser=get_auth_user_by_subject(db=db_session,subject=identifier)
    assert updated_authuser.is_verified == True
    assert updated_authuser.verification_code is None
    assert updated_authuser.verification_code_expires_at is None
    
def test_invalid_refresh_route(client):
    invalid_refresh_token_test_case(client,"invalidtoken1234567890")
#======================================================================

