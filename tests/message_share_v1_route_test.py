# A file to test the message_share route. Written by Jacky Ma z5336759, Nov 2021

SUCCESS = 200
INPUT_ERROR = 400
ACCESS_ERROR = 403

from os import access
import pytest
import requests
import json
from src import config
import jwt
import src.other

from tests.fixtures import jacky_init

def test_both_channel_and_dm_id_invalid(jacky_init):
    # both channel_id and dm_id are invalid
    resp = requests.post(config.url + 'message/share/v1', json={'token': jacky_init["token"][1], 'og_message_id': jacky_init["messages"][1], 'message': "", 'channel_id': -1, 'dm_id': -1})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/share/v1', json={'token': jacky_init["token"][2], 'og_message_id': jacky_init["messages"][5], 'message': "", 'channel_id': 100, 'dm_id': -1})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/share/v1', json={'token': jacky_init["token"][3], 'og_message_id': jacky_init["messages"][7], 'message': "", 'channel_id': -1, 'dm_id': -100})
    assert resp.status_code == INPUT_ERROR

def test_neither_negative_one(jacky_init):
    # neither channel_id nor dm_id are -1
    resp = requests.post(config.url + 'message/share/v1', json={'token': jacky_init["token"][1], 'og_message_id': jacky_init["messages"][1], 'message': "", 'channel_id': jacky_init["channel_id"][1], 'dm_id': jacky_init["dm_id"][1]})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/share/v1', json={'token': jacky_init["token"][2], 'og_message_id': jacky_init["messages"][1], 'message': "testing", 'channel_id': jacky_init["channel_id"][2], 'dm_id': jacky_init["dm_id"][2]})
    assert resp.status_code == INPUT_ERROR

def test_user_dont_have_permission_to_og_message(jacky_init):
    # og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
    resp = requests.post(config.url + 'message/share/v1', json={'token': jacky_init["token"][3], 'og_message_id': jacky_init["messages"][1], 'message': "", 'channel_id': jacky_init["channel_id"][2], 'dm_id': -1})
    assert resp.status_code == INPUT_ERROR
    resp = requests.post(config.url + 'message/share/v1', json={'token': jacky_init["token"][3], 'og_message_id': jacky_init["messages"][3], 'message': "testing", 'channel_id': -1, 'dm_id': jacky_init["dm_id"][2]})
    assert resp.status_code == INPUT_ERROR

def test_length_of_msg_too_long(jacky_init):
    # length of message is more than 1000 characters
    resp = requests.post(config.url + 'message/share/v1', json={'token': jacky_init["token"][1], 'og_message_id': jacky_init["messages"][1], 'message': "6RHkMaUjBHhn6K9WKtI6MnEo7OziC06QJUYuYCh17aE\
        g6bxIXFk0CFdXCSn4iHxMo952QjvKGyKYKL1NDaWxf44CvXlsl8OmvyHAKUsMoh73vVbUkhUFwzl4RuujXAe2SRALNXuj1txlo7vJ\
        77b6g0GNyGvZbqOTpR5m6ezhrbgkLaYssYqytuxpac1sOvGerHpxQG7MgYZq25HxCTQkT4vGMh7M5EW6DubNGAgLxgSB3k5XIT5me\
        qrtU3amds6XPuTiX7IUBvxj8yiRU8ewL4lKEtuNN7Yspa4bmOm7HA3FRkoANQAKWpknhwQmWXzPTbJqO9z6k6bcraZlh7o1mqtVJw\
        eCTitHhWr0BOzOfo9KgzLuF6CFZxOcAWmiIKXqj7IWLzhXD2v9Df6colREbyXuYclLt0j4oDr7SVQpXpYiBrMmtOQtqnHA0rMaWwD\
        nNzvRtSRtD1egCjN3rtb90YnnD4ZzVazzRFYiVt2j7eBa6DQZAxflqYhuFcaybTWqlgoOLjdowyg5CJhMTLjNaCWDbCQ7fIHkeid3\
        OfWSkO8heBQ0uVA9UAymBF1cQ7pJ01CG7MbscR2LXgB82gPJSwdoxj3YH6fhsHL7WTZHI4zdWNxwDaFlPRGHDAov2WiJebxTK9ZMw\
        PwwW8jIU3FJdjAEV4PjUyDhX21Z2ZqPWm4fi9ENUxZN8wtOsVKxTiEDJqGVexyltkNAXenm9FqWuvD6cZZhnXOTE0bweeZATHUUNo\
        ulHcMJWkZGxISMayRTG5bvvxJZnktQnGXdskuSTkkS6H0WLVsiSJd73Gvlp5JuslU7n01Wur8YqnngaX0Xma8nDsSKuRcDZPJbx30\
        o5PEt80f2q6llHHFUULn9tgS7fvWK2h1ov4NUUtD9RATH1wmB3ySnfJmMKGElSHhUyJVX6odRKcBXndzJ9SNA5oqbce0k8hlz6Rmn\
        X8766BwGE4F2oFONn7ZABEodj6WyuxpmDjhLGDeXdVWhjIaCm", 'channel_id': jacky_init["channel_id"][2], 'dm_id': -1})
    assert resp.status_code == INPUT_ERROR

def test_user_has_not_joined_the_channel_or_dm_they_are_trying_to_share_to(jacky_init):
    # the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and 
    # the authorised user has not joined the channel or DM they are trying to share the message to
    resp = requests.post(config.url + 'message/share/v1', json={'token': jacky_init["token"][3], 'og_message_id': jacky_init["messages"][5], 'message': "", 'channel_id': jacky_init["channel_id"][1], 'dm_id': -1})
    assert resp.status_code == ACCESS_ERROR
    resp = requests.post(config.url + 'message/share/v1', json={'token': jacky_init["token"][3], 'og_message_id': jacky_init["messages"][6], 'message': "testing", 'channel_id': -1, 'dm_id': jacky_init["dm_id"][1]})
    assert resp.status_code == ACCESS_ERROR
    resp = requests.post(config.url + 'message/share/v1', json={'token': jacky_init["token"][3], 'og_message_id': jacky_init["messages"][3], 'message': "", 'channel_id': jacky_init["channel_id"][1], 'dm_id': -1})
    assert resp.status_code == ACCESS_ERROR
    resp = requests.post(config.url + 'message/share/v1', json={'token': jacky_init["token"][3], 'og_message_id': jacky_init["messages"][4], 'message': "", 'channel_id': -1, 'dm_id': jacky_init["dm_id"][1]})
    assert resp.status_code == ACCESS_ERROR

def test_share_successfully(jacky_init):
    # channel to channel
    resp = requests.post(config.url + 'message/share/v1', json={'token': jacky_init["token"][1], 'og_message_id': jacky_init["messages"][1], 'message': "testing", 'channel_id': jacky_init["channel_id"][2], 'dm_id': -1})
    assert resp.json() == {"shared_message_id": 8}
    assert resp.status_code == 200
    # channel to dm
    resp = requests.post(config.url + 'message/share/v1', json={'token': jacky_init["token"][2], 'og_message_id': jacky_init["messages"][5], 'message': "", 'channel_id': -1, 'dm_id': jacky_init["dm_id"][1]})
    assert resp.json() == {"shared_message_id": 9}
    assert resp.status_code == 200
    # dm to dm
    resp = requests.post(config.url + 'message/share/v1', json={'token': jacky_init["token"][3], 'og_message_id': jacky_init["messages"][7], 'message': "1", 'channel_id': -1, 'dm_id': jacky_init["dm_id"][2]})
    assert resp.json() == {"shared_message_id": 10}
    assert resp.status_code == 200
    # dm to channel
    resp = requests.post(config.url + 'message/share/v1', json={'token': jacky_init["token"][2], 'og_message_id': jacky_init["messages"][4], 'message': "", 'channel_id': jacky_init["channel_id"][1], 'dm_id': -1})
    assert resp.json() == {"shared_message_id": 11}
    assert resp.status_code == 200
