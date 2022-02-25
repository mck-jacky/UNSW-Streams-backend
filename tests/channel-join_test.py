# A program to test the channel_join feature.
# Written by Alex Hunter z5312469
'''
import pytest

# Iteration 1:
#from src.channel import channel_join_v1
from src.channels import channels_create_v1
from src.error import InputError
from src.error import AccessError
from src.auth import auth_register_v1
from src.other import clear_v1
import src.channels

# Iteration 2:
import requests
import json
from src import config

#################### ITERATION 1: ###########################

@pytest.fixture
def initialise():
    clear_v1()
    
    ### TODO: REMEMBER TO CHANGE TO V2 FUNCTIONS!!! ###
    user_1 = auth_register_v1("sample@gmail.au", "password", "namefirst", "namelast")
    user_2 = auth_register_v1("sample2@gmail.au", "password2", "namefirst2", "namelast2")
    user_3 = auth_register_v1("sample3@gmail.au", "password3", "namefirst3", "namelast3")
    
    global user_id_1
    global user_id_2
    global user_id_3
    user_id_1 = user_1['auth_user_id']
    user_id_2 = user_2['auth_user_id']
    user_id_3 = user_3['auth_user_id']
    
    global token_1
    global token_2
    global token_3
    token_1 = user_1['token']
    token_2 = user_2['token']
    token_3 = user_3['token']
    
    global channel_id_1
    global channel_id_2
    global channel_id_3
    channel_id_1 = channels_create_v1(user_id_1, "channel1", True)['channel_id']
    channel_id_2 = channels_create_v1(user_id_1, "channel2", True)['channel_id']
    channel_id_3 = channels_create_v1(user_id_1, "channel3", False)['channel_id']
    # channel3 is private
    # user_id_1 is an owner of channel 1, 2 and 3. Also a global owner
    # user_id_2 and 3 are not in any channels.
    
    # invite user 3 into channel 3 as a member
    requests.post(
            config.url + 'channel/invite/v2',
            data = {
                'token': token_1, 
                'channel_id': channel_id_3,
                'u_id': user_id_3
            }
        ) 



# Give InputError if "channel_id" is not a valid channel
def test_valid_channel_id(initialise):

    # Expect to work:
    channel_join_v1(user_id_2['auth_user_id'], channel_id_1['channel_id'])
    channel_join_v1(user_id_2['auth_user_id'], channel_id_2['channel_id'])
    
    # Expect to fail:
    with pytest.raises(InputError):
        channel_join_v1(user_id_2['auth_user_id'], 999)


# Give InputError if user is authorised and already a member of "channel_id"
def test_already_member(initialise):
    
    # Expect to work:
    channel_join_v1(user_id_2['auth_user_id'], channel_id_1['channel_id'])
    channel_join_v1(user_id_2['auth_user_id'], channel_id_2['channel_id'])
    
    # Expect to fail:
    with pytest.raises(InputError):
        channel_join_v1(user_id_1['auth_user_id'], channel_id_1['channel_id'])
    with pytest.raises(InputError):
        channel_join_v1(user_id_2['auth_user_id'], channel_id_2['channel_id'])      


# Give AccessError if user is not authorised to access "channel_id"
def test_private_channel_access(initialise):
    
    #Expect to work:
    channel_join_v1(user_id_2['auth_user_id'], channel_id_1['channel_id'])
    channel_join_v1(user_id_3['auth_user_id'], channel_id_2['channel_id'])
    
    #Expect to fail:
    with pytest.raises(AccessError):
        channel_join_v1(user_id_2['auth_user_id'], channel_id_3['channel_id'])
    with pytest.raises(AccessError):
        channel_join_v1(user_id_3['auth_user_id'], channel_id_3['channel_id'])

def test_user_exists_alex():
    clear_v1()
    user_id_1 = auth_register_v1("sample@gmail.au", "password", "namefirst", "namelast")
    channel_id_1 = channels_create_v1(user_id_1['auth_user_id'], "channel1", True)
    with pytest.raises(AccessError):
        channel_join_v1(user_id_1['auth_user_id'] + 1, channel_id_1['channel_id'])
    with pytest.raises(AccessError):
        channel_join_v1(user_id_1['auth_user_id'] - 1, channel_id_1['channel_id'])

def test_global_owner_private_channel_access_alex():
    clear_v1()
    user_id_1 = auth_register_v1("sample1@gmail.au", "password", "namefirst1", "namelast1")['auth_user_id']
    user_id_2 = auth_register_v1("sample2@gmail.au", "password", "namefirst2", "namelast2")['auth_user_id']
    user_id_3 = auth_register_v1("sample3@gmail.au", "password", "namefirst3", "namelast3")['auth_user_id']
    channel_id_1 = channels_create_v1(user_id_3, "channel1", False)['channel_id']
    # User 1 is a global owner, user 3 is a channel owner of channel 1
    
    # Expect success:
    channel_join_v1(user_id_1, channel_id_1) 
    
    with pytest.raises(AccessError):
        channel_join_v1(user_id_2, channel_id_1)
    

# ------- Extra tests --------
# Tests if auth_user_id is invalid
def test_user_exists(initialise):
    with pytest.raises(AccessError):
        channel_join_v1(4, channel_id_3['channel_id'])

# Tests return values are empty dictionaries
def test_output(initialise):
    assert channel_join_v1(user_id_2['auth_user_id'], channel_id_2['channel_id']) == {}
    assert channel_join_v1(user_id_3['auth_user_id'], channel_id_1['channel_id']) == {}

# Tests global owner successfully joining a private channel
def test_global_owner_private_channel_access(initialise):
    # User 2 creates private channel
    channels_create_v1(user_id_2['auth_user_id'], "channel4", False)
    # User 1 (global owner can join private channels)
    assert channel_join_v1(user_id_1['auth_user_id'], 4) == {}
    # AccessError - User 2 cannot join private channel 
    with pytest.raises(AccessError):
        channel_join_v1(user_id_3['auth_user_id'], 4)

def test_channel_owner_private_channel_access():
    # currently there is no way to check this properly as you can not be a
    # channel owner without also being a member (already joined the channel)
    
    clear_v1()
    auth_register_v1("sample1@gmail.au", "password", "namefirst1", "namelast1")['auth_user_id']
    user_id_2 = auth_register_v1("sample2@gmail.au", "password", "namefirst2", "namelast2")['auth_user_id']
    user_id_3 = auth_register_v1("sample3@gmail.au", "password", "namefirst3", "namelast3")['auth_user_id']
    channel_id_1 = channels_create_v1(user_id_3, "channel1", False)['channel_id']
    # User 1 is a global owner, user 3 is a channel owner of channel 1
    """
    # Expect success:
    channel_join_v1(user_id_3, channel_id_1) 
    """
    with pytest.raises(AccessError):
        channel_join_v1(user_id_2, channel_id_1)


#################### ITERATION 2: ###########################

def test_simple(initialise):
    """
    A simple test to check channel join v2
    """
    # user 3 tries to join channel 1
    resp = requests.post(
            config.url + 'channel/join/v2',
            json = {
                'token': token_3, 
                'channel_id': channel_id_1
            }
        ) 

    #assert json.loads(resp.text) == {}


# This function will allow all iteration 1 tests to work for iteration 2:
def channel_join_v1(user_id, channel_id):
    resp = requests.get(config.url + 'channel/join/v2', json = {
                'token': token_3, 
                'channel_id': channel_id_1
            })
    if resp.status_code == 403:
        raise AccessError("Access error raised")
    elif resp.status_code == 400:
        raise InputError("Input error raised")
    
    return json.loads(resp.text)

'''



