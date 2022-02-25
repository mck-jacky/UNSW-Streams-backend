# Tests for the dm/create/v1 route
# Written by Andy Wu z5363503

import pytest
import requests
import json
from src import config

# TODO: Replace auth_user_id with token

# InputError when any of:
#     - Occurs when any u_id in u_ids does not refer to a valid user
# AccessError when any of:
#     - auth_user_id does not belong to any user's id

# Clears list of users, channels and dms, registers 3 new users
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

# Testing each member creating a dm with the other users
def test_simple(clear_and_register):
    resp = requests.post(config.url + 'dm/create/v1', json={'token': clear_and_register[0], 'u_ids': [2,3]})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {'dm_id': 1}

    resp = requests.post(config.url + 'dm/create/v1', json={'token': clear_and_register[1], 'u_ids': [1,3]})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {'dm_id': 2}

    resp = requests.post(config.url + 'dm/create/v1', json={'token': clear_and_register[2], 'u_ids': [1,2]})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {'dm_id': 3}

    resp = requests.post(config.url + 'dm/create/v1', json={'token': clear_and_register[2], 'u_ids': [1]})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {'dm_id': 4}

# Test creation of dm with a list of no ids
def test_one_member(clear_and_register):
    resp = requests.post(config.url + 'dm/create/v1', json={'token': clear_and_register[0], 'u_ids': []})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {'dm_id': 1}

# Test repeated creation of dms with a list of no ids
def test_one_member_repeat(clear_and_register):
    resp = requests.post(config.url + 'dm/create/v1', json={'token': clear_and_register[0], 'u_ids': []})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {'dm_id': 1}

    resp = requests.post(config.url + 'dm/create/v1', json={'token': clear_and_register[0], 'u_ids': []})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {'dm_id': 2}

    resp = requests.post(config.url + 'dm/create/v1', json={'token': clear_and_register[0], 'u_ids': []})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {'dm_id': 3}

# Raise 400 error code (InputError) when a u_id in given list is invalid
def test_invalid_user(clear_and_register):
    resp = requests.post(config.url + 'dm/create/v1', json={'token': clear_and_register[0], 'u_ids': [2,3,4]})
    assert resp.status_code == 400

# Raise 400 error code (InputError) when all u_ids in given list is invalid
def test_all_invalid_user(clear_and_register):
    resp = requests.post(config.url + 'dm/create/v1', json={'token': clear_and_register[0], 'u_ids': [4,5,6]})
    assert resp.status_code == 400

# Raise 403 error code (AccessError) when auth_user_id is invalid
def test_invalid_auth_id(clear_and_register):
    resp = requests.post(config.url + 'dm/create/v1', json={'token': 4, 'u_ids': [1,2,3]})
    assert resp.status_code == 403

# Test repeated creations of same dms but each have unique id
def test_repeat_create(clear_and_register):
    resp = requests.post(config.url + 'dm/create/v1', json={'token': clear_and_register[0], 'u_ids': [2,3]})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {'dm_id': 1}

    resp = requests.post(config.url + 'dm/create/v1', json={'token': clear_and_register[0], 'u_ids': [2,3]})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {'dm_id': 2}

    resp = requests.post(config.url + 'dm/create/v1', json={'token': clear_and_register[0], 'u_ids': [2,3]})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {'dm_id': 3}

    resp = requests.post(config.url + 'dm/create/v1', json={'token': clear_and_register[0], 'u_ids': [2,3]})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {'dm_id': 4}
