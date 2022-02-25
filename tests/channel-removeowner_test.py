"""
A file to test the channel removeowner feature
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

def post_removeowner(token, channel_id, u_id):
    return requests.post(
            config.url + 'channel/removeowner/v1',
            json = {
                'token': token, 
                'channel_id': channel_id,
                'u_id': u_id
            }
        ) 

#input errors:

def test_channel_exists(initialise):
    response = post_removeowner(token_1, channel_id_3 + 1, user_id_3)
    assert response.status_code == INPUT_ERROR
    
    response = post_removeowner(token_1, channel_id_1 - 1, user_id_3)
    assert response.status_code == INPUT_ERROR
    
    response = post_removeowner(token_1, 999, user_id_3)
    assert response.status_code == INPUT_ERROR


def test_uid_exists(initialise):
    response = post_removeowner(token_1, channel_id_3 , user_id_3 + 1)
    assert response.status_code == INPUT_ERROR
    
    response = post_removeowner(token_1, channel_id_3 , user_id_1 - 1)
    assert response.status_code == INPUT_ERROR
    
    response = post_removeowner(token_1, channel_id_3 , 999)
    assert response.status_code == INPUT_ERROR


def test_uid_not_a_channel_owner(initialise):
    """
    Test when the user to be made a channel owner is not an owner of the channel.
    Should throw input error. Test when u_id is not a global owner here.
    """
    response = post_removeowner(token_1, channel_id_3, user_id_3)
    assert response.status_code == INPUT_ERROR
    
    pass


def test_uid_sole_channel_owner(initialise):

    response = post_removeowner(token_1, channel_id_3, user_id_1) # removing themselves
    assert response.status_code == INPUT_ERROR
    
    # Add multiple channel owners:
    requests.post(
            config.url + 'channel/addowner/v1',
            json = {
                'token': token_1, 
                'channel_id': channel_id_3,
                'u_id': user_id_3
            }
        ) 
    
    
    response = post_removeowner(token_1, channel_id_3, user_id_1) # removing themselves
    assert response.status_code == SUCCESS
    
    response = post_removeowner(token_1, channel_id_3, user_id_3) # Now user 3 is the last owner.
    assert response.status_code == INPUT_ERROR
    
    pass
    

# Access errors:

def test_not_authorised(initialise):
    """
    Test when the admin user (not u_id) is not a global or channel owner. 
    Should throw access error.
    """
    # Add multiple channel owners so that we don't get an input error:
    requests.post(
            config.url + 'channel/addowner/v1',
            json = {
                'token': token_1, 
                'channel_id': channel_id_3,
                'u_id': user_id_3
            }
        ) 
    
    # User 2 tries to remove channel owner access from user 1
    response = post_removeowner(token_2, channel_id_3, user_id_1)
    assert response.status_code == ACCESS_ERROR
    
    pass

# Other:


def test_only_channel_owner_or_only_global_owner(initialise):
    """
    Test if successful when the admin user (not u_id) is a channel and/or global owner only.
    """
    # First add user 2 & 3 as a channel owner of channel 3.
    requests.post(
            config.url + 'channel/addowner/v1',
            json = {
                'token': token_1, 
                'channel_id': channel_id_3,
                'u_id': user_id_2
            }
        )
    
    requests.post(
            config.url + 'channel/addowner/v1',
            json = {
                'token': token_1, 
                'channel_id': channel_id_3,
                'u_id': user_id_3
            }
        ) 
    # User 3 removes user 1
    post_removeowner(token_3, channel_id_3, user_id_1)
    
    # User 1 is now a global owner but not a channel owner of channel 3:
    # User 1 removes user 3
    post_removeowner(token_1, channel_id_3, user_id_3)
    
    pass

"""
def test_channel_and_global_owner(initialise):
    
    #Test if successful when the admin user (not u_id) is a channel and global owner.
    
    pass
"""

def test_uid_not_a_member(initialise):
    """
    Tests when the user is not a member of the channel. (This means they are also
    not a channel owner, so it should throw an input error)
    """
    response = post_removeowner(token_1, channel_id_2, user_id_3)
    assert response.status_code == INPUT_ERROR
    
    pass

def test_global_owner_nonmember_cannot_remove_owner(initialise):
    """
    Test when the user is a global owner, but not a channel member. In this case,
    the user does not have channel owner permission.
    """
    # Make user 3 a channel owner of channel 3
    requests.post(
            config.url + 'channel/addowner/v1',
            json = {
                'token': token_1, 
                'channel_id': channel_id_3,
                'u_id': user_id_3
            }
        ) 
    # Make user 2 a global owner:
    requests.post(
            config.url + 'admin/userpermission/change/v1',
            json = {
                'token': token_1,
                'u_id': user_id_2,
                'permission_id': GLOBAL_OWNER
            }
        )
    # User 2 tries to remove user 3 from being a channel owner:
    resp = post_removeowner(token_2, channel_id_3, user_id_3)
    assert resp.status_code == ACCESS_ERROR

"""
def test_u-id_sole_global_owner():
    
    #tests if the user to have channel owner removed is the sole global owner and a channel owner.
    #Should not affect the channel ownerremove process.
    
    pass
"""

    
