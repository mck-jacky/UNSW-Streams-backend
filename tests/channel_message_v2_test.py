import pytest
import requests
import json
from src import config
from src.data_store import data_store

@pytest.fixture
def flask_initialize():
    requests.delete(config.url + 'clear/v1')

    r1 = requests.post(config.url + 'auth/register/v2', json={'email': 'email1@gmail.com', 'password': 'password', 'name_first': 'name_first1', 'name_last': 'name_last1'})
    r2 = requests.post(config.url + 'auth/register/v2', json={'email': 'email2@gmail.com', 'password': 'password', 'name_first': 'name_first2', 'name_last': 'name_last2'})
    r3 = requests.post(config.url + 'auth/register/v2', json={'email': 'email3@gmail.com', 'password': 'password', 'name_first': 'name_first3', 'name_last': 'name_last3'})
    global r1_token
    global r2_token
    global r3_token

    r1_token = json.loads(r1.text)['token']
    r2_token = json.loads(r2.text)['token']
    r3_token = json.loads(r3.text)['token']

    requests.post(config.url + 'channels/create/v2', json={'token': r1_token, 'name': 'channel1', 'is_public': True})
    requests.post(config.url + 'channels/create/v2', json={'token': r2_token, 'name': 'channel2', 'is_public': True})
    requests.post(config.url + 'channels/create/v2', json={'token': r3_token, 'name': 'channel3', 'is_public': True})
    requests.post(config.url + 'channel/join/v2', json={'token': r1_token, 'channel_id': 3})
    requests.post(config.url + 'channel/join/v2', json={'token': r2_token, 'channel_id': 3})

    requests.post(config.url + 'message/send/v1', json={'token': r1_token, 'channel_id': 1, 'message': "hello world"})
    requests.post(config.url + 'message/send/v1', json={'token': r2_token, 'channel_id': 2, 'message': "hello world"})
    requests.post(config.url + 'message/send/v1', json={'token': r2_token, 'channel_id': 2, 'message': "hello world world"})
    requests.post(config.url + 'message/send/v1', json={'token': r2_token, 'channel_id': 2, 'message': "hello"})
    
def test_flask_user_id_invalid(flask_initialize):
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": 4, "channel_id": 1, "start": 1})
    assert resp.status_code == 403
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": 5, "channel_id": 2, "start": 1})
    assert resp.status_code == 403
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": 6, "channel_id": 3, "start": 1})
    assert resp.status_code == 403

def test_flask_channel_id_invalid(flask_initialize):
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r1_token, "channel_id": 0, "start": 1})
    assert resp.status_code == 400
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r1_token, "channel_id": 4, "start": 1})
    assert resp.status_code == 400
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r1_token, "channel_id": 5, "start": 1})
    assert resp.status_code == 400

def test_flask_channel_start_excess(flask_initialize):
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r1_token, "channel_id": 1, "start": 2})
    assert resp.status_code == 400
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r1_token, "channel_id": 1, "start": 1})
    assert resp.status_code == 400
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r2_token, "channel_id": 2, "start": 4})
    assert resp.status_code == 400
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r2_token, "channel_id": 2, "start": 3})
    assert resp.status_code == 400
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r3_token, "channel_id": 3, "start": 1})
    assert resp.status_code == 400

def test_flask_channel_access_error(flask_initialize):
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r1_token, "channel_id": 2, "start": 1})
    assert resp.status_code == 403
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r2_token, "channel_id": 1, "start": 1})
    assert resp.status_code == 403
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r3_token, "channel_id": 1, "start": 1})
    assert resp.status_code == 403
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r3_token, "channel_id": 2, "start": 1})
    assert resp.status_code == 403

def test_flask_both_error(flask_initialize):
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r1_token, "channel_id": 2, "start": 4})
    assert resp.status_code == 403
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r3_token, "channel_id": 2, "start": 6})
    assert resp.status_code == 403

def test_flask_success(flask_initialize):
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r2_token, "channel_id": 2, "start": 0})
    assert resp.status_code == 200
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r1_token, "channel_id": 1, "start": 0})
    assert resp.status_code == 200
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r2_token, "channel_id": 2, "start": 1})
    assert resp.status_code == 200
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r2_token, "channel_id": 2, "start": 2})
    assert resp.status_code == 200

def test_zero_message_start(flask_initialize):
    requests.delete(config.url + 'clear/v1')
    r1 = requests.post(config.url + 'auth/register/v2', json={'email': 'email1@gmail.com', 'password': 'password', 'name_first': 'name_first1', 'name_last': 'name_last1'})
    r1_token = json.loads(r1.text)['token']
    requests.post(config.url + 'channels/create/v2', json={'token': r1_token, 'name': 'channel1', 'is_public': True})
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": r1_token, "channel_id": 1, "start": 0})
    assert resp.status_code == 200

@pytest.fixture
def over_50_messages_initialize():
    requests.delete(config.url + 'clear/v1')

    r1 = requests.post(config.url + 'auth/register/v2', json={'email': 'email1@gmail.com', 'password': 'password', 'name_first': 'name_first1', 'name_last': 'name_last1'})
    user_1 = json.loads(r1.text)['token']

    requests.post(config.url + 'channels/create/v2', json={'token': user_1, 'name': 'channel1', 'is_public': True})

    for _ in range (1, 60):
        requests.post(config.url + 'message/send/v1', json={'token': user_1, 'channel_id': 1, 'message': "hello world"})

    return [user_1]

def test_over_50_msg(over_50_messages_initialize):
    resp = requests.get(config.url + 'channel/messages/v2', params={"token": over_50_messages_initialize[0], "channel_id": 1, "start": 1})
    assert resp.status_code == 200