# A program to test the channel_join_v2 feature.
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

from src.data_store import data_store
from tests.fixtures import alex_init
"""
### Importing iteration 1 functions:
from src.auth import auth_register_v1
from src.other import clear_v1
from src.channels import channels_create_v1
"""

def post_channeljoin(token, channel_id):
    return requests.post(
            config.url + 'channel/join/v2',
            json = {
                'token': token, 
                'channel_id': channel_id
            }
        ) 

    
# Give InputError if "channel_id" is not a valid channel
def test_valid_channel_id(alex_init):

    resp = post_channeljoin(alex_init['token'][2], alex_init['channel_id'][1])
    resp = post_channeljoin(alex_init['token'][2], alex_init['channel_id'][2])
    
    resp = post_channeljoin(alex_init['token'][2], 999)
    assert resp.status_code == INPUT_ERROR

# Give InputError if user is authorised and already a member of "channel_id"
def test_already_member(alex_init):
    
    post_channeljoin(alex_init['token'][2], alex_init['channel_id'][2])
    
    resp = post_channeljoin(alex_init['token'][1], alex_init['channel_id'][1])
    assert resp.status_code == INPUT_ERROR
    resp = post_channeljoin(alex_init['token'][2], alex_init['channel_id'][2])
    assert resp.status_code == INPUT_ERROR

# Give AccessError if user is not authorised to access "channel_id"
def test_private_channel_access(alex_init):

    # Expect success:
    resp = post_channeljoin(alex_init['token'][2], alex_init['channel_id'][1])
    assert resp.status_code == SUCCESS
    resp = post_channeljoin(alex_init['token'][3], alex_init['channel_id'][2])
    assert resp.status_code == SUCCESS
    
    
    
    # Expect fail:
    resp = post_channeljoin(alex_init['token'][2], alex_init['channel_id'][3])
    assert resp.status_code == ACCESS_ERROR
    
    resp = post_channeljoin(alex_init['token'][3], alex_init['channel_id'][3])
    assert resp.status_code == ACCESS_ERROR
    
    # Make user 3 a global owner:
    requests.post(
            config.url + 'admin/userpermission/change/v1',
            json = {
                'token': alex_init['token'][1], 
                'u_id': alex_init['user_id'][3],
                'permission_id': GLOBAL_OWNER
            }
        ) 
    
    # User 3 tries to join private channel again
    resp = post_channeljoin(alex_init['token'][3], alex_init['channel_id'][3])
    assert resp.status_code == SUCCESS



def test_correct_token_format_with_invalid_userid(alex_init):
    
    user_id = 99
    session_id = 1
    
    invalid_token = jwt.encode({'auth_user_id': str(user_id), 'session_id': str(session_id)},
                               src.other.SUPERSECRETPASSWORD, algorithm="HS256")
    
    resp = post_channeljoin(invalid_token, alex_init['channel_id'][1])
    assert resp.status_code == ACCESS_ERROR

def test_correct_token_format_with_invalid_seshid(alex_init):
    
    user_id = 2
    session_id = 99999
    
    invalid_token = jwt.encode({'auth_user_id': str(user_id), 'session_id': str(session_id)},
                               src.other.SUPERSECRETPASSWORD, algorithm="HS256")
    
    resp = post_channeljoin(invalid_token, alex_init['channel_id'][1])
    assert resp.status_code == ACCESS_ERROR


# Tests return values are empty dictionaries
def test_output(alex_init):
    resp = post_channeljoin(alex_init['token'][2], alex_init['channel_id'][2])
    assert json.loads(resp.text) == {}


def test_invalid_token(alex_init):
    print("Test_invalid_token")
    resp = post_channeljoin("InvalidToken", alex_init['channel_id'][3])
    assert resp.status_code == ACCESS_ERROR

 
def test_incorrect_password(alex_init):
    requests.delete(config.url + 'clear/v1')
    """
    user_1 = requests.post(config.url + 'auth/register/v2', json={'email': 'hellothere@gmail.com', 'password': 'thisismypassword', 'name_first': 'Luke', 'name_last': 'Skywalker'})
    alex_init['token'][1] = json.loads(user_1.text)['token']
    channel_1 = requests.post(config.url + 'channels/create/v2', json={'token': alex_init['token'][1], 'name': "channel1", 'is_public': True})
    alex_init['channel_id'][1] = json.loads(channel_1.text)['channel_id']
    
    print(f"From test file: {data_store.get()}")
    """
    invalid_token = jwt.encode(jwt.decode(alex_init['token'][1], src.other.SUPERSECRETPASSWORD,
                               algorithms=["HS256"]), "IncorrectPassword", algorithm="HS256")
    
    resp = post_channeljoin(invalid_token, alex_init['channel_id'][1])
    assert resp.status_code == ACCESS_ERROR
    pass

        
    
    
    
