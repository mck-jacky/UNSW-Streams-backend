"""
Server route Pytest for the dm_remove_v1() function.
"""

import json
import pytest
import requests
from src import config

@pytest.fixture
def clear_and_create_new_values():
    """
    1. Clears all existing details in data_store.
    2. Creates three new users.
    3. Extracts all three users' tokens.
    """

    requests.delete(config.url + 'clear/v1')

    user1 = requests.post(config.url + 'auth/register/v2',
        json = {'email': '1@em.com',
                'password': 'password1',
                'name_first': 'NF1',
                'name_last': 'NL1'})
    
    user2 = requests.post(config.url + 'auth/register/v2',
        json = {'email': '2@em.com',
                'password': 'password2',
                'name_first': 'NF2',
                'name_last': 'NL2'})
    
    user3 = requests.post(config.url + 'auth/register/v2',
        json = {'email': '3@em.com',
                'password': 'password3',
                'name_first': 'NF3',
                'name_last': 'NL3'})
    
    user1_id = json.loads(user1.text)['auth_user_id']
    user2_id = json.loads(user2.text)['auth_user_id']
    user3_id = json.loads(user3.text)['auth_user_id']

    user1_token = json.loads(user1.text)['token']
    user2_token = json.loads(user2.text)['token']
    user3_token = json.loads(user3.text)['token']
    
    # [1, 2, 3, token1, token2, token3]
    return [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]

def test_invalid_token(clear_and_create_new_values):
    """
    1. Assert an AccessError is raised with an invalid token.
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values

    resp = requests.delete(config.url + 'dm/remove/v1',
        json = {'token': -1, 'dm_id': [fixList[0]]})
    
    assert(resp.status_code == 403)

def test_valid_user_not_valid_dm(clear_and_create_new_values):
    """
    1. Register user4.
    2. Try to remove an invalid DM.
    3. Assert that the status code is 400 (InputError)
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values

    user4 = requests.post(config.url + 'auth/register/v2',
        json = {'email': '4@em.com',
                'password': 'password4',
                'name_first': 'NF4',
                'name_last': 'NL4'})
    
    assert(user4.status_code == 200)

    user4_token = json.loads(user4.text)['token']
    
    resp = requests.delete(config.url + 'dm/remove/v1',
        json = {'token': user4_token, 'dm_id': fixList[0]})
    
    assert(resp.status_code == 400)

def test_valid_user_is_owner_of_dm(clear_and_create_new_values):
    """
    1. User1 creates DM with user2.
    2. User2 creates DM with user3.
    3. User1 lists DM with user2.
    4. User1 removes DM with user2.
    5. User1 attempts to remove DM with user2 again.
    6. Assert that the DM has been removed by trying to remove the same DM again
       (should raise a 400 status code (InputError)).
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values
    
    # 1
    resp0 = requests.post(config.url + 'dm/create/v1',
        json = {'token': fixList[3], 'u_ids': [fixList[1]]})
    
    assert(resp0.status_code == 200)
    
    resp0_txt = json.loads(resp0.text)['dm_id']  # dm_id

    # 2
    resp9 = requests.post(config.url + 'dm/create/v1',
        json = {'token': fixList[4], 'u_ids': [fixList[2]]})
    
    assert(resp9.status_code == 200)

    # 3
    resp1 = requests.get(config.url + 'dm/list/v1',
        params = {'token': fixList[3]})

    assert(resp1.status_code == 200)

    # 4
    resp2 = requests.delete(config.url + 'dm/remove/v1',
        json = {'token': fixList[3], 'dm_id': resp0_txt})

    assert(resp2.status_code == 200)

    # 5
    resp3 = requests.delete(config.url + 'dm/remove/v1',
        json = {'token': fixList[3], 'dm_id': resp0_txt})
    
    # 6
    assert(resp3.status_code == 400)

def test_valid_user_is_not_owner_of_dm(clear_and_create_new_values):
    """
    1. User1 creates DM with user2.
    2. User2 creates DM with user3.
    3. User1 lists DM with user2.
    4. User2 tries to remove user1's DM.
    5. Assert that the DM has been removed by trying to remove the same DM again
       (should raise a 403 status code (AccessError)).
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values
    
    # 1
    resp0 = requests.post(config.url + 'dm/create/v1',
        json = {'token': fixList[3], 'u_ids': [fixList[1]]})
    
    assert(resp0.status_code == 200)
    
    resp0_txt = json.loads(resp0.text)['dm_id']  # dm_id

    # 2
    resp9 = requests.post(config.url + 'dm/create/v1',
        json = {'token': fixList[4], 'u_ids': [fixList[2]]})
    
    assert(resp9.status_code == 200)

    # 3
    resp1 = requests.get(config.url + 'dm/list/v1',
        params = {'token': fixList[3]})

    assert(resp1.status_code == 200)

    # 4
    resp2 = requests.delete(config.url + 'dm/remove/v1',
        json = {'token': fixList[4], 'dm_id': resp0_txt})

    # 5
    assert(resp2.status_code == 403)

def test_create_remove_create_dm(clear_and_create_new_values):
    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values

    # User1 creates DM with user2
    resp0 = requests.post(config.url + 'dm/create/v1',
        json = {'token': fixList[3], 'u_ids': [fixList[1]]})

    # dm_id of first create
    resp0_text = json.loads(resp0.text)['dm_id']
    
    # Remove 1st DM
    requests.delete(config.url + 'dm/remove/v1',
        json = {'token': fixList[3], 'dm_id': resp0_text})
    
    # User1 creates DM with user2 AGAIN
    resp2 = requests.post(config.url + 'dm/create/v1',
        json = {'token': fixList[3], 'u_ids': [fixList[1]]})

    # dm_id of second create
    resp2_text = json.loads(resp2.text)['dm_id']

    assert(resp0_text != resp2_text)
