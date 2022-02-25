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


def test_too_long_name_given_u1():
    """
    Test that provides a too long first name as input
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    data = res.json()
    res2 = requests.put(config.url + '/user/profile/setname/v1', json={'token': data['token'], 'name_first': 'AndyAndyAndyAndyAndyAndyAndyAndyAndyAndyAndyAndyAmy', 'name_last': 'Wu'})
    assert res2.status_code == 400

def test_no_first_name_given_u1():
    """
    Test that has no first name as input
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    data = res.json()
    res2 = requests.put(config.url + '/user/profile/setname/v1', json={'token': data['token'], 'name_first': '', 'name_last': 'Wu'})
    assert res2.status_code == 400

def test_no_last_name_given_u1():
    """
    Test that has no last name as input
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    data = res.json()
    res2 = requests.put(config.url + '/user/profile/setname/v1', json={'token': data['token'], 'name_first': 'Andy', 'name_last': ''})
    assert res2.status_code == 400

def test_valid_input_for_username_change_u1():
    """
    Test that provides valid input
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Alex', 'name_last': 'Hunter'})
    data = res.json()
    res2 = requests.put(config.url + '/user/profile/setname/v1', json={'token': data['token'], 'name_first': 'Alexei', 'name_last': 'Predator'})
    assert res2.status_code == 200






# the following tests is a white box tests !!!
'''
def test_valid_input_with_output_u1():
    """
    test that checks the output when valid input was given
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@mail.au', 'password': 'password', 'name_first': 'Alex', 'name_last': 'Hunter'})
    data = res.json()
    res2 = requests.put(config.url + '/user/profile/setname/v1', json={'token': data['token'], 'name_first': 'Alexei', 'name_last': 'Predator'})
    assert res2.status_code == 200
    """
    x = 0
    z = 1
    for user in data_store.get()['users']:
        if user['name_first'] == 'Alexei' and user['name_last'] == 'Predator':
            x = 1
        if user['name_first'] == 'Alex' and user['name_last'] == 'Hunter':
            z = 0
    assert x == 1
    assert z == 1
    """
'''
