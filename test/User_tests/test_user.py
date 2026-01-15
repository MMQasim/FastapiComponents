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

def user_profile_test_case(client,token:str):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    return data

#======================================================================

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



#======================================================================
# Test Cases

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
def test_user_profile_route(client,identifier_type, identifier):
    tokens = login_test_case(client,{'identifier': identifier, 'identifier_type': identifier_type, 'password': PASSWORD if identifier_type != "google" else None})
    user_data = user_profile_test_case(client,tokens['access_token'])
    user_data_keys = user_data.keys()
    if identifier_type in user_data_keys:
        assert user_data[identifier_type] == identifier
    else:
        assert user_data['user_id'] == identifier

#======================================================================

