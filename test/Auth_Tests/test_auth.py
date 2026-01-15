
from requests import Session
from fastapicomponents.user_module.config import get_user_config
from fastapicomponents.db_module.database import get_db
from fastapicomponents.auth.services import get_auth_user_by_subject
from datetime import datetime, timezone, timedelta
from fastapicomponents.auth.schemas import IdentifierFieldEnum
import logging
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
#======================================================================

config= get_user_config()
if config.USER_IDENTIFIER_FIELD=='email':
    cradentials = {'valid':{
        "email": "test@example.com",
        "password": "Secret@123",
        "roles": ["user"]
    },'invalid':{
        "email": "te@example.com",
        "password": "Secrklj@123",
        "roles": ["user"]
    },'uppervalid':{
        "email": "Test@example.com",
        "password": "Secret@123",
        "roles": ["user"]
    }}
elif config.USER_IDENTIFIER_FIELD=='username':
    cradentials = {'valid':{
        "username": "testuser",
        "password": "Secret@123",
        "roles": ["user"]
    },'invalid':{
        "username": "testus",
        "password": "Secrklj@123",
        "roles": ["user"]
    },'uppervalid':{
        "username": "Testuser",
        "password": "Secret@123",
        "roles": ["user"]
    }}
elif config.USER_IDENTIFIER_FIELD=='phone':
    cradentials = {'valid':{
        "phone": "1234567890",
        "password": "Secret@123",
        "roles": ["user"]
    },'invalid':{
        "phone": "0987654321",
        "password": "Secrklj@123",
        "roles": ["user"]
    },'uppervalid':{
        "phone": "0987654321",
        "password": "Secret@123",
        "roles": ["user"]
    }}
else:
    cradentials = {'valid':{
        "user_id": "uniqueuser123",
        "password": "Secret@123",
        "roles": ["user"]
    },'invalid':{
        "user_id": "uniqueuser12",
        "password": "Secrklj@123",
        "roles": ["user"]
    },'uppervalid':{
        "user_id": "Uniqueuser123",
        "password": "Secret@123",
        "roles": ["user"]
    }}
#======================================================================
# Test Cases

@pytest.mark.parametrize(
    "identifier_type,identifier",
    [
        ("email", "test@example.com"),
        ("username", "testuser"),
        ("phone", "+49123456789"),
        ("google", "google-sub-123"),
    ],
)
def test_register_route(client,identifier_type, identifier):
    payload = {
        "identifier": identifier,
        "identifier_type": identifier_type,
        "password": "Secret@123" if identifier_type != "google" else None,
    }
    registertion_test_case(client,payload)

"""
def test_login_route(client):
    logging.info(f"Testing with identifier field: {config.USER_IDENTIFIER_FIELD}")
    login_test_case(client,cradentials['valid'])

def test_login_route(client):
    logging.info(f"Testing with identifier field: {config.USER_IDENTIFIER_FIELD}")
    login_test_case(client,cradentials['uppervalid'])

def test_invalid_login_route(client):
    logging.info(f"Testing with identifier field: {config.USER_IDENTIFIER_FIELD}")
    invalid_login_test_case(client,cradentials['invalid'])

def test_refresh_route(client):
    logging.info(f"Testing with identifier field: {config.USER_IDENTIFIER_FIELD}")
    login_data = login_test_case(client,cradentials['valid'])
    refresh_token = login_data['refresh_token']
    refresh_token_test_case(client,refresh_token)

def test_invalid_refresh_route(client):
    logging.info(f"Testing with identifier field: {config.USER_IDENTIFIER_FIELD}")
    invalid_refresh_token_test_case(client,"invalidtoken1234567890")

def test_account_verification(client,db_session: Session):
    logging.info(f"Testing with identifier field: {config.USER_IDENTIFIER_FIELD}")
    subject_value = cradentials['valid'][config.USER_IDENTIFIER_FIELD].lower()
    new_account_verification_test_case(client,db_session,subject_value)
"""
#======================================================================

