# A file to test the message_react route. Written by Jacky Ma z5336759, Nov 2021

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
    resp = requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][3], 'message_id': jacky_init["messages"][1], 'react_id': LIKE})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][3], 'message_id': jacky_init["messages"][2], 'react_id': LIKE})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][3], 'message_id': jacky_init["messages"][3], 'react_id': LIKE})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][3], 'message_id': jacky_init["messages"][4], 'react_id': LIKE})
    assert resp.status_code == INPUT_ERROR

def test_invalid_react_id(jacky_init):
    resp = requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][1], 'react_id': 2})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][2], 'react_id': 3})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][2], 'message_id': jacky_init["messages"][3], 'react_id': 4})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][2], 'message_id': jacky_init["messages"][4], 'react_id': 5})
    assert resp.status_code == INPUT_ERROR

def test_already_reacted(jacky_init):
    requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][1], 'react_id': LIKE})
    resp = requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][1], 'react_id': LIKE})
    assert resp.status_code == INPUT_ERROR
    requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][2], 'message_id': jacky_init["messages"][3], 'react_id': 1})
    resp = requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][2], 'message_id': jacky_init["messages"][3], 'react_id': LIKE})
    assert resp.status_code == INPUT_ERROR

def test_react_successfully(jacky_init):
    for i in range(1, 5):
        print(i)
        resp = requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][i], 'react_id': LIKE})
        assert resp.json() == {}
        assert resp.status_code == SUCCESS
        resp = requests.post(config.url + 'message/react/v1', json={'token': jacky_init["token"][2], 'message_id': jacky_init["messages"][i], 'react_id': LIKE})
        assert resp.json() == {}
        assert resp.status_code == SUCCESS

