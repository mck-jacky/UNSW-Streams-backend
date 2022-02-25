# Tests for users/all/v1 route
# Written by Andy Wu z5363503

import pytest
import requests
import json
from src import config

# AccessError when any of: 
#     - auth_user_id is invalid

# TODO: Change auth_user_ids to token

# Clears and registers 3 new users
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

# Testing simple case
def test_simple(clear_and_register):
    resp = requests.get(config.url + 'users/all/v1', params={'token': clear_and_register[0]})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {'users': [
        {
            'u_id': 1,
            'email': "hellothere@gmail.com",
            'name_first': "Luke",
            'name_last': "Skywalker",
            'handle_str': "lukeskywalker",
        },
        {
            'u_id': 2,
            'email': "helloagain@gmail.com",
            'name_first': "Han",
            'name_last': "Solo",
            'handle_str': "hansolo",
        },
        {
            'u_id': 3,
            'email': "myemail@hotmail.com",
            'name_first': "Anakin",
            'name_last': "Skywalker",
            'handle_str': "anakinskywalker",
        }
    ]}

# 403 error code (AccessError) - auth_user_id does not belong to any user's id
def test_invalid_auth_id(clear_and_register):
    resp = requests.get(config.url + 'users/all/v1', params={'token': 4})
    assert resp.status_code == 403

# Testing when there are no users
def test_no_users():
    requests.delete(config.url + 'clear/v1')

    resp = requests.get(config.url + 'users/all/v1', params={'token': 1})
    assert resp.status_code == 403

# Testing when there is only 1 user
def test_only_one_user():
    requests.delete(config.url + 'clear/v1')
    r1 = requests.post(config.url + 'auth/register/v2', json={'email': 'hellothere@gmail.com', 'password': 'thisismypassword', 'name_first': 'Luke', 'name_last': 'Skywalker'})
    r1_token = json.loads(r1.text)['token']
    resp = requests.get(config.url + 'users/all/v1', params={'token': r1_token})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {'users': [
        {
            'u_id': 1,
            'email': "hellothere@gmail.com",
            'name_first': "Luke",
            'name_last': "Skywalker",
            'handle_str': "lukeskywalker",
        }
    ]}
