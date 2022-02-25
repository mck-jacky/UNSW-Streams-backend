# A file to test the message_pin route. Written by Jacky Ma z5336759, Nov 2021

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

def test_message_id_invalid(jacky_init):
    # message_id is not a valid message within a channel or DM that the authorised user has joined
    resp = requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][3], 'message_id': jacky_init["messages"][1]})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][3], 'message_id': jacky_init["messages"][2]})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][3], 'message_id': jacky_init["messages"][3]})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][3], 'message_id': jacky_init["messages"][4]})
    assert resp.status_code == INPUT_ERROR

def test_message_is_already_pinned(jacky_init):
    # the message is already pinned
    requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][1]})
    resp = requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][1]})
    assert resp.status_code == INPUT_ERROR
    requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][3]})
    resp = requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][3]})
    assert resp.status_code == INPUT_ERROR
    requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][5]})
    resp = requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][5]})
    assert resp.status_code == INPUT_ERROR

def test_user_dont_have_permission_to_pin(jacky_init):
    # message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM
    resp = requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][2], 'message_id': jacky_init["messages"][1]})
    assert resp.status_code == ACCESS_ERROR
    resp = requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][3], 'message_id': jacky_init["messages"][5]})
    assert resp.status_code == ACCESS_ERROR
    resp = requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][3], 'message_id': jacky_init["messages"][7]})
    assert resp.status_code == ACCESS_ERROR
    resp = requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][7]})
    assert resp.status_code == ACCESS_ERROR

def test_user_pin_successfully(jacky_init):
    # message pin successfully
    resp = requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][1]})
    assert resp.json() == {}
    assert resp.status_code == SUCCESS
    resp = requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][2]})
    assert resp.json() == {}
    assert resp.status_code == SUCCESS
    resp = requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][1], 'message_id': jacky_init["messages"][6]})
    assert resp.json() == {}
    assert resp.status_code == SUCCESS
    resp = requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][2], 'message_id': jacky_init["messages"][5]})
    assert resp.json() == {}
    assert resp.status_code == SUCCESS
    resp = requests.post(config.url + 'message/pin/v1', json={'token': jacky_init["token"][2], 'message_id': jacky_init["messages"][7]})
    assert resp.json() == {}
    assert resp.status_code == SUCCESS