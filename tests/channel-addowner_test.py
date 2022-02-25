"""
A file to test the channel addowner feature
"""
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


@pytest.fixture
def initialise():
    requests.delete(config.url + 'clear/v1')
    
    user_1 = requests.post(config.url + 'auth/register/v2',
                         json={'email': 'hellothere@gmail.com', 'password': 'thisismypassword',
                               'name_first': 'Luke', 'name_last': 'Skywalker'})
    user_2 = requests.post(config.url + 'auth/register/v2',
                           json={'email': 'helloagain@gmail.com', 'password': 'newpassword',
                                 'name_first': 'Han', 'name_last': 'Solo'})
    user_3 = requests.post(config.url + 'auth/register/v2',
                           json={'email': 'myemail@hotmail.com', 'password': 'insanepassword',
                                 'name_first': 'Anakin', 'name_last': 'Skywalker'})
    
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
    
    channel_1 = requests.post(config.url + 'channels/create/v2',
                             json={'token': token_1, 'name': "channel1", 'is_public': True})
    channel_2 = requests.post(config.url + 'channels/create/v2',
                             json={'token': token_1, 'name': "channel2", 'is_public': True})
    channel_3 = requests.post(config.url + 'channels/create/v2',
                             json={'token': token_1, 'name': "channel3", 'is_public': False})
    
    channel_id_1 = json.loads(channel_1.text)['channel_id']
    channel_id_2 = json.loads(channel_2.text)['channel_id']
    channel_id_3 = json.loads(channel_3.text)['channel_id']
    
    # channel3 is private
    # user_id_1 is an owner of channel 1, 2 and 3. Also a global owner
    # user_id_2 and 3 are not in any channels.
    
    # invite user 3 into channel 3 as a member
    requests.post(
            config.url + 'channel/invite/v2',
            json = {
                'token': token_1, 
                'channel_id': channel_id_3,
                'u_id': user_id_3
            }
        ) 

def post_addowner(token, channel_id, u_id):
    return requests.post(
            config.url + 'channel/addowner/v1',
            json = {
                'token': token, 
                'channel_id': channel_id,
                'u_id': u_id
            }
        )


#input errors:

def test_channel_exists(initialise):
    response = post_addowner(token_1, channel_id_3 + 1, user_id_3)
    assert response.status_code == INPUT_ERROR
    
    response = post_addowner(token_1, channel_id_1 - 1, user_id_3)
    assert response.status_code == INPUT_ERROR
    
    response = post_addowner(token_1, 999, user_id_3)
    assert response.status_code == INPUT_ERROR

def test_uid_exists(initialise):
    response = post_addowner(token_1, channel_id_3 , user_id_3 + 1)
    assert response.status_code == INPUT_ERROR
    
    response = post_addowner(token_1, channel_id_3 , user_id_1 - 1)
    assert response.status_code == INPUT_ERROR
    
    response = post_addowner(token_1, channel_id_3 , 999)
    assert response.status_code == INPUT_ERROR

def test_uid_not_a_member(initialise):
    """
    Test when the user to be made a channel owner is not a member of the channel.
    Should throw input error.
    """
    # try to make user 2 an owner when not in channel 2 yet
    response = post_addowner(token_1, channel_id_2 , user_id_2)
    assert response.status_code == INPUT_ERROR
    
    
    # insert user 2 into channel 2 as a member
    requests.post(
            config.url + 'channel/invite/v2',
            json = {
                'token': token_1, 
                'channel_id': channel_id_2,
                'u_id': user_id_2
            }
        ) 
    
    # make user 2 an owner
    response = post_addowner(token_1, channel_id_2 , user_id_2)
    assert response.status_code == SUCCESS
    
    pass

def test_uid_already_channel_owner(initialise):
    response = post_addowner(token_1, channel_id_3 , user_id_1) # adding yourself as an owner
    assert response.status_code == INPUT_ERROR
    
    response = post_addowner(token_1, channel_id_3 , user_id_3) # add user 3 as an owner
    assert response.status_code == SUCCESS
    
    response = post_addowner(token_1, channel_id_3 , user_id_3) # add user 3 as an owner again
    assert response.status_code == INPUT_ERROR
    
    # add user 1 as an owner to new channel 4.
    # User 3 is the owner of channel 4
    # Should work
    channel_4 = requests.post(config.url + 'channels/create/v2',
                             json={'token': token_3, 'name': "channel4", 'is_public': False})
    
    channel_id_4 = json.loads(channel_4.text)['channel_id']
    response = post_addowner(token_3, channel_id_4 , user_id_1)
    assert response.status_code == INPUT_ERROR 
        # Input error here as user 1 is not a member of channel 4 
    
    # Add user 1 to channel 4 as a member
    requests.post(config.url + 'channel/join/v2',
                  json = {'token': token_1, 'channel_id': channel_id_4})
    
    # Make user 1 an owner of channel 4
    response = post_addowner(token_3, channel_id_4 , user_id_1)
    assert response.status_code == SUCCESS


# Access errors:
#@pytest.mark.skip
def test_not_authorised(initialise):
    """
    Test when the admin user (not u_id) is not a global or channel owner. Should throw access error.
    """
    # user 2 tries to add user 3 as a channel 2 owner.
    response = post_addowner(token_2, channel_id_2 , user_id_3) 
    assert response.status_code == ACCESS_ERROR
    
    # add user 1 as an owner to new channel 4. Should work as user 3 is a channel owner of channel 4
    channel_4 = requests.post(config.url + 'channels/create/v2',
                             json={'token': token_3, 'name': "channel4", 'is_public': False})
    
    channel_id_4 = json.loads(channel_4.text)['channel_id']
    # Add user 1 to channel 4
    requests.post(config.url + 'channel/invite/v2',
                  json = {'token': token_3,'channel_id': channel_id_4,'u_id': user_id_1})
    # Make user 1 an owner of channel 4
    response = post_addowner(token_3, channel_id_4 , user_id_1) 
    assert response.status_code == SUCCESS
    
    # make user 2 a global owner
    requests.post(
            config.url + 'admin/userpermission/change/v1',
            json = {
                'token': token_1, 
                'u_id': user_id_2,
                'permission_id': GLOBAL_OWNER
            }
        )
    
    # Add user 3 to channel 2
    requests.post(config.url + 'channel/invite/v2',
                  json = {'token': token_1,'channel_id': channel_id_2,'u_id': user_id_3})
     
    # user 2 tries again. Should NOT be successful as user 2 doesnt have channel
    # owner permissions. (need to be a member as well)
    response = post_addowner(token_2, channel_id_2 , user_id_3) 
    assert response.status_code == ACCESS_ERROR
    
# Other:

    
def test_channel_and_global_owner(initialise):
    """
    Test if successful when the admin user (not u_id) is a channel and global owner.
    """
    response = post_addowner(token_1, channel_id_3 , user_id_3) 
    assert response.status_code == SUCCESS
    
    pass


def test_uid_already_global_owner(initialise):
    """
    Tests when the user to be made a channel owner is already a global owner. The
    program should still add them as a channel owner.
    """
    # make user 2 a global owner
    requests.post(
            config.url + 'admin/userpermission/change/v1',
            json = {
                'token': token_1, 
                'u_id': user_id_2,
                'permission_id': GLOBAL_OWNER
            }
        )
    
    # Add user 2 to channel 3
    requests.post(config.url + 'channel/invite/v2',
                  json = {'token': token_1,'channel_id': channel_id_3,'u_id': user_id_2})
    
    # add user 2 as a channel owner of channel 3
    response = post_addowner(token_1, channel_id_3 , user_id_2) 
    assert response.status_code == SUCCESS
    
def test_global_owner_non_member_cant_addowner_private(initialise):
    # Make user 2 a global owner
    requests.post(
            config.url + 'admin/userpermission/change/v1',
            json = {
                'token': token_1,
                'u_id': user_id_2,
                'permission_id': GLOBAL_OWNER
            }
        )
    # User 2 tries to add user 3 as an owner of channel 3
    resp = post_addowner(token_2, channel_id_3, user_id_3)
    assert resp.status_code == ACCESS_ERROR
    
def test_global_owner_non_member_cant_addowner_public(initialise):
    # Add user 3 to channel 2 (public)
    requests.post(
            config.url + 'channel/invite/v2',
            json = {
                'token': token_1, 
                'channel_id': channel_id_2,
                'u_id': user_id_3
            }
        )
    
    # Make user 2 a global owner
    requests.post(
            config.url + 'admin/userpermission/change/v1',
            json = {
                'token': token_1,
                'u_id': user_id_2,
                'permission_id': GLOBAL_OWNER
            }
        )
    # User 2 tries to add user 3 as an owner of channel 2
    resp = post_addowner(token_2, channel_id_2, user_id_3)
    assert resp.status_code == ACCESS_ERROR
