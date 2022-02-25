"""
Server route Pytest for the channels_listall_v1() function.
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

    resp = requests.get(config.url + 'channels/listall/v2',
        params = {'token': -1, 'u_ids': [fixList[0]]})
    
    assert(resp.status_code == 403)

def test_valid_user_list_all_channels(clear_and_create_new_values):
    """
    1. User1 creates two channels.
    2. User1 wants to list all available channels.
    3. Assert return value matches the expected return.
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values

    resp0 = requests.post(config.url + 'channels/create/v2',
        json = {'token': fixList[3],
                'name': 'Channel1',
                'is_public': True
                })

    assert(resp0.status_code == 200)

    resp1 = requests.post(config.url + 'channels/create/v2',
        json = {'token': fixList[3],
                'name': 'Channel2',
                'is_public': True
                })
    
    assert(resp1.status_code == 200)

    resp2 = requests.get(config.url + 'channels/listall/v2',
        params = {'token': fixList[3],
                  'name': 'Channel1',
                  'is_public': True
                  })

    assert(resp2.status_code == 200)

    resp2_text = json.loads(resp2.text)
    
    expected_return = {'channels': [{'channel_id': 1, 'name': 'Channel1'},
                      {'channel_id': 2, 'name': 'Channel2'}]}
    
    assert(resp2_text == expected_return)

def test_valid_user_no_channels(clear_and_create_new_values):
    """
    1. User1 wants to list all available channels, even though none have been
       created.
    2. Assert return value matches the expected return.
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values

    resp = requests.get(config.url + 'channels/listall/v2',
        params = {'token': fixList[4],
                  'name': 'Channel1',
                  'is_public': True
                  })

    assert(resp.status_code == 200)

    resp_text = json.loads(resp.text)
    
    expected_return = {'channels': []}
    
    assert(resp_text == expected_return)
