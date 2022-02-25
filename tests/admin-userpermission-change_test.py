"""
A file to test the user permission change feature. 
Written by Alex Hunter z5312469
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

def post_permissionchange(token, u_id, perm_id):
    return requests.post(
            config.url + 'admin/userpermission/change/v1',
            json = {
                'token': token, 
                'u_id': u_id,
                'permission_id': perm_id
            }
        ) 

# Input Errors:

def test_uid_invalid(initialise):

    response = post_permissionchange(token_1, user_id_3 + 1, GLOBAL_MEMBER )
    assert response.status_code == INPUT_ERROR
    pass

def test_demote_only_global_owner(initialise):

    # Try to remove the only global owner:
    response = post_permissionchange(token_1, user_id_1, GLOBAL_MEMBER)
    assert response.status_code == INPUT_ERROR
    
    # Add another global owner:
    post_permissionchange(token_1, user_id_3, GLOBAL_OWNER)
    
    # Send same request, but should work now:
    response = post_permissionchange(token_1, user_id_1, GLOBAL_MEMBER)
    assert response.status_code == SUCCESS

def test_permissionid_invalid(initialise): 

    response = post_permissionchange(token_1, user_id_1, 3)
    assert response.status_code == INPUT_ERROR

    response = post_permissionchange(token_1, user_id_1, 0)
    assert response.status_code == INPUT_ERROR
    
# Access Errors:
def test_authuser_doesnt_exist(initialise):

    response = post_permissionchange("Invalid token", user_id_1, GLOBAL_MEMBER )
    assert response.status_code == ACCESS_ERROR
    # Token validity test is checked in other test functions. Don't need much detail here.
    
    pass

def test_authuser_not_global_owner(initialise):

    response = post_permissionchange(token_2, user_id_1, GLOBAL_MEMBER)
    assert response.status_code == ACCESS_ERROR
    
    response = post_permissionchange(token_3, user_id_2, GLOBAL_OWNER)
    assert response.status_code == ACCESS_ERROR
    
    pass

# Other:

def test_permission_change_successful(initialise):
    
    # user 1 makes user 2 a global owner
    response = post_permissionchange(token_1, user_id_2, GLOBAL_OWNER)
    assert response.status_code == SUCCESS
    
    # user 2 maker user 1 a global member
    response = post_permissionchange(token_2, user_id_1, GLOBAL_MEMBER)
    assert response.status_code == SUCCESS
    pass

# For is_sole_global_owner() helper function coverage
def test_is_sole_global_owner():
    """
    Test whether the only valid global owner left can remove himself. Should
    raise an InputError.
    """

    requests.delete(config.url + 'clear/v1')

    user1 = requests.post(config.url + 'auth/register/v2',
        json = {'email': '1@em.com',
                'password': 'password1',
                'name_first': 'NF1',
                'name_last': 'NL1'})

    user1_id = json.loads(user1.text)['auth_user_id']
    user1_token = json.loads(user1.text)['token']

    resp = requests.post(config.url + 'admin/userpermission/change/v1',
        json = {'token': user1_token,
                'u_id': user1_id,
                'permission_id': GLOBAL_MEMBER})

    assert(resp.status_code == 400)
