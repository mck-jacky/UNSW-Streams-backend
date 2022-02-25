import pytest

from src.auth import auth_register_v1
from src.data_store import data_store
from src.other import clear_v1, is_valid_token, decrypt_token
from src.error import InputError
from flask import Flask, request
from json import dumps
import time

import jwt
import requests
import json
from src import config

SUPERSECRETPASSWORD = "StampsWithAlpacas"


def test_logout_with_valid_input():
    """
    Test that provides valid input
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Alex', 'name_last': 'Hunter'})
    data = res.json()
    res2 = requests.post(config.url + '/auth/logout/v1', json={'token': data['token']})
    assert res2.status_code == 200



def test_logout_and_try_to_perform_other_action_with_that_token_afterwards():
    """
    Test that provides valid input and then tries to perform another action
    with the same now invalid token
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Alex', 'name_last': 'Hunter'})
    data = res.json()
    res2 = requests.post(config.url + '/auth/logout/v1', json={'token': data['token']})
    assert res2.status_code == 200
    res3 = requests.put(config.url + '/user/profile/setemail/v1', json={'token': data['token'], 'email': 'other@mail.com'})
    assert res3.status_code == 403

'''
def test_logout_with_invalid_token():
    """
    Test that checks if the token is valid and active
    """
    requests.delete(config.url + 'clear/v1')
    requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    res = requests.post(config.url + '/auth/logout/v1', json={'token': 'aaa111'})
    assert res.status_code == 403



# the following tests are white box tests !!!

def test_valid_input_with_output_logout():
    """
    test that checks the output when valid input was given
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Alex', 'name_last': 'Hunter'})
    data = res.json()
    decoded_token = decrypt_token(data['token'])
    
    res2 = requests.post(config.url + '/auth/logout/v1', json={'token': data['token']})
    assert res2.status_code == 200
    x = 1
    for user in data_store.get()['users']:
        if user['auth_user_id'] == decoded_token['auth_user_id']:
            for session_id in user['session_ids']:
                if session_id == decoded_token['session_id']:
                    x = 0
    assert x == 1
'''


def test_check_manually_created_invalid_token_sethandle_logout():
    """
    Test that checks if the token is valid and active; test should raise an
    access error because the token has an invalid session idea
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Alex', 'name_last': 'Hunter'})
    data = res.json()
    
    requests.post(config.url + '/auth/logout/v1', json={'token': data['token']})
    token = jwt.encode({'auth_user_id': '1', 'session_id': '1'}, SUPERSECRETPASSWORD, algorithm="HS256")
    res = requests.put(config.url + '/user/profile/sethandle/v1', json={'token': token, 'handle_str': 'abcd'})
    assert res.status_code == 403
