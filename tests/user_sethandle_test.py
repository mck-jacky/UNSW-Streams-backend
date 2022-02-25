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


def test_invalid_name_handle_u1():
    """
    Test that provides an invalid name handle as input
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    data = res.json()
    res2 = requests.put(config.url + '/user/profile/sethandle/v1', json={'token': data['token'], 'handle_str': '123_abc'})
    assert res2.status_code == 400

def test_another_invalid_name_handle_u1():
    """
    Test that provides an invalid name handle as input
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    data = res.json()
    res2 = requests.put(config.url + '/user/profile/sethandle/v1', json={'token': data['token'], 'handle_str': '+-.'})
    assert res2.status_code == 400

def test_name_handle_already_in_use_u1():
    """
    Test that tries to cange the email to an already used email; should return Input error
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    data = res.json()
    requests.post(config.url + 'auth/register/v2', json={'email': 'other@mail.au', 'password': 'passwordo', 'name_first': 'Other', 'name_last': 'Other'})
    res2 = requests.put(config.url + '/user/profile/sethandle/v1', json={'token': data['token'], 'handle_str': 'otherother'})
    assert res2.status_code == 400


def test_too_long_name_handle_u1():
    """
    Test that provides a too long name handle as input
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    data = res.json()
    res2 = requests.put(config.url + '/user/profile/sethandle/v1', json={'token': data['token'], 'handle_str': 'abcdefghijklmnopqrstu'})
    assert res2.status_code == 400

def test_too_short_name_handle_u1():
    """
    Test that provides a too short name handle as input
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    data = res.json()
    res2 = requests.put(config.url + '/user/profile/sethandle/v1', json={'token': data['token'], 'handle_str': 'ab'})
    assert res2.status_code == 400


def test_valid_input_for_name_handle_change_u1():
    """
    Test that provides valid input
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Alex', 'name_last': 'Hunter'})
    data = res.json()
    res2 = requests.put(config.url + '/user/profile/sethandle/v1', json={'token': data['token'], 'handle_str': 'abcd'})
    assert res2.status_code == 200




# the following tests are white box tests !!!
'''
def test_valid_input_with_output_u1():
    """
    test that checks the output when valid input was given
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Alex', 'name_last': 'Hunter'})
    data = res.json()
    res2 = requests.put(config.url + '/user/profile/sethandle/v1', json={'token': data['token'], 'handle_str': 'abcd'})
    assert res2.status_code == 200
    x = 0
    z = 1
    for user in data_store.get()['users']:
        if user['name_handle'] == 'abcd':
            x = 1
        if user['name_handle'] == 'alexhunter':
            z = 0
    assert x == 1
    assert z == 1
'''