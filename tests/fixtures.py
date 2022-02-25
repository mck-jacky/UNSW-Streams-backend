# A document to store fixtures which are reused.

import pytest
import requests
import json
from src import config
import jwt
import src.other

@pytest.fixture
def init_users():
    """
    Initialise 3 users. User 1 is a global owner.
    
    User 1 handle: lukeskywalker
    User 2 handle: hansolo
    User 3 handle: anakinskywalker
    
    return a dictionary: 
    {
        'token':[0, token_1, token_2, token_3],
        'user_id':[0, user_id_1, user_id_2, user_id_3] 
    }
    """
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

    token_1 = json.loads(user_1.text)['token']
    token_2 = json.loads(user_2.text)['token']
    token_3 = json.loads(user_3.text)['token']
    
    user_id_1 = int(jwt.decode(token_1, src.other.SUPERSECRETPASSWORD, algorithms=["HS256"])['auth_user_id'])
    user_id_2 = int(jwt.decode(token_2, src.other.SUPERSECRETPASSWORD, algorithms=["HS256"])['auth_user_id'])
    user_id_3 = int(jwt.decode(token_3, src.other.SUPERSECRETPASSWORD, algorithms=["HS256"])['auth_user_id'])

    return {
        'token':[0, token_1, token_2, token_3],
        'user_id':[0, user_id_1, user_id_2, user_id_3] 
    }

@pytest.fixture
def init_channel_id(init_users):
    """
    Initialises 3 channels.
    Channel3 is private
    user_id_1 is an owner of channel 1, 2 and 3. Also a global owner
    user_id_2 and 3 are not in any channels.
    
    Return: [0, channel_id_1, channel_id_2, channel_id_3] 
    """
    channel_1 = requests.post(config.url + 'channels/create/v2',
                             json={'token': init_users['token'][1], 'name': "channel1", 'is_public': True})
    channel_2 = requests.post(config.url + 'channels/create/v2',
                             json={'token': init_users['token'][1], 'name': "channel2", 'is_public': True})
    channel_3 = requests.post(config.url + 'channels/create/v2',
                             json={'token': init_users['token'][1], 'name': "channel3", 'is_public': False})
    
    channel_id_1 = json.loads(channel_1.text)['channel_id']
    channel_id_2 = json.loads(channel_2.text)['channel_id']
    channel_id_3 = json.loads(channel_3.text)['channel_id']
    
    return [0, channel_id_1, channel_id_2, channel_id_3]
    
@pytest.fixture
def init_dm_id(init_users):
    """
    Initialises 3 dms.
    dm 1: user 1 is an owner, user 3 is a member
    dm 2: user 2 is an owner, user 1 and 3 are members
    dm 3: user 1 is an owner, user 2 is a member.
    
    return: dm_ids = [0, dm_id_1, dm_id_2, dm_id_3]
    """

    dm_ids = [0]

    resp = requests.post(config.url + 'dm/create/v1',
                        json = {'token': init_users['token'][1],
                                'u_ids': [init_users['user_id'][3]]
                               })
    dm_ids.append(json.loads(resp.text)['dm_id'])
    
    resp = requests.post(config.url + 'dm/create/v1',
                        json = {'token': init_users['token'][2],
                                'u_ids': [init_users['user_id'][1], init_users['user_id'][3]]
                               })
    dm_ids.append(json.loads(resp.text)['dm_id'])
    
    resp = requests.post(config.url + 'dm/create/v1',
                        json = {'token': init_users['token'][1],
                                'u_ids': [init_users['user_id'][2]]
                               })
    dm_ids.append(json.loads(resp.text)['dm_id'])
    
    return dm_ids

@pytest.fixture
def init_msg_id(init_users, init_channel_id, init_dm_id):
    """
    Initialise messages from user 1 in channel 1/2/3 and dm 1/2/3
    
    Return a list: [0, msg_id_1, msg_id_2, ... ,msg_id_9]
    """
    message_ids = [0]
    # msg id 1
    resp = requests.post(config.url + 'message/send/v1',
                         json={'token': init_users['token'][1],
                               'channel_id': init_channel_id[1],
                               'message': "hello channel 1!"})
    message_ids.append(json.loads(resp.text)['message_id'])
    # msg id 2
    resp = requests.post(config.url + 'message/send/v1',
                         json={'token': init_users['token'][1],
                               'channel_id': init_channel_id[1],
                               'message': "Gday channel 1!"})
    message_ids.append(json.loads(resp.text)['message_id'])
    # msg id 3
    resp = requests.post(config.url + 'message/send/v1',
                         json={'token': init_users['token'][1],
                               'channel_id': init_channel_id[3],
                               'message': "Gday channel 3!"})
    message_ids.append(json.loads(resp.text)['message_id'])
    # msg id 4
    resp = requests.post(config.url + 'message/send/v1',
                         json={'token': init_users['token'][1],
                               'channel_id': init_channel_id[2],
                               'message': "Good morning channel 2!"})
    message_ids.append(json.loads(resp.text)['message_id'])
    # msg id 5
    resp = requests.post(config.url + 'message/senddm/v1',
                         json={'token': init_users['token'][1],
                               'dm_id': init_dm_id[1],
                               'message': "hello dm 1!"})
    message_ids.append(json.loads(resp.text)['message_id'])   
    # msg id 6
    resp = requests.post(config.url + 'message/senddm/v1',
                         json={'token': init_users['token'][1],
                               'dm_id': init_dm_id[1],
                               'message': "Gday dm 1!"})
    message_ids.append(json.loads(resp.text)['message_id'])
    # msg id 7
    resp = requests.post(config.url + 'message/senddm/v1',
                         json={'token': init_users['token'][1],
                               'dm_id': init_dm_id[3],
                               'message': "Gday dm 3!"})
    message_ids.append(json.loads(resp.text)['message_id'])
    # msg id 8
    resp = requests.post(config.url + 'message/senddm/v1',
                         json={'token': init_users['token'][1],
                               'dm_id': init_dm_id[2],
                               'message': "Good morning dm 2!"})
    message_ids.append(json.loads(resp.text)['message_id'])
    # msg id 9
    resp = requests.post(config.url + 'message/senddm/v1',
                         json={'token': init_users['token'][1],
                               'dm_id': init_dm_id[1],
                               'message': "Good evening dm 1!"})
    message_ids.append(json.loads(resp.text)['message_id'])
    
    # USER 2 SENDS SOME MESSAGES
    # msg id 10
    resp = requests.post(config.url + 'message/senddm/v1',
                         json={'token': init_users['token'][2],
                               'dm_id': init_dm_id[2],
                               'message': "Gday from User 2 dm 2!"})
    message_ids.append(json.loads(resp.text)['message_id'])
    
    # user 2 joins channel 3
    requests.post(
            config.url + 'channel/invite/v2',
            json = {
                'token': init_users['token'][1], 
                'channel_id': init_channel_id[3],
                'u_id': init_users['user_id'][2]
            }
        )
    
    # msg id 11
    resp = requests.post(config.url + 'message/send/v1',
                         json={'token': init_users['token'][2],
                               'channel_id': init_channel_id[3],
                               'message': "Good morning from User 2 channel 3!"})
    message_ids.append(json.loads(resp.text)['message_id'])
    
    return message_ids

@pytest.fixture
def alex_init():
    """
    Initialise 3 users and 3 channels.
    
    channel3 is private
    user_id_1 is an owner of channel 1, 2 and 3. Also a global owner
    user_id_2 and 3 are not in any channels.
    
    returns a dictionary:
    {
        'token':[0, token_1, token_2, token_3],
        'user_id':[0, user_id_1, user_id_2, user_id_3],
        'channel_id': [0, channel_id_1, channel_id_2, channel_id_3]   
    }
    (first element is set as a dummy variable so that I can access the elements
    with the corresponding number. E.g. ['token'][1] == token_1)
    """
    

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

    token_1 = json.loads(user_1.text)['token']
    token_2 = json.loads(user_2.text)['token']
    token_3 = json.loads(user_3.text)['token']

    
    user_id_1 = int(jwt.decode(token_1, src.other.SUPERSECRETPASSWORD, algorithms=["HS256"])['auth_user_id'])
    user_id_2 = int(jwt.decode(token_2, src.other.SUPERSECRETPASSWORD, algorithms=["HS256"])['auth_user_id'])
    user_id_3 = int(jwt.decode(token_3, src.other.SUPERSECRETPASSWORD, algorithms=["HS256"])['auth_user_id'])

    
    channel_1 = requests.post(config.url + 'channels/create/v2',
                             json={'token': token_1, 'name': "channel1", 'is_public': True})
    channel_2 = requests.post(config.url + 'channels/create/v2',
                             json={'token': token_1, 'name': "channel2", 'is_public': True})
    channel_3 = requests.post(config.url + 'channels/create/v2',
                             json={'token': token_1, 'name': "channel3", 'is_public': False})
    
    channel_id_1 = json.loads(channel_1.text)['channel_id']
    channel_id_2 = json.loads(channel_2.text)['channel_id']
    channel_id_3 = json.loads(channel_3.text)['channel_id']
    
    return {
        'token':[0, token_1, token_2, token_3],
        'user_id':[0, user_id_1, user_id_2, user_id_3],
        'channel_id': [0, channel_id_1, channel_id_2, channel_id_3]   
    }
    # set first element as a dummy variable so that I can access the elements
    # with the corresponding number. E.g. ['token'][1] == token_1

@pytest.fixture
def jacky_init():

    requests.delete(config.url + 'clear/v1')

    user_1 = requests.post(config.url + 'auth/register/v2', json={'email': 'email1@gmail.com', 'password': 'password', 'name_first': 'name_first1', 'name_last': 'name_last1'})
    user_2 = requests.post(config.url + 'auth/register/v2', json={'email': 'email2@gmail.com', 'password': 'password', 'name_first': 'name_first2', 'name_last': 'name_last2'})
    user_3 = requests.post(config.url + 'auth/register/v2', json={'email': 'email3@gmail.com', 'password': 'password', 'name_first': 'name_first3', 'name_last': 'name_last3'})
    
    token_1 = json.loads(user_1.text)['token']
    token_2 = json.loads(user_2.text)['token']
    token_3 = json.loads(user_3.text)['token']

    user_id_1 = int(jwt.decode(token_1, src.other.SUPERSECRETPASSWORD, algorithms=["HS256"])['auth_user_id'])
    user_id_2 = int(jwt.decode(token_2, src.other.SUPERSECRETPASSWORD, algorithms=["HS256"])['auth_user_id'])
    user_id_3 = int(jwt.decode(token_3, src.other.SUPERSECRETPASSWORD, algorithms=["HS256"])['auth_user_id'])

    channel_1 = requests.post(config.url + 'channels/create/v2', json={'token': token_1, 'name': 'channel1', 'is_public': True})
    channel_id_1 = json.loads(channel_1.text)['channel_id']
    requests.post(config.url + 'channel/join/v2', json={'token': token_2, 'channel_id': channel_id_1})
    channel_2 = requests.post(config.url + 'channels/create/v2', json={'token': token_2, 'name': 'channel2', 'is_public': True})
    channel_id_2 = json.loads(channel_2.text)['channel_id']
    requests.post(config.url + 'channel/join/v2', json={'token': token_1, 'channel_id': channel_id_2})
    requests.post(config.url + 'channel/join/v2', json={'token': token_3, 'channel_id': channel_id_2})

    dm_1 = requests.post(config.url + 'dm/create/v1', json={'token': token_1, 'u_ids': [user_id_2]})
    dm_id_1 = json.loads(dm_1.text)['dm_id']
    dm_2 = requests.post(config.url + 'dm/create/v1', json={'token': token_2, 'u_ids': [user_id_1, user_id_3]})
    dm_id_2 = json.loads(dm_2.text)['dm_id']

    message_ids = [0]
    message_1 = requests.post(config.url + 'message/send/v1', json={'token': token_1, 'channel_id': channel_id_1, 'message': "hello world"})
    message_ids.append(json.loads(message_1.text)['message_id'])
    message_2 = requests.post(config.url + 'message/send/v1', json={'token': token_2, 'channel_id': channel_id_1, 'message': "hello world"})
    message_ids.append(json.loads(message_2.text)['message_id'])
    message_3 = requests.post(config.url + 'message/senddm/v1', json={'token': token_1, 'dm_id': dm_id_1, 'message': "hello world"})
    message_ids.append(json.loads(message_3.text)['message_id'])
    message_4 = requests.post(config.url + 'message/senddm/v1', json={'token': token_2, 'dm_id': dm_id_1, 'message': "hello world"})
    message_ids.append(json.loads(message_4.text)['message_id'])
    message_5 = requests.post(config.url + 'message/send/v1', json={'token': token_2, 'channel_id': channel_id_2, 'message': "hello world"})
    message_ids.append(json.loads(message_5.text)['message_id'])
    message_6 = requests.post(config.url + 'message/send/v1', json={'token': token_3, 'channel_id': channel_id_2, 'message': "hello world"})
    message_ids.append(json.loads(message_6.text)['message_id'])
    message_7 = requests.post(config.url + 'message/senddm/v1', json={'token': token_2, 'dm_id': dm_id_2, 'message': "hello world"})
    message_ids.append(json.loads(message_7.text)['message_id'])

    return {
        "token": [0, token_1, token_2, token_3],
        "user_id": [0, user_id_1, user_id_2, user_id_3],
        "channel_id": [0, channel_id_1, channel_id_2],
        "dm_id": [0, dm_id_1, dm_id_2],
        "messages": message_ids
    }

    # Channel_id_1 
    # owner: user_1(channel + global)
    # memeber: user_1, user_2
    # messages: message_id_1(Sent by user_1)
    #           message_id_2(Sent by user_2)

    # Channel_id_2
    # owner: user_2(channel), user_1(global)
    # memeber: user_1, user_2, user_3
    # messages: message_id_5(Sent by user_2)
    #           message_id_6(Sent by user_3)

    # dm_id_1
    # owner: user_1(dm)
    # member: user_1, user_2
    # messages: message_id_3(Sent by user_1)
    #           message_id_4(Sent by user_2)

    # dm_id_2
    # owner: user_2(dm)
    # memeber: user_1, user_2, user_3
    # messages: message_id_7(Sent by user_2)
