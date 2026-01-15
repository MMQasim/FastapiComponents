
from fastapicomponents.user_module.config import get_user_config
import logging



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
    }}
#======================================================================
# Test Cases


def test_register_route(client):
    logging.info(f"Testing with identifier field: {config.USER_IDENTIFIER_FIELD}")
    registertion_test_case(client,cradentials['valid'])


def test_login_route(client):
    logging.info(f"Testing with identifier field: {config.USER_IDENTIFIER_FIELD}")
    login_test_case(client,cradentials['valid'])

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

#======================================================================

