"""
Server route Pytest for the dm_list_v1() function.
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

    resp = requests.get(config.url + 'dm/list/v1',
        params = {'token': -1, 'u_ids': [fixList[0]]})
    
    assert(resp.status_code == 403)

def test_valid_user_no_dms(clear_and_create_new_values):
    """
    1. Register user4.
    2. Assert that the DMs of user4 is empty (expected return).
    """

    user4 = requests.post(config.url + 'auth/register/v2',
        json = {'email': '4@em.com',
                'password': 'password4',
                'name_first': 'NF4',
                'name_last': 'NL4'})
    
    assert(user4.status_code == 200)

    user4_token = json.loads(user4.text)['token']
    
    resp = requests.get(config.url + 'dm/list/v1',
        params = {'token': user4_token})
    
    assert(resp.status_code == 200)
    
    resp_txt = json.loads(resp.text)

    expected_return = {'dms': []}

    assert(resp_txt == expected_return)

def test_retrieve_dm_owners_dm(clear_and_create_new_values):
    """
    1. User1 creates a DM with user2.
    2. Retrieve list of DMs user1 is part of.
    2. Assert that user1 is part of DM with user2 (expected return).
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values
    
    resp0 = requests.post(config.url + 'dm/create/v1',
        json = {'token': fixList[3], 'u_ids': [fixList[1]]})

    assert(resp0.status_code == 200)

    resp1 = requests.get(config.url + 'dm/list/v1',
        params = {'token': fixList[3]})
    
    assert(resp1.status_code == 200)

    expected_return = {'dms': [{'dm_id': 1, 'name': 'nf1nl1, nf2nl2'}]}

    resp1_txt = json.loads(resp1.text)  
    
    assert(resp1_txt == expected_return)

def test_retrieve_dm_members_dm(clear_and_create_new_values):
    """
    1. User1 creates a DM with user2.
    2. Retrieve list of DMs user2 is part of.
    2. Assert that user2 is part of DM with user1 (expected return).
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values
    
    resp0 = requests.post(config.url + 'dm/create/v1',
        json = {'token': fixList[3], 'u_ids': [fixList[1]]})

    assert(resp0.status_code == 200)

    resp1 = requests.get(config.url + 'dm/list/v1',
        params = {'token': fixList[4]})
    
    assert(resp1.status_code == 200)

    expected_return = {'dms': [{'dm_id': 1, 'name': 'nf1nl1, nf2nl2'}]}

    resp1_txt = json.loads(resp1.text)  
    
    assert(resp1_txt == expected_return)

def test_valid_user_not_part_of_any_dms(clear_and_create_new_values):
    """
    1. Register user4.
    2. Create DM between user1 and user2 + user3.
    3. Create DM between user2 and user3.
    3. Assert that the DMs of user4 is empty (expected return).
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values

    resp0 = requests.post(config.url + 'dm/create/v1',
        json = {'token': fixList[3], 'u_ids': [fixList[1], fixList[2]]})

    assert(resp0.status_code == 200)

    resp1 = requests.post(config.url + 'dm/create/v1',
        json = {'token': fixList[4], 'u_ids': [fixList[2]]})

    assert(resp1.status_code == 200)

    resp2 = requests.get(config.url + 'dm/list/v1',
        params = {'token': fixList[3]})
    
    assert(resp2.status_code == 200)

    user4 = requests.post(config.url + 'auth/register/v2',
        json = {'email': '4@em.com',
                'password': 'password4',
                'name_first': 'NF4',
                'name_last': 'NL4'})
    
    assert(user4.status_code == 200)

    user4_token = json.loads(user4.text)['token']
    
    resp3 = requests.get(config.url + 'dm/list/v1',
        params = {'token': user4_token})
    
    assert(resp3.status_code == 200)
    
    resp3_txt = json.loads(resp3.text)

    expected_return = {'dms': []}

    assert(resp3_txt == expected_return)
