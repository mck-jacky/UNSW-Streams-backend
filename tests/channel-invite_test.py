# A program to test the channel_invite_v1 function.
# Written by Alex Hunter z5312469
'''

import pytest

# Iteration 1:
from src.channel import channel_join_v1
from src.channel import channel_invite_v1
from src.error import InputError
from src.error import AccessError
from src.auth import auth_register_v1
from src.other import clear_v1
from src.channels import channels_create_v1

# Iteration 2:
import requests
import json
from src import config

#################### ITERATION 1: ###########################

@pytest.fixture
def initialise():
    clear_v1()
    global user_id_1
    global user_id_2
    global user_id_3
    user_id_1 = auth_register_v1("sample@gmail.au", "password", "namefirst", "namelast")
    user_id_2 = auth_register_v1("sample2@gmail.au", "password2", "namefirst2", "namelast2")
    user_id_3 = auth_register_v1("sample3@gmail.au", "password3", "namefirst3", "namelast3")
    global channel_id_1
    global channel_id_2
    global channel_id_3
    channel_id_1 = channels_create_v1(user_id_1['auth_user_id'], "channel1", True)
    channel_id_2 = channels_create_v1(user_id_1['auth_user_id'], "channel2", True)
    channel_id_3 = channels_create_v1(user_id_1['auth_user_id'], "channel3", False)
    # channel3 is private
    # user_id_1 is an owner of channel 1, 2 and 3. Also a global owner
    # user_id_2 and 3 are not in any channels.
    return [user_id_1, user_id_2, user_id_3, channel_id_1, channel_id_2, channel_id_3]
    
def test_valid_channel_id(initialise):
    
    # Expect success:
    channel_invite_v1(user_id_1['auth_user_id'], channel_id_1['channel_id'], user_id_2['auth_user_id'])
    channel_invite_v1(user_id_1['auth_user_id'], channel_id_2['channel_id'], user_id_2['auth_user_id'])
    channel_invite_v1(user_id_1['auth_user_id'], channel_id_3['channel_id'], user_id_2['auth_user_id']) 
        # This also tests inviting to a private channel
    
    # Expect fail:
    with pytest.raises(InputError):
        channel_invite_v1(user_id_1['auth_user_id'], 99, user_id_2['auth_user_id'])
    with pytest.raises(InputError):
        channel_invite_v1(user_id_1['auth_user_id'], channel_id_3['channel_id'] + 1, user_id_2['auth_user_id'])
    
    
def test_valid_user(initialise): #tests u_id
    
    # Expect success:
    channel_invite_v1(user_id_1['auth_user_id'], channel_id_1['channel_id'], user_id_2['auth_user_id'])
        #user1 adds user2 to channel1
    channel_invite_v1(user_id_2['auth_user_id'], channel_id_1['channel_id'], user_id_3['auth_user_id'])
        #user2 adds user3 to channel1
    channel_invite_v1(user_id_1['auth_user_id'], channel_id_3['channel_id'], user_id_3['auth_user_id'])
        #user1 adds user3 to channel3
    # user 1 and 2 in channel 1, user 1 in channel 2, user 1 and 3 in channel 3

    # Expect fail:
    with pytest.raises(InputError):
        channel_invite_v1(user_id_1['auth_user_id'], channel_id_1['channel_id'], user_id_3['auth_user_id'] + 1)
    with pytest.raises(InputError):
        channel_invite_v1(user_id_1['auth_user_id'], channel_id_1['channel_id'], 99)

def test_valid_auth_user(initialise): #tests auth_user_id
    
    # Expect success:

    # user1 adds user2 to channel1
    channel_invite_v1(user_id_1['auth_user_id'], channel_id_1['channel_id'], user_id_2['auth_user_id'])
    # user2 adds user3 to channel1
    channel_invite_v1(user_id_2['auth_user_id'], channel_id_1['channel_id'], user_id_3['auth_user_id'])
    # user1 adds user3 to channel3
    channel_invite_v1(user_id_1['auth_user_id'], channel_id_3['channel_id'], user_id_3['auth_user_id'])
    
    # user 1 and 2 in channel 1, user 1 in channel 2, user 1 and 3 in channel 3

    # Expect fail:
    with pytest.raises(AccessError):
        channel_invite_v1(99, channel_id_1['channel_id'], user_id_3['auth_user_id'])
    with pytest.raises(AccessError):
        channel_invite_v1(user_id_3['auth_user_id'] + 1, channel_id_1['channel_id'], user_id_3['auth_user_id'])

def test_invite_self(initialise):
    # Test what happens when inviting yourself: 
    # (shouldn't work because you're already a member)
    with pytest.raises(InputError):
        channel_invite_v1(user_id_1['auth_user_id'], channel_id_1['channel_id'], user_id_1['auth_user_id']) 


def test_already_member(initialise):
    
    # Expect success: (also setting up the later tests)
    channel_invite_v1(user_id_1['auth_user_id'], channel_id_1['channel_id'], user_id_2['auth_user_id'])
    channel_invite_v1(user_id_1['auth_user_id'], channel_id_2['channel_id'], user_id_2['auth_user_id'])
    channel_invite_v1(user_id_1['auth_user_id'], channel_id_1['channel_id'], user_id_3['auth_user_id']) 
    # all users are in channel 1, users 1 and 2 in channel 2
    
    # Expect fail:
    with pytest.raises(InputError):
        channel_invite_v1(user_id_1['auth_user_id'], channel_id_1['channel_id'], user_id_2['auth_user_id'])
    with pytest.raises(InputError):
        channel_invite_v1(user_id_2['auth_user_id'], channel_id_1['channel_id'], user_id_1['auth_user_id'])
    with pytest.raises(InputError):
        channel_invite_v1(user_id_3['auth_user_id'], channel_id_1['channel_id'], user_id_2['auth_user_id'])

def test_not_authorised(initialise):
    # Successful tests are tested in previous functions.
    
    # Expect fail:
    with pytest.raises(AccessError):
        channel_invite_v1(user_id_2['auth_user_id'], channel_id_1['channel_id'], user_id_3['auth_user_id'])
    with pytest.raises(AccessError):
        channel_invite_v1(user_id_3['auth_user_id'], channel_id_1['channel_id'], user_id_1['auth_user_id'])
        
# ------- Extra tests --------
def test_invalid_u_id(initialise):
    with pytest.raises(InputError):
        channel_invite_v1(user_id_2['auth_user_id'], channel_id_3['channel_id'], 64)

def test_invalid_auth_and_u_id(initialise):
    with pytest.raises(AccessError):
        channel_invite_v1(-63, channel_id_3['channel_id'], 28)

def test_output(initialise):
    channel_invite_v1(user_id_1['auth_user_id'], channel_id_1['channel_id'], user_id_2['auth_user_id']) == {}
    channel_invite_v1(user_id_1['auth_user_id'], channel_id_1['channel_id'], user_id_3['auth_user_id']) == {}
    
#################### ITERATION 2: ###########################

def test_simple(initialise):
    """
    A simple test to check channel invite v2
    """
    
    resp = requests.post(config.url + 'channel/invite/v2', 
                        json={'token': user_id_1['auth_user_id'],
                                'channel_id'['channel_id'] : 2,
                                'u_id': user_id_3['auth_user_id']})
                                # User 1 invites user 3 to join channel 2
        
    assert json.loads(resp.text) == {}

# This function will allow all iteration 1 tests to work for iteration 2:
def channel_invite_v1(user_id, channel_id, u_id):
    resp = requests.post(
            config.url + 'channel/invite/v2',
            data = {
                'token': str(user_id), #CHANGE THIS
                'channel_id' : channel_id,
                'u_id': u_id
            }
        )

    return json.loads(resp.text)

'''












