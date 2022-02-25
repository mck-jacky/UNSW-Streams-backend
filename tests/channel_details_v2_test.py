# Tests for channel/details/v2 route
# Written by Andy Wu z5363503

import pytest
import requests
import json
from src import config

# 400 error code (InputError) when any of:
#     - channel_id does not refer to a valid channel
# 403 error code (AccessError) when any of:
#     - channel_id is valid but the authorised user is not a member of the channel
#     - auth_user_id does not belong to any user's id

# TODO: Change auth_user_ids to token

# Clears all data and registers 3 users and 3 channels
@pytest.fixture
def clear_and_create_users_and_channels():
    requests.delete(config.url + 'clear/v1')
    r1 = requests.post(config.url + 'auth/register/v2', json={'email': 'hellothere@gmail.com', 'password': 'thisismypassword', 'name_first': 'Luke', 'name_last': 'Skywalker'})
    r2 = requests.post(config.url + 'auth/register/v2', json={'email': 'helloagain@gmail.com', 'password': 'newpassword', 'name_first': 'Han', 'name_last': 'Solo'})
    r3 = requests.post(config.url + 'auth/register/v2', json={'email': 'myemail@hotmail.com', 'password': 'insanepassword', 'name_first': 'Anakin', 'name_last': 'Skywalker'})
    r1_token = json.loads(r1.text)['token']
    r2_token = json.loads(r2.text)['token']
    r3_token = json.loads(r3.text)['token']

    requests.post(config.url + 'channels/create/v2', json={'token': r1_token, 'name': 'General', 'is_public': True})
    requests.post(config.url + 'channels/create/v2', json={'token': r2_token, 'name': 'Discussions', 'is_public': True})
    requests.post(config.url + 'channels/create/v2', json={'token': r3_token, 'name': 'Ideas', 'is_public': False})

    return [r1_token, r2_token, r3_token]

# 400 error code (InputError) - channel_id does not refer to a valid channel
def test_channel_details_v2_invalid_channel_id(clear_and_create_users_and_channels):
    resp = requests.get(config.url + 'channel/details/v2', params={'token': clear_and_create_users_and_channels[0], 'channel_id': 4})
    assert resp.status_code == 400

# 403 error code (AccessError) - auth_user_id does not belong to any user's id
def test_channel_details_v2_invalid_user():
    requests.delete(config.url + 'clear/v1')

    resp = requests.get(config.url + 'channel/details/v2', params={'token': 1, 'channel_id': 2})
    assert resp.status_code == 403
        
# 403 error code (AccessError) - channel_id is valid but the authorised user is not a member of the channel
def test_channel_details_v2_non_member_(clear_and_create_users_and_channels):
    resp = requests.get(config.url + 'channel/details/v2', params={'token': clear_and_create_users_and_channels[0], 'channel_id': 2})
    assert resp.status_code == 403

# Testing simple valid case - No channel_join function used
def test_channel_details_v2_no_join(clear_and_create_users_and_channels):
    resp = requests.get(config.url + 'channel/details/v2', params={'token': clear_and_create_users_and_channels[0], 'channel_id': 1})
    assert json.loads(resp.text) == {
        'name': "General",
        'is_public': True,
        'owner_members': [
            {
                'u_id': 1,
                'email': "hellothere@gmail.com",
                'name_first': "Luke",
                'name_last': "Skywalker",
                'handle_str': "lukeskywalker",
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'email': "hellothere@gmail.com",
                'name_first': "Luke",
                'name_last': "Skywalker",
                'handle_str': "lukeskywalker",
            }
        ]
    }
    resp = requests.get(config.url + 'channel/details/v2', params={'token': clear_and_create_users_and_channels[2], 'channel_id': 3})
    assert json.loads(resp.text) == {
        'name': "Ideas",
        'is_public': False,
        'owner_members': [
            {
                'u_id': 3,
                'email': "myemail@hotmail.com",
                'name_first': "Anakin",
                'name_last': "Skywalker",
                'handle_str': "anakinskywalker",
            }
        ],
        'all_members': [
            {
                'u_id': 3,
                'email': "myemail@hotmail.com",
                'name_first': "Anakin",
                'name_last': "Skywalker",
                'handle_str': "anakinskywalker",
            }
        ]
    }
# @pytest.mark.skip
# Testing simple valid case - channel_join function used
def test_channel_details_v2_join(clear_and_create_users_and_channels):
    requests.post(config.url + 'channel/join/v2', json={'token': clear_and_create_users_and_channels[0], 'channel_id': 2}) # channel_join_v1(1, 2)
    requests.post(config.url + 'channel/join/v2', json={'token': clear_and_create_users_and_channels[2], 'channel_id': 2}) # channel_join_v1(3, 2)

    resp = requests.get(config.url + 'channel/details/v2', params={'token': clear_and_create_users_and_channels[2], 'channel_id': 2})
    assert json.loads(resp.text) == {
        'name': "Discussions",
        'is_public': True,
        'owner_members': [
            {
                'u_id': 2,
                'email': "helloagain@gmail.com",
                'name_first': "Han",
                'name_last': "Solo",
                'handle_str': "hansolo",
            }
        ],
        'all_members': [
            {
                'u_id': 2,
                'email': "helloagain@gmail.com",
                'name_first': "Han",
                'name_last': "Solo",
                'handle_str': "hansolo",
            },
            {
                'u_id': 1,
                'email': "hellothere@gmail.com",
                'name_first': "Luke",
                'name_last': "Skywalker",
                'handle_str': "lukeskywalker",
            },
            {
                'u_id': 3,
                'email': "myemail@hotmail.com",
                'name_first': "Anakin",
                'name_last': "Skywalker",
                'handle_str': "anakinskywalker",
            }
        ]
    }
