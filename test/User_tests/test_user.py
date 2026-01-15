
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

def user_profile_test_case(client,token:str):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
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

"""
def test_register_route(client):
    logging.info(f"Testing with identifier field: {config.USER_IDENTIFIER_FIELD}")
    registertion_test_case(client,cradentials['valid'])


def test_user_profile_route(client):
    logging.info(f"Testing with identifier field: {config.USER_IDENTIFIER_FIELD}")
    tokens = login_test_case(client,cradentials['valid'])
    user_data = user_profile_test_case(client,tokens['access_token'])
    identifier_value = cradentials['valid'][config.USER_IDENTIFIER_FIELD]
    assert user_data[config.USER_IDENTIFIER_FIELD] == identifier_value"""


#======================================================================

