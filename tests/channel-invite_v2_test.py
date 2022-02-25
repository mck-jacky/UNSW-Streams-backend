# A program to test the channel_invite_v2 feature.
# Written by Alex Hunter z5312469

GLOBAL_OWNER = 1
GLOBAL_MEMBER = 2

SUCCESS = 200
INPUT_ERROR = 400
ACCESS_ERROR = 403

import pytest
import requests
import json
from src import config
import jwt
import src.other

from tests.helpers import post_channel_invite
from src.data_store import data_store
"""
### Importing iteration 1 functions:
from src.auth import auth_register_v1
from src.other import clear_v1
from src.channels import channels_create_v1
""" 

@pytest.fixture
def initialise():
    requests.delete(config.url + 'clear/v1')
    
    user_1 = requests.post(config.url + 'auth/register/v2', json={'email': 'hellothere@gmail.com', 'password': 'thisismypassword', 'name_first': 'Luke', 'name_last': 'Skywalker'})
    user_2 = requests.post(config.url + 'auth/register/v2', json={'email': 'helloagain@gmail.com', 'password': 'newpassword', 'name_first': 'Han', 'name_last': 'Solo'})
    user_3 = requests.post(config.url + 'auth/register/v2', json={'email': 'myemail@hotmail.com', 'password': 'insanepassword', 'name_first': 'Anakin', 'name_last': 'Skywalker'})
    
    global token_1
    global token_2
    global token_3
    token_1 = json.loads(user_1.text)['token']
    token_2 = json.loads(user_2.text)['token']
    token_3 = json.loads(user_3.text)['token']
    
    global user_id_1
    global user_id_2
    global user_id_3
    
    user_id_1 = int(jwt.decode(token_1, src.other.SUPERSECRETPASSWORD, algorithms=["HS256"])['auth_user_id'])
    user_id_2 = int(jwt.decode(token_2, src.other.SUPERSECRETPASSWORD, algorithms=["HS256"])['auth_user_id'])
    user_id_3 = int(jwt.decode(token_3, src.other.SUPERSECRETPASSWORD, algorithms=["HS256"])['auth_user_id'])
    
    global channel_id_1
    global channel_id_2
    global channel_id_3
    """
    channel_id_1 = channels_create_v1(user_id_1, "channel1", True)['channel_id']
    channel_id_2 = channels_create_v1(user_id_1, "channel2", True)['channel_id']
    channel_id_3 = channels_create_v1(user_id_1, "channel3", False)['channel_id']
    """
    # TODO: improve this style.
    channel_1 = requests.post(config.url + 'channels/create/v2', json={'token': token_1, 'name': "channel1", 'is_public': True})
    channel_2 = requests.post(config.url + 'channels/create/v2', json={'token': token_1, 'name': "channel2", 'is_public': True})
    channel_3 = requests.post(config.url + 'channels/create/v2', json={'token': token_1, 'name': "channel3", 'is_public': False})
    
    channel_id_1 = json.loads(channel_1.text)['channel_id']
    channel_id_2 = json.loads(channel_2.text)['channel_id']
    channel_id_3 = json.loads(channel_3.text)['channel_id']
    
    # channel3 is private
    # user_id_1 is an owner of channel 1, 2 and 3. Also a global owner
    # user_id_2 and 3 are not in any channels.
    """
    # invite user 3 into channel 3 as a member
    requests.post(
            config.url + 'channel/invite/v2',
            json = {
                'token': token_1, 
                'channel_id': channel_id_3,
                'u_id': user_id_3
            }
        )
    """


def test_valid_channel_id(initialise):
    
    # Expect success:        
    resp = post_channel_invite(token_1, channel_id_1, user_id_2)
    assert resp.status_code == SUCCESS
    resp = post_channel_invite(token_1, channel_id_2, user_id_2)
    assert resp.status_code == SUCCESS
    resp = post_channel_invite(token_1, channel_id_3, user_id_2)
    assert resp.status_code == SUCCESS
        # This also tests inviting to a private channel
    
    # Expect fail:
    resp = post_channel_invite(token_1, 99, user_id_2)
    assert resp.status_code == INPUT_ERROR
    resp = post_channel_invite(token_1, channel_id_3 + 1, user_id_2)
    assert resp.status_code == INPUT_ERROR
    

def test_valid_user(initialise): #tests u_id
    
    # Expect success:
    resp = post_channel_invite(token_1, channel_id_1, user_id_2)
    assert resp.status_code == SUCCESS
        #user1 adds user2 to channel1
    resp = post_channel_invite(token_2, channel_id_1, user_id_3)
    assert resp.status_code == SUCCESS
        #user2 adds user3 to channel1
    resp = post_channel_invite(token_1, channel_id_3, user_id_3)
    assert resp.status_code == SUCCESS
        #user1 adds user3 to channel3
    # user 1 and 2 in channel 1, user 1 in channel 2, user 1 and 3 in channel 3

    # Expect fail:
    resp = post_channel_invite(token_1, channel_id_1, user_id_3 + 1)
    assert resp.status_code == INPUT_ERROR
    
    resp = post_channel_invite(token_1, channel_id_1, 99)
    assert resp.status_code == INPUT_ERROR
    
    resp = post_channel_invite(token_1, channel_id_1, 0)
    assert resp.status_code == INPUT_ERROR

def test_valid_token_authuserid(initialise): #tests auth_user_id 
    """
    # Expect success:
    # user1 adds user2 to channel1
    channel_invite_v1(user_id_1['auth_user_id'], channel_id_1['channel_id'], user_id_2['auth_user_id'])
    # user2 adds user3 to channel1
    channel_invite_v1(user_id_2['auth_user_id'], channel_id_1['channel_id'], user_id_3['auth_user_id'])
    # user1 adds user3 to channel3
    channel_invite_v1(user_id_1['auth_user_id'], channel_id_3['channel_id'], user_id_3['auth_user_id'])
    
    # user 1 and 2 in channel 1, user 1 in channel 2, user 1 and 3 in channel 3
    """
    
    # Expect fail:
    invalid_token = jwt.encode({'auth_user_id': str(999), 'session_id': str(1)},
                               src.other.SUPERSECRETPASSWORD, algorithm="HS256")
    resp = post_channel_invite(invalid_token, channel_id_1, user_id_3)
    assert resp.status_code == ACCESS_ERROR
    
    invalid_token = jwt.encode({'auth_user_id': str(user_id_3 + 1), 'session_id': str(1)},
                               src.other.SUPERSECRETPASSWORD, algorithm="HS256")
    resp = post_channel_invite(invalid_token, channel_id_1, user_id_3)
    assert resp.status_code == ACCESS_ERROR

#@pytest.mark.skip #TODO: fix the token checker function is_valid_token() in other.py
def test_valid_seshid(initialise):
    invalid_token = jwt.encode({'auth_user_id': str(user_id_1), 'session_id': str(999)},
                               src.other.SUPERSECRETPASSWORD, algorithm="HS256")
    resp = post_channel_invite(invalid_token, channel_id_1, user_id_3)
    assert resp.status_code == ACCESS_ERROR
    

def test_invite_self(initialise):
    # Test what happens when inviting yourself: 
    # (shouldn't work because you're already a member)
    resp = post_channel_invite(token_1, channel_id_1, user_id_1)
    assert resp.status_code == INPUT_ERROR
    
    resp = post_channel_invite(token_1, channel_id_3, user_id_1)
    assert resp.status_code == INPUT_ERROR


def test_already_member(initialise):
    
    # Expect success: (also setting up the later tests)
    resp = post_channel_invite(token_1, channel_id_1, user_id_2)
    assert resp.status_code == SUCCESS
    resp = post_channel_invite(token_1, channel_id_2, user_id_2)
    assert resp.status_code == SUCCESS
    resp = post_channel_invite(token_1, channel_id_1, user_id_3)
    assert resp.status_code == SUCCESS
    # all users are in channel 1, users 1 and 2 in channel 2
    
    # Expect fail:
    resp = post_channel_invite(token_1, channel_id_1, user_id_2)
    assert resp.status_code == INPUT_ERROR
    resp = post_channel_invite(token_2, channel_id_1, user_id_1)
    assert resp.status_code == INPUT_ERROR
    resp = post_channel_invite(token_3, channel_id_1, user_id_2)
    assert resp.status_code == INPUT_ERROR
    

def test_not_authorised(initialise):
    # Successful tests are tested in previous functions.
    
    # Expect fail:
    resp = post_channel_invite(token_2, channel_id_1, user_id_3)
    assert resp.status_code == ACCESS_ERROR
    resp = post_channel_invite(token_3, channel_id_1, user_id_1)
    assert resp.status_code == ACCESS_ERROR
    
# ------- Extra tests --------
def test_invalid_u_id(initialise): 
    # Here, both INPUT_ERROR and ACCESS_ERROR would be thrown, so throw an ACCESS_ERROR:
    resp = post_channel_invite(token_2, channel_id_3, 64)
    assert resp.status_code == ACCESS_ERROR
    
    resp = post_channel_invite(token_3, channel_id_3, -1)
    assert resp.status_code == ACCESS_ERROR

def test_invalid_auth_and_u_id(initialise):
    invalid_token = jwt.encode({'auth_user_id': str(-63), 'session_id': str(1)},
                               src.other.SUPERSECRETPASSWORD, algorithm="HS256")
    resp = post_channel_invite(invalid_token, channel_id_1, 28)
    assert resp.status_code == ACCESS_ERROR
    
    invalid_token = jwt.encode({'auth_user_id': str(63), 'session_id': str(1)},
                               src.other.SUPERSECRETPASSWORD, algorithm="HS256")
    resp = post_channel_invite(invalid_token, channel_id_1, -28)
    assert resp.status_code == ACCESS_ERROR

def test_output(initialise):
    resp = post_channel_invite(token_1, channel_id_1, user_id_2)
    assert json.loads(resp.text) == {}





