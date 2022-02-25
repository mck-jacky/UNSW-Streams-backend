"""
Server route Pytest for the dm_details_v1() function.
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

    resp = requests.get(config.url + 'dm/details/v1',
        params = {'token': -1, 'dm_id': [fixList[0]]})
    
    assert(resp.status_code == 403)

def test_valid_user_no_dms(clear_and_create_new_values):
    """
    1. Register user4.
    2. Try to remove an invalid DM.
    3. Assert that the status code is 400 (InputError)
    """

    user4 = requests.post(config.url + 'auth/register/v2',
        json = {'email': '4@em.com',
                'password': 'password4',
                'name_first': 'NF4',
                'name_last': 'NL4'})
    
    assert(user4.status_code == 200)

    user4_token = json.loads(user4.text)['token']
    
    resp = requests.get(config.url + 'dm/details/v1',
        params = {'token': user4_token, 'dm_id': -1})
    
    assert(resp.status_code == 400)

def test_valid_user_one_dm(clear_and_create_new_values):
    """
    1. User1 creates DM with user2.
    2. Assert that response equals expected return.
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values

    resp0 = requests.post(config.url + 'dm/create/v1',
        json = {'token': fixList[3], 'u_ids': [fixList[1]]})
    
    resp0_text = json.loads(resp0.text)['dm_id']

    assert(resp0.status_code == 200)
    
    resp1 = requests.get(config.url + 'dm/details/v1',
        params = {'token': fixList[3], 'dm_id': resp0_text})
    
    assert(resp1.status_code == 200)

    resp1_text = json.loads(resp1.text)
    
    expected_return = {
        'name': 'nf1nl1, nf2nl2',
        'members': [
            {
                'u_id': 1,
                'email': '1@em.com',
                'name_first': 'NF1',
                'name_last': 'NL1',
                'handle_str': 'nf1nl1'
            },
            {
                'u_id': 2,
                'email': '2@em.com',
                'name_first': 'NF2',
                'name_last': 'NL2',
                'handle_str': 'nf2nl2'
            }
        ]
    }

    assert(resp1_text == expected_return)

def test_valid_user_not_part_of_dm(clear_and_create_new_values):
    """
    1. User1 creates DM with user2.
    2. User3 tries to get the details of user1-user2 DM.
    2. Assert that the response status code is 403 (AccessError).
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values

    resp0 = requests.post(config.url + 'dm/create/v1',
        json = {'token': fixList[3], 'u_ids': [fixList[1]]})
    
    resp0_text = json.loads(resp0.text)['dm_id']

    assert(resp0.status_code == 200)
    
    resp1 = requests.get(config.url + 'dm/details/v1',
        params = {'token': fixList[5], 'dm_id': resp0_text})
    
    assert(resp1.status_code == 403)
