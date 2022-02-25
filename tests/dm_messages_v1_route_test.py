"""
Server route Pytest for the dm_messages_v1() function.
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

    resp = requests.get(config.url + 'dm/messages/v1',
        params = {'token': -1, 'dm_id': [fixList[0]]})
    
    assert(resp.status_code == 403)

def test_valid_user_invalid_dm_id(clear_and_create_new_values):
    """
    1. Register user4.
    2. Try to leave an invalid DM.
    3. Assert that the status code is 400 (InputError)
    """

    user4 = requests.post(config.url + 'auth/register/v2',
        json = {'email': '4@em.com',
                'password': 'password4',
                'name_first': 'NF4',
                'name_last': 'NL4'})
    
    assert(user4.status_code == 200)

    user4_token = json.loads(user4.text)['token']
    
    resp = requests.get(config.url + 'dm/messages/v1',
        params = {'token': user4_token, 'dm_id': -1, 'start': 0})
    
    assert(resp.status_code == 400)

def test_valid_51_messages_return(clear_and_create_new_values):
    """
    1. User1 creates DM with user2.
    2. User1 sends 51 messages to user2.
    3. Assert that the second 50-messages call matches excepted return values.
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
    
    resp2 = requests.post(config.url + 'message/senddm/v1',
        json = {'token': fixList[3], 'dm_id': resp0_text, 'message': "Ghey"})

    assert(resp2.status_code == 200)

    for _ in range(50):
        resp3 = requests.post(config.url + 'message/senddm/v1',
            json = {'token': fixList[3], 'dm_id': resp0_text, 'message': "Ghey"})
        
        assert(resp3.status_code == 200)
    
    # First batch of 50 out of 51
    resp4 = requests.get(config.url + 'dm/messages/v1',
        params = {'token': fixList[3], 'dm_id': resp0_text, 'start': 0})
    
    assert(resp4.status_code == 200)

    # Remaining one message after the first 50
    resp5 = requests.get(config.url + 'dm/messages/v1',
        params = {'token': fixList[3], 'dm_id': resp0_text, 'start': 50})
    
    assert(resp5.status_code == 200)

    resp5_text = json.loads(resp5.text)
    
    """
    expected_return = {'messages': [{'message_id': 1, 'u_id': 1, 'message':
                        'Ghey', 'time_created': SOME_TIME}],
                        'start': 50, 'end': -1}
    """

    assert(resp5_text['messages'][0]['message'] == 'Ghey')
    assert(resp5_text['start'] == 50)
    assert(resp5_text['end'] == -1)

def test_valid_user_start_too_big(clear_and_create_new_values):
    """
    1. User1 creates a DM with user2.
    2. User1 sends one message to user2.
    3. Assert that trying to retrieve 50 messages results in status code 400
       (InputError).
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
    
    resp2 = requests.post(config.url + 'message/senddm/v1',
        json = {'token': fixList[3], 'dm_id': resp0_text, 'message': "Ghey"})

    assert(resp2.status_code == 200)

    resp3 = requests.get(config.url + 'dm/messages/v1',
        params = {'token': fixList[3], 'dm_id': resp0_text, 'start': 50})
    
    assert(resp3.status_code == 400)

def test_valid_parameters_no_dms(clear_and_create_new_values):
    """
    1. User1 creates a DM with user2.
    2. User1 retrieves their own DM with start at zero.
    3. Assert that the return matches the expected return.
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

    resp2 = requests.get(config.url + 'dm/messages/v1',
        params = {'token': fixList[3], 'dm_id': resp0_text, 'start': 0})
    
    assert(resp2.status_code == 200)

    resp2_text = json.loads(resp2.text)

    expected_return = {'messages': [], 'start': 0, 'end': -1}

    assert(resp2_text == expected_return)

def test_valid_parameters_not_member_of_dm(clear_and_create_new_values):
    """
    1. User1 creates a DM with user2.
    2. User3 tries to list the DM messages.
    3. Assert that this raises a status code of 403 (AccessError).
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values

    # 1
    resp0 = requests.post(config.url + 'dm/create/v1',
        json = {'token': fixList[3], 'u_ids': [fixList[1]]})
    
    resp0_text = json.loads(resp0.text)['dm_id']

    assert(resp0.status_code == 200)

    resp1 = requests.get(config.url + 'dm/details/v1',
        params = {'token': fixList[3], 'dm_id': resp0_text})
    
    assert(resp1.status_code == 200)

    # 2
    resp2 = requests.get(config.url + 'dm/messages/v1',
        params = {'token': fixList[5], 'dm_id': resp0_text, 'start': 0})
    
    # 3
    assert(resp2.status_code == 403)
