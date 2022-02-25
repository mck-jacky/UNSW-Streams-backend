

import pytest
import requests
import json
from src import config
import jwt
import src.other

from tests.helpers import post_channel_invite, post_message_send, post_dm_create, \
                          SUCCESS, ACCESS_ERROR, INPUT_ERROR
from tests.fixtures import init_users, init_channel_id, init_dm_id

def get_notifications(token):
    return requests.get(config.url + 'notifications/get/v1',
                        params={'token':token})

@pytest.fixture
def init_notifications(init_users, init_channel_id):
    """
    User 3 will receive the following notifications:
    1. "lukeskywalker added you to channel1"
    2. "lukeskywalker added you to channel2"
    3. "lukeskywalker added you to channel3"
    4. "lukeskywalker added you to anakinskywalker, hansolo, lukeskywalker"
    5. "lukeskywalker added you to anakinskywalker, lukeskywalker"
    6. "lukeskywalker tagged you in channel3: @anakinskywalker!"
    7. "lukeskywalker tagged you in channel2: Good evening @anakin"
    
    User 2 will receive:
    1. "lukeskywalker added you to anakinskywalker, hansolo, lukeskywalker"
    
    User 1 recieves no notifications.
    """

    resp = post_channel_invite(init_users['token'][1], init_channel_id[1], init_users['user_id'][3])
    
    resp = post_channel_invite(init_users['token'][1], init_channel_id[2], init_users['user_id'][3])
    
    resp = post_channel_invite(init_users['token'][1], init_channel_id[3], init_users['user_id'][3])
    

    resp = post_dm_create(init_users['token'][1], [init_users['user_id'][2], init_users['user_id'][3]])
    dm_1 = json.loads(resp.text)
    resp = post_dm_create(init_users['token'][1], [init_users['user_id'][3]])
    dm_2 = json.loads(resp.text)
    # Dm 1 is called 'anakinskywalker, hansolo, lukeskywalker'
    # Dm 2 is called 'anakinskywalker, lukeskywalker'
    
    resp = post_message_send(init_users['token'][1], init_channel_id[3], "@anakinskywalker!")
    msg_1 = json.loads(resp.text)
    resp = post_message_send(init_users['token'][1], init_channel_id[2], "Good evening @anakinskywalker!")
    msg_2 = json.loads(resp.text)
    
    return {
        'channel_id': [0, init_channel_id[1], init_channel_id[2], init_channel_id[3]],
        'dm_id': [0, dm_1['dm_id'], dm_2['dm_id']],
        'message_id': [0, msg_1['message_id'], msg_2['message_id']]
    }

#@pytest.mark.skip
def test_return_20_max(init_users, init_channel_id): # Does not import init_notifications
    """
    Test if notifications/get returns a maximum of 20 messages.
    """
    post_channel_invite(init_users['token'][1], init_channel_id[3], init_users['user_id'][3])
    
    
    for i in range(25):
        post_message_send(init_users['token'][1], init_channel_id[3], f"{i + 1}. Hello @anakinskywalker!")
        
        
    resp = get_notifications(init_users['token'][3])
    assert resp.status_code == SUCCESS
    resp_data = json.loads(resp.text)['notifications']
    
    assert len(resp_data) == 20
    assert resp_data[0]["notification_message"] == "lukeskywalker tagged you in channel3: 25. Hello @anakinsky"
    assert resp_data[-1]["notification_message"] == "lukeskywalker tagged you in channel3: 6. Hello @anakinskyw"

#@pytest.mark.skip
def test_notifications_empty(init_users, init_notifications):
    """
    Test when a user's notifications are empty.
    """
    resp = get_notifications(init_users['token'][1])
    assert resp.status_code == SUCCESS
    resp_data = json.loads(resp.text)
    assert resp_data['notifications'] == []


def test_correct_order(init_users, init_notifications):
    """
    Test that the messages are returned from most recent to least recent.
    """
    # this is tested already. Implement if you feel like it
    pass


#@pytest.mark.skip
def test_channel_invite_notification(init_users, init_notifications):
    """
    Test if a user recieves the correct notification when they are added to a
    channel.
    """
    resp = get_notifications(init_users['token'][3])
    assert resp.status_code == SUCCESS
    resp_data = json.loads(resp.text)
    print(resp_data)
    assert resp_data['notifications'][-1] == {
        'channel_id': init_notifications['channel_id'][1],
        'dm_id': -1 ,
        'notification_message': "lukeskywalker added you to channel1"
    }
    

#@pytest.mark.skip
def test_tagging(init_users, init_notifications):
    """
    Test if a user recieves the correct notification when they are tagged in a
    message. Also tests if tagging returns 20 chars only
    """
    resp = get_notifications(init_users['token'][3])
    assert resp.status_code == SUCCESS
    resp_data = json.loads(resp.text)
    assert resp_data['notifications'][1] == {
        'channel_id': init_notifications['channel_id'][3],
        'dm_id': -1 ,
        'notification_message': "lukeskywalker tagged you in channel3: @anakinskywalker!"
    }
    assert resp_data['notifications'][0] == {
        'channel_id': init_notifications['channel_id'][2],
        'dm_id': -1 ,
        'notification_message': "lukeskywalker tagged you in channel2: Good evening @anakin"
    }

#@pytest.mark.skip
def test_dm_create_notification(init_users, init_notifications):
    """
    Test if a user recieves the correct notification when they are added to a dm.
    """
    resp = get_notifications(init_users['token'][2])
    assert resp.status_code == SUCCESS
    resp_data = json.loads(resp.text)
    assert resp_data['notifications'] == [
        {
            'channel_id': -1,
            'dm_id': init_notifications['dm_id'][1],
            'notification_message': "lukeskywalker added you to anakinskywalker, hansolo, lukeskywalker"
        }
    ]
    pass

#@pytest.mark.skip
def test_react_notification(init_users, init_notifications):
    """
    Test if a user recieves the correct notification when their message recieves
     a react.
    """
    requests.post(config.url + 'message/react/v1',
                  json = {
                    'token': init_users['token'][3],
                    'message_id': init_notifications['message_id'][1],
                    'react_id': 1
                  }
              )
    resp = get_notifications(init_users['token'][1])
    resp_data = json.loads(resp.text)
    assert resp_data['notifications'] == [
        {
            'channel_id': init_notifications['channel_id'][3],
            'dm_id': -1,
            'notification_message': "anakinskywalker reacted to your message in channel3" 
        }
    ]

