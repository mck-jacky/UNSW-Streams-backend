import pytest

from src.auth import auth_register_v1
from src.data_store import data_store
from src.other import clear_v1
from src.error import InputError
from flask import Flask, request
from json import dumps
import time

import jwt
import requests
import json
from src import config

SUPERSECRETPASSWORD = "StampsWithAlpacas"


def test_auth_register_invalid_email_v2():
    """
    The test function uses an email address without '@'.
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'aaa', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    assert res.status_code == 400


def test_auth_register_other_invalid_email_v2():
    """
    The test function uses an email address without domain '.ending'.
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    assert res.status_code == 400

def test_auth_register_another_invalid_email_v2():
    """
    The test function uses an email address without domain 'ending'.
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    assert res.status_code == 400

def test_register_duplicate_email_v2():
    """
    The test function tries to register a second user with an already used 
    email address.
    """
    requests.delete(config.url + 'clear/v1')
    requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': 'Other', 'name_last': 'Other'})
    assert res.status_code == 400

def test_too_short_password_v2():
    """
    The test function uses a password, which is only 5 chars long.
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'passw', 'name_first': 'Name', 'name_last': 'Name'})
    assert res.status_code == 400

def test_too_long_name_v2():
    """
    The test function uses a family name that is too long.
    """
    requests.delete(config.url + 'clear/v1')                                                                                                                 # these are exactly 51 chars
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Namenamenamenamenamenamenamenamenamenamenamenamenam'})
    assert res.status_code == 400

def test_no_first_name_given_v2():
    """
    The test function uses an empty string for the first name.
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': '', 'name_last': 'Name'})
    assert res.status_code == 400


def test_no_family_name_given_v2():
    """
    The test function uses an empty string for the last name.
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': 'Name', 'name_last': ''})
    assert res.status_code == 400


def test_valid_auth_register_input_v2():
    """
    #Test function uses valid input to register 2 users.
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    res2 = requests.post(config.url + 'auth/register/v2', json={'email': 'other@gmail.au', 'password': 'password', 'name_first': 'Other', 'name_last': 'Other'})
    assert res.status_code == 200
    assert res2.status_code == 200
    
    body = res.json()
    body2 = res2.json()
    assert body['auth_user_id'] != body2['auth_user_id']

def test_valid_auth_register_inputs_with_ints_v2():
    """
    Test function uses valid input to register a user.
    The input is mostly composed of numbers.
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    assert res.status_code == 200

def test_extra_long_name_to_increase_code_coverage_v2():
    """
    Test function provides a long name that needs to be cut to from the name
    handle.
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': 'Andyandyandyandyandy', 'name_last': 'Name'})
    assert res.status_code == 200

def test_register_multiple_users_that_have_the_same_name_handle_v2():
    """
    Test function registers multiple users with the same name, so the name
    handle has to increment.
    """
    requests.delete(config.url + 'clear/v1')
    res = requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    assert res.status_code == 200
    res2 = requests.post(config.url + 'auth/register/v2', json={'email': 'sampl@gmail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    assert res2.status_code == 200
    res3 = requests.post(config.url + 'auth/register/v2', json={'email': 'sampe@gmail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    assert res3.status_code == 200
    