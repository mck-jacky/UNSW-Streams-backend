# A file to test the message_unreact route. Written by Jacky Ma z5336759, Nov 2021

SUCCESS = 200
INPUT_ERROR = 400
ACCESS_ERROR = 403

import pytest
import requests
import json
from src import config
import jwt
import src.other

from tests.fixtures import jacky_init

LIKE = 1

def test_message_id_invalid(jacky_init):
    resp = requests.post(config.url + 'message/unreact/v1', json={'token': jacky_init["token"][3], 'message_id': jacky_init["messages"][1], 'react_id': LIKE})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/unreact/v1', json={'token': jacky_init["token"][3], 'message_id': jacky_init["messages"][2], 'react_id': LIKE})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/unreact/v1', json={'token': jacky_init["token"][3], 'message_id': jacky_init["messages"][3], 'react_id': LIKE})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/unreact/v1', json={'token': jacky_init["token"][3], 'message_id': jacky_init["messages"][4], 'react_id': LIKE})
    assert resp.status_code == INPUT_ERROR

def test_invalid_react_id(jacky_init):
    resp = requests.post(config.url + 'message/unreact/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][1], 'react_id': 2})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/unreact/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][2], 'react_id': 3})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/unreact/v1', json={'token': jacky_init["token"][2], 'message_id': jacky_init["messages"][3], 'react_id': 4})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/unreact/v1', json={'token': jacky_init["token"][2], 'message_id': jacky_init["messages"][4], 'react_id': 5})
    assert resp.status_code == INPUT_ERROR

def test_does_not_contain_reacted(jacky_init):
    for i in range (1, 5):
        resp = requests.post(config.url + 'message/unreact/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][i], 'react_id': LIKE})
        assert resp.status_code == INPUT_ERROR
        resp = requests.post(config.url + 'message/unreact/v1', json={'token': jacky_init["token"][2], 'message_id': jacky_init["messages"][i], 'react_id': LIKE})
        assert resp.status_code == INPUT_ERROR

def test_unreact_successfully(jacky_init):
    resp = requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][1], 'react_id': LIKE})
    assert resp.status_code == SUCCESS
    resp = requests.post(config.url + 'message/unreact/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][1], 'react_id': LIKE})
    assert resp.status_code == SUCCESS
    resp = requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][1], 'react_id': LIKE})
    assert resp.status_code == SUCCESS
    resp = requests.post(config.url + 'message/unreact/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][1], 'react_id': LIKE})
    assert resp.status_code == SUCCESS

    for i in range (2, 5):
        resp = requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][i], 'react_id': LIKE})
        assert resp.status_code == SUCCESS
        resp = requests.post(config.url + 'message/unreact/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][i], 'react_id': LIKE})
        assert resp.status_code == SUCCESS
        resp = requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][2], 'message_id': jacky_init["messages"][i], 'react_id': LIKE})
        assert resp.status_code == SUCCESS
        resp = requests.post(config.url + 'message/unreact/v1', json={'token': jacky_init["token"][2], 'message_id': jacky_init["messages"][i], 'react_id': LIKE})
        assert resp.status_code == SUCCESS