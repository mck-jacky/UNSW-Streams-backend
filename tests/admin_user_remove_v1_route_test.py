"""
Server route Pytest for the admin_user_remove_v1() function.
"""

import json
import pytest
import requests
from src import config

GLOBAL_OWNER = 1
GLOBAL_MEMBER = 2

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
    Test whether an invalid token raises an AccessError.
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values

    resp = requests.delete(config.url + 'admin/user/remove/v1',
        json = {'token': -1, 'u_ids': [fixList[1]]})
    
    assert(resp.status_code == 403)

def test_not_a_global_owner(clear_and_create_new_values):
    """
    Test whether a valid user, who is not a global owner, and tries to remove a
    user, raises an AccessError.
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values

    resp = requests.delete(config.url + 'admin/user/remove/v1',
        json = {'token': fixList[4], 'u_id': fixList[2]})

    assert(resp.status_code == 403)

def test_global_owner_removing_himself(clear_and_create_new_values):
    """
    Test whether the only valid global owner left can remove himself. Should
    raise an InputError.
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values

    resp = requests.delete(config.url + 'admin/user/remove/v1',
        json = {'token': fixList[3], 'u_id': fixList[0]})

    assert(resp.status_code == 400)

def test_simple_user_removal_then_retrieve_profile(clear_and_create_new_values):
    """
    1. Global owner user1 removing user2.
    2. Assert user2's profile matches the expected return.
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values

    # 1
    resp0 = requests.delete(config.url + 'admin/user/remove/v1',
        json = {'token': fixList[3], 'u_id': fixList[1]})

    assert(resp0.status_code == 200)
    
    resp1 = requests.get(config.url + 'user/profile/v1',
        params = {'token': fixList[3], 'u_id': fixList[1]})
    
    assert(resp1.status_code == 200)

    # 2
    resp_txt = json.loads(resp1.text)

    expected_return = {'user': {'u_id': fixList[1],
                        'email': '',
                        'name_first': 'Removed',
                        'name_last': 'user',
                        'handle_str': ''}}

    # Assert that the removed user's details have been removed
    assert(resp_txt == expected_return)

def test_add_another_global_owner_then_remove(clear_and_create_new_values):
    """
    1. User1 is the first global owner.
    2. Have user1 set user2 (global member) as another global owner.
    3. Have user1 remove user2.
    4. Assert user2 (as a global owner) is able to be removed.
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values

    # 2
    resp0 = requests.post(config.url + 'admin/userpermission/change/v1',
            json = {'token': fixList[3],
                    'u_id': fixList[2],
                    'permission_id': GLOBAL_OWNER}) 

    assert(resp0.status_code == 200)

    # 3
    resp1 = requests.delete(config.url + 'admin/user/remove/v1',
        json = {'token': fixList[3], 'u_id': fixList[1]})

    assert(resp1.status_code == 200)

    # 4
    resp2 = requests.get(config.url + 'user/profile/v1',
        params = {'token': fixList[3], 'u_id': fixList[1]})
    
    assert(resp1.status_code == 200)

    # Profile of removed user
    resp2_txt = json.loads(resp2.text)

    expected_return = {'user': {'u_id': fixList[1],
                        'email': '',
                        'name_first': 'Removed',
                        'name_last': 'user',
                        'handle_str': ''}}

    # Assert that the removed user's details have been removed
    assert(resp2_txt == expected_return)

def test_invalid_user_to_remove(clear_and_create_new_values):
    """
    Test whether a global owner removing a non-existent user (invalid u_id) will
    return a status code 400 (InputError).
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values

    # 1
    resp0 = requests.delete(config.url + 'admin/user/remove/v1',
        json = {'token': fixList[3], 'u_id': -1})

    assert(resp0.status_code == 400)
    
def test_complete_removal(clear_and_create_new_values):
    """
    Test whether a global owner (user1) removing a global member (user2) who is:
    - part of a channel
    - part of a DM

    1. User2 creates a channel.
    2. User2 sends a message in the channel.
    3. User2 creates a DM with user3.
    4. User2 sends a DM to user3.
    5. User1 removes user2.
    6. Assert removed user2's profile matches expected return.
    7. Assert removed user2's channel matches expected return.
    8. Assert removed user2's DM raises a 403 status code (AccessError).

    Created users 4 and 5 are just to add noise (i.e. trying to increase
    coverage).
    """

    # [user1_id, user2_id, user3_id, user1_token, user2_token, user3_token]
    # [1, 2, 3, token1, token2, token3]
    fixList = clear_and_create_new_values

    # user4 and user5 #####################
    user4 = requests.post(config.url + 'auth/register/v2',
        json = {'email': '4@em.com',
                'password': 'password4',
                'name_first': 'NF4',
                'name_last': 'NL4'})
    
    user5 = requests.post(config.url + 'auth/register/v2',
        json = {'email': '5@em.com',
                'password': 'password5',
                'name_first': 'NF5',
                'name_last': 'NL5'})
    
    assert(user4.status_code == 200)
    assert(user5.status_code == 200)

    user5_id = json.loads(user5.text)['auth_user_id']
    user4_token = json.loads(user4.text)['token']
    
    resp_user4_c = requests.post(config.url + 'channels/create/v2',
        json = {'token': user4_token,
                'name': 'Channel4',
                'is_public': True})

    assert(resp_user4_c.status_code == 200)

    resp_user4_c_text = json.loads(resp_user4_c.text)['channel_id']

    resp_user4_cm = requests.post(config.url + 'message/send/v1',
        json = {'token': user4_token,
                'channel_id': resp_user4_c_text,
                'message': "ChannelTest"})

    assert(resp_user4_cm.status_code == 200)

    resp_user4_d = requests.post(config.url + 'dm/create/v1',
        json = {'token': user4_token,
                'u_ids': [user5_id]})

    assert(resp_user4_d.status_code == 200)

    resp_user4_d_text = json.loads(resp_user4_d.text)['dm_id']

    resp_user4_dm = requests.post(config.url + 'message/senddm/v1',
        json = {'token': user4_token,
                'dm_id': resp_user4_d_text,
                'message': "DMTest"})
    
    assert(resp_user4_dm.status_code == 200)
    
    #######################################

    # 1
    resp0 = requests.post(config.url + 'channels/create/v2',
        json = {'token': fixList[4],
                'name': 'Channel1',
                'is_public': True})

    assert(resp0.status_code == 200)

    # Get the channel_id
    resp0_txt = json.loads(resp0.text)['channel_id']
    
    # 2
    resp1 = requests.post(config.url + 'message/send/v1',
        json = {'token': fixList[4],
                'channel_id': resp0_txt,
                'message': "ChannelTest"})

    assert(resp1.status_code == 200)

    # 3
    resp2 = requests.post(config.url + 'dm/create/v1',
        json = {'token': fixList[4],
                'u_ids': [fixList[2]]})

    assert(resp2.status_code == 200)

    # Get the dm_id
    resp2_txt = json.loads(resp2.text)['dm_id']

    # 4
    resp3 = requests.post(config.url + 'message/senddm/v1',
        json = {'token': fixList[4],
                'dm_id': resp2_txt,
                'message': "DMTest"})
    
    assert(resp3.status_code == 200)

    # 5
    resp4 = requests.delete(config.url + 'admin/user/remove/v1',
        json = {'token': fixList[3], 'u_id': fixList[1]})

    assert(resp4.status_code == 200)

    # 6
    resp5 = requests.get(config.url + 'user/profile/v1',
        params = {'token': fixList[3], 'u_id': fixList[1]})
    
    assert(resp5.status_code == 200)

    # Profile of removed user
    resp5_txt = json.loads(resp5.text)

    expected_return_1 = {'user': {'u_id': fixList[1],
                            'email': '',
                            'name_first': 'Removed',
                            'name_last': 'user',
                            'handle_str': ''}}

    # Assert that the removed user's details have been removed
    assert(resp5_txt == expected_return_1)

    # 7
    resp6 = requests.get(config.url + 'channels/list/v2',
        params = {'token': fixList[3], 'u_id': fixList[1]})

    assert(resp6.status_code == 200)

    resp6_text = json.loads(resp6.text)

    expected_return_2 = {'channels': []}

    assert(resp6_text == expected_return_2)

    # 8
    resp7 = requests.get(config.url + 'dm/list/v1',
            params = {'token': fixList[4]})

    assert(resp7.status_code == 403)
