# Tests for channels/create/v2 route
# Written by Andy Wu z5363503

import pytest
import requests
import json
from src import config

import jwt
# 400 error code (InputError) when any of:
#     - Name of new channel is less than 1 character
#     - Name of new channel is more than 20 characters
#     - Name of new channel is the same name as an existing public/private channel
# 403 error code (AccessError) when any of:
#     - auth_user_id does not belong to any user's id

# TODO: Change auth_user_ids to token

# Clears all data and registers 3 new users with ids 1,2,3 - returns a list of tokens belonging to the users
@pytest.fixture
def clear_and_register():
    requests.delete(config.url + 'clear/v1')
    r1 = requests.post(config.url + 'auth/register/v2', json={'email': 'hellothere@gmail.com', 'password': 'thisismypassword', 'name_first': 'Luke', 'name_last': 'Skywalker'})
    r2 = requests.post(config.url + 'auth/register/v2', json={'email': 'helloagain@gmail.com', 'password': 'newpassword', 'name_first': 'Han', 'name_last': 'Solo'})
    r3 = requests.post(config.url + 'auth/register/v2', json={'email': 'myemail@hotmail.com', 'password': 'insanepassword', 'name_first': 'Anakin', 'name_last': 'Skywalker'})
    r1_token = json.loads(r1.text)['token']
    r2_token = json.loads(r2.text)['token']
    r3_token = json.loads(r3.text)['token']

    return [r1_token, r2_token, r3_token]

# Testing correct json and code output
def test_channels_create_v2_output(clear_and_register):
    resp = requests.post(config.url + 'channels/create/v2', json={'token': clear_and_register[0], 'name': 'Discussions', 'is_public': True})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {'channel_id': 1}

# Testing 403 AccessError code when auth_user_id calling channels_create does not exist
def test_channels_create_v2_no_users():
    # Clear all data to remove all users
    requests.delete(config.url + 'clear/v1')

    resp = requests.post(config.url + 'channels/create/v2', json = {'token': 1, 'name': 'Discussions', 'is_public': True})
    assert resp.status_code == 403

# Testing 1 character channel name 
def test_channels_create_v2_valid_short_name(clear_and_register):
    resp = requests.post(config.url + 'channels/create/v2', json = {'token': clear_and_register[1], 'name': 'K', 'is_public': True})
    assert json.loads(resp.text) == {'channel_id': 1}

# 400 error code (InputError) when user enters an empty name for new channel
def test_channels_create_v2_invalid_no_name(clear_and_register):
    resp = requests.post(config.url + 'channels/create/v2', json = {'token': clear_and_register[2], 'name': '', 'is_public': True})
    assert resp.status_code == 400

# 400 error code (InputError) when user enters name of > 20 character for new channel
def test_channels_create_v2_invalid_long_name(clear_and_register):
    resp = requests.post(config.url + 'channels/create/v2', json = {'token': clear_and_register[2], 'name': 'This is a really long channel name and should be invalid.', 'is_public': True})
    assert resp.status_code == 400

# Testing 20 character channel name
def test_channels_create_v2_invalid_20_char_name(clear_and_register):
    resp = requests.post(config.url + 'channels/create/v2', json = {'token': clear_and_register[2], 'name': 'Abetalipoproteinemia', 'is_public': True})
    assert resp.status_code == 200

# Testing when user enters name of an existing channel
def test_channels_create_v2_existing_channel(clear_and_register):
    resp = requests.post(config.url + 'channels/create/v2', json = {'token': clear_and_register[0], 'name': 'General', 'is_public': True})
    assert json.loads(resp.text) == {'channel_id': 1}

    resp = requests.post(config.url + 'channels/create/v2', json = {'token': clear_and_register[1], 'name': 'Discussions', 'is_public': True})
    assert json.loads(resp.text) == {'channel_id': 2}

    resp = requests.post(config.url + 'channels/create/v2', json = {'token': clear_and_register[2], 'name': 'General', 'is_public': True})
    assert json.loads(resp.text) == {'channel_id': 3}

    resp = requests.post(config.url + 'channels/create/v2', json = {'token': clear_and_register[1], 'name': 'Ideas', 'is_public': True})
    assert json.loads(resp.text) == {'channel_id': 4}

# Testing simple valid cases
def test_channels_create_v2_simple(clear_and_register):
    resp = requests.post(config.url + 'channels/create/v2', json = {'token': clear_and_register[0], 'name': 'General', 'is_public': True})
    assert json.loads(resp.text) == {'channel_id': 1}

    resp = requests.post(config.url + 'channels/create/v2', json = {'token': clear_and_register[1], 'name': 'Discussions', 'is_public': True})
    assert json.loads(resp.text) == {'channel_id': 2}

    resp = requests.post(config.url + 'channels/create/v2', json = {'token': clear_and_register[2], 'name': 'Ideas', 'is_public': True})
    assert json.loads(resp.text) == {'channel_id': 3}

    resp = requests.post(config.url + 'channels/create/v2', json = {'token': clear_and_register[1], 'name': 'Announcements', 'is_public': True})
    assert json.loads(resp.text) == {'channel_id': 4}
