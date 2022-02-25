"""
A file to test the channel_leave_v1 function
Written by Alex Hunter z5312469, October 2021
"""

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
    # TODO: improve this style. (can copy paste from another one of my test files)
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
            data = {
                'token': token_1, 
                'channel_id': channel_id_3,
                'u_id': user_id_3
            }
        )
    """
def post_leave_req(token, channel_id):
    return requests.post(config.url + 'channel/leave/v1',
                         json={'token': token, 'channel_id': channel_id}) 


# Input errors:
def test_channel_doesnt_exist(initialise):
    """
    Test if a user is trying to leave a channel which doesn't exist
    """
    
    response = post_leave_req(token_1, channel_id_3 + 1)
    assert response.status_code == INPUT_ERROR
    
    response = post_leave_req(token_1, 999)
    assert response.status_code == INPUT_ERROR

    pass
    
    
# Access errors: 
def test_not_a_member(initialise):
    """
    Test if a user is trying to leave a channel which they are not a part of
    """
    response = post_leave_req(token_3, channel_id_1)
    assert response.status_code == ACCESS_ERROR
    
    response = post_leave_req(token_2, channel_id_2)
    assert response.status_code == ACCESS_ERROR
    
    pass

# Other:
def test_lose_message_send_access(initialise):
    """
    Test if a user has left a channel successfully. e.g. loses access to sending messages
    """
    # User 1 leaves channel 2, then tries to send a message to channel 2.
    response = post_leave_req(token_1, channel_id_2)
    assert response.status_code == SUCCESS
    response = requests.post(
            config.url + 'message/send/v1',
            json = {
                'token': token_1, 
                'channel_id': channel_id_2,
                'message': "hello"
            }
        )
    assert response.status_code == ACCESS_ERROR
    
    pass


def test_messages_remain(initialise):
    """
    Test if a user's messages remain in a channel after they leave.
    """
    # Add user 3 to channel 2 (required for channel/messages/v2)
    resp = requests.post(
            config.url + 'channel/join/v2',
            json = {
                'token': token_3, 
                'channel_id': channel_id_2
            }
        ) 
    assert resp.status_code == SUCCESS
    # User 1 sends a message to channel 2
    response = requests.post(
            config.url + 'message/send/v1',
            json = {
                'token': token_1, 
                'channel_id': channel_id_2,
                'message': "hello_my_name_is_jeff"
            }
        )
    assert response.status_code == SUCCESS
    # User 1 leaves channel 2
    response = post_leave_req(token_1, channel_id_2)
    assert response.status_code == SUCCESS
    
    # Check message is still in the channel.
    response = requests.get(
            config.url + 'channel/messages/v2',
            params = {
                'token': token_3, 
                'channel_id': channel_id_2,
                'start': 0 
            }
        )
    assert response.status_code == SUCCESS

    ### Check if the message still exists:    
    message_status = False
    return_val = json.loads(response.text) 
    for message in return_val["messages"]:
        if message["message"] == "hello_my_name_is_jeff" and message["u_id"] == user_id_1:
            message_status = True
    assert message_status == True
    
    message_status = False
    return_val = json.loads(response.text) 
    for message in return_val["messages"]:
        if message["message"] == "hello_my_name_is_jeff" and message["u_id"] == user_id_2: # (wrong user id)
            message_status = True
    assert message_status == False
    
    message_status = False
    return_val = json.loads(response.text) 
    for message in return_val["messages"]:
        if message["message"] == "hello" and message["u_id"] == user_id_1: # (wrong message)
            message_status = True
    assert message_status == False


def test_lone_channel_owner_leaves(initialise):
    """
    Test if the lone channel owner leaves
    """
    resp = post_leave_req(token_1, channel_id_3)
    assert resp.status_code == SUCCESS 
    # Here, the only channel owner leaves. Shouldn't be an error
    pass


def test_rejoin_after_leave(initialise):
    """
    Test if you can rejoin after you leave. 
    If channel is private, will only work for global owners.
    """
    # Leave and join channel 3
    response = post_leave_req(token_1, channel_id_1)
    assert response.status_code == SUCCESS
    requests.post(
            config.url + 'channel/join/v2',
            json = {
                'token': token_1, 
                'channel_id': channel_id_1
            }
        ) 
    
    # Leave and join channel 2
    response = post_leave_req(token_1, channel_id_2)
    assert response.status_code == SUCCESS
    requests.post(
            config.url + 'channel/join/v2',
            json = {
                'token': token_1, 
                'channel_id': channel_id_2
            }
        ) 
    
    # Leave and join channel 3
    response = post_leave_req(token_1, channel_id_3)
    assert response.status_code == SUCCESS
    requests.post(
            config.url + 'channel/join/v2',
            data = {
                'token': token_1, 
                'channel_id': channel_id_3
            }
        ) 
    
    pass


def test_rejoin_after_leave_private(initialise):

    # Invite user 3 to join channel 3
    requests.post(
            config.url + 'channel/invite/v2',
            json = {
                'token': token_1, 
                'channel_id': channel_id_3,
                'u_id': user_id_3
            }
        ) 
    
    response = post_leave_req(token_3, channel_id_3)
    assert response.status_code == SUCCESS
    # User 3 tries to re-join channel 3
    resp = requests.post(
            config.url + 'channel/join/v2',
            json = {
                'token': token_3, 
                'channel_id': channel_id_3
            }
        ) 
    assert resp.status_code == ACCESS_ERROR
    

