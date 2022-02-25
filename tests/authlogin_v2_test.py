import pytest
import hashlib
import jwt
import requests
import json

from src.auth import auth_register_v1
from src.auth import auth_login_v1
from src.other import clear_v1
from src.error import InputError
from json import dumps
from src import config

SUPERSECRETPASSWORD = "StampsWithAlpacas"


def test_login_wrong_password_v2():
    """
    The test function tries to login a user, who entered a wrong password.
    """
    requests.delete(config.url + 'clear/v1')
    requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    response = requests.post(config.url + 'auth/login/v2', json={'email': 'sample@gmail.au', 'password': 'passwordo'})
    
    assert response.status_code == 400


def test_login_without_account_v2():
    """
    The test function tries to login a user, even though no account exists.
    """
    requests.delete(config.url + 'clear/v1')
    response = requests.post(config.url + 'auth/login/v2', json={'email': 'sample@gmail.au', 'password': 'password'})
    assert response.status_code == 400

def test_login_with_other_users_password_v2():
    """
    The test function tries to login a user, who uses the password of a
    different user.
    """
    requests.delete(config.url + 'clear/v1')
    requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    requests.post(config.url + 'auth/register/v2', json={'email': 'other@gmail.au', 'password': 'passwordo', 'name_first': 'Other', 'name_last': 'Other'})
    response = requests.post(config.url + 'auth/login/v2', json={'email': 'sample@gmail.au', 'password': 'passwordo'})
    assert response.status_code == 400

def test_login_without_password_v2():
    """
    The test function tries to login a user, who did not enter a password.
    """
    requests.delete(config.url + 'clear/v1')
    requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    response = requests.post(config.url + 'auth/login/v2', json={'email': 'sample@gmail.au', 'password': ''})
    assert response.status_code == 400

def test_login_without_email_v2():
    """
    The test function tries to login a user, who did not enter his/her email.
    """
    requests.delete(config.url + 'clear/v1')
    requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    response = requests.post(config.url + 'auth/login/v2', json={'email': '', 'password': 'password'})
    assert response.status_code == 400

def test_valid_auth_login_input_v2():
    """
    The test function logs in a user, who entered valid input.
    """
    requests.delete(config.url + 'clear/v1')
    requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    response = requests.post(config.url + 'auth/login/v2', json={'email': 'sample@gmail.au', 'password': 'password'})
    assert response.status_code == 200

def test_valid_auth_login_with_two_consecutive_logins_v2():
    """
    The same user logs in twice with the same valid input.
    """
    requests.delete(config.url + 'clear/v1')
    requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    response = requests.post(config.url + 'auth/login/v2', json={'email': 'sample@gmail.au', 'password': 'password'})
    response2 = requests.post(config.url + 'auth/login/v2', json={'email': 'sample@gmail.au', 'password': 'password'})
    body = response.json()
    body2 = response2.json()
    assert body['token'] != body2['token']
    assert response.status_code == 200
    assert response2.status_code == 200

def test_valid_auth_login_with_two_logins_with_different_accounts_v2():
    """
    The test function logs in two user consecutively.
    """
    requests.delete(config.url + 'clear/v1')
    requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    requests.post(config.url + 'auth/register/v2', json={'email': 'other@gmail.au', 'password': 'passwordo', 'name_first': 'Other', 'name_last': 'Other'})
    response = requests.post(config.url + 'auth/login/v2', json={'email': 'sample@gmail.au', 'password': 'password'})
    response2 = requests.post(config.url + 'auth/login/v2', json={'email': 'other@gmail.au', 'password': 'passwordo'})
    body = response.json()
    body2 = response2.json()
    assert body['token'] != body2['token']
    assert response.status_code == 200
    assert response2.status_code == 200







### The following function is a white box test !!!

def test_valid_auth_login_input_with_output_v2():
    """
    The test function logs in a user, who entered valid input and compares the output.
    """
    requests.delete(config.url + 'clear/v1')
    requests.post(config.url + 'auth/register/v2', json={'email': 'sample@gmail.au', 'password': 'password', 'name_first': 'Name', 'name_last': 'Name'})
    response = requests.post(config.url + 'auth/login/v2', json={'email': 'sample@gmail.au', 'password': 'password'})

    data = response.json()

    assert data['token'] == jwt.encode({'auth_user_id': '1', 'session_id': '2'}, SUPERSECRETPASSWORD, algorithm="HS256")
    assert response.status_code == 200
