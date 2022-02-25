# A file to test the search/v1 route. Written by Alex Hunter z5312469, Nov 2021


import pytest
import requests
import json
from src import config
import jwt
from tests.helpers import SUCCESS, ACCESS_ERROR, INPUT_ERROR
from tests.fixtures import alex_init, init_users, init_channel_id, init_dm_id, init_msg_id

def get_search(token, query):
    return requests.get(config.url + 'search/v1',
                        params={'token': token, 'query_str': query})

# Input errors:
#@pytest.mark.skip
def test_query_empty(init_users, init_channel_id, init_dm_id, init_msg_id):
    resp = get_search(init_users['token'][1], "")
    assert resp.status_code == INPUT_ERROR
    pass

#@pytest.mark.skip
def test_query_over_1000_chars(init_users, init_channel_id, init_dm_id, init_msg_id):

    chars_20 = "abcdefghij1234567890"
    assert len(chars_20) == 20
    chars_100 = chars_20 * 5
    query_1000_chars = chars_100 * 10
    assert len(query_1000_chars) == 1000
    query_1001_chars = query_1000_chars + "a"

    resp = get_search(init_users['token'][1], query_1000_chars)
    assert resp.status_code == SUCCESS
    
    resp = get_search(init_users['token'][1], query_1001_chars)
    assert resp.status_code == INPUT_ERROR
    
    pass

# Other:
#@pytest.mark.skip
def test_success_across_channels_and_dms(init_users, init_channel_id, init_dm_id, init_msg_id):
    
    resp = get_search(init_users['token'][1], "Gday")
    assert resp.status_code == SUCCESS
    resp_data = json.loads(resp.text)
    
    for message in resp_data['messages']:
        if "Gday" not in message['message']:
            assert False

    assert len(resp_data['messages']) == 5
    
#@pytest.mark.skip
def test_success_across_channels(init_users, init_channel_id, init_dm_id, init_msg_id):
    resp = get_search(init_users['token'][1], "channel")
    assert resp.status_code == SUCCESS
    resp_data = json.loads(resp.text)
    
    for message in resp_data['messages']:
        if "channel" not in message['message']:
            assert False

    assert len(resp_data['messages']) == 5
    
#@pytest.mark.skip
def test_success_across_dms(init_users, init_channel_id, init_dm_id, init_msg_id):
    """
    Test if successful across multiple dms
    """
    resp = get_search(init_users['token'][1], "dm")
    assert resp.status_code == SUCCESS
    resp_data = json.loads(resp.text)
    
    for message in resp_data['messages']:
        if "dm" not in message['message']:
            assert False

    assert len(resp_data['messages']) == 6

#@pytest.mark.skip
def test_single_message(init_users, init_channel_id, init_dm_id, init_msg_id):
    """
    Test if it can return a single message.
    """
    resp = get_search(init_users['token'][1], "hello channel 1!")
    assert resp.status_code == SUCCESS
    resp_data = json.loads(resp.text)
    
    for message in resp_data['messages']:
        if "hello channel 1!" not in message['message']:
            assert False

    assert len(resp_data['messages']) == 1
    
    resp = get_search(init_users['token'][1], "hello dm")
    assert resp.status_code == SUCCESS
    resp_data = json.loads(resp.text)
    
    for message in resp_data['messages']:
        if "hello dm" not in message['message']:
            assert False

    assert len(resp_data['messages']) == 1

#@pytest.mark.skip
def test_no_matches(init_users, init_channel_id, init_dm_id, init_msg_id):
    """
    Test the case where the query matches no messages
    """
    resp = get_search(init_users['token'][1], "i never said this!")
    assert resp.status_code == SUCCESS
    resp_data = json.loads(resp.text)
    assert resp_data['messages'] == []

#@pytest.mark.skip
def test_left_dm_messages(init_users, init_channel_id, init_dm_id, init_msg_id):
    """
    Test whether it returns messages from dms which the user has left
    """
    # Leave dm 3
    resp = requests.post(config.url + 'dm/leave/v1',
                         json={'token': init_users['token'][1],
                               'dm_id': init_dm_id[3]})
    assert resp.status_code == SUCCESS
    # Search for "Gday dm 3!" message
    resp = get_search(init_users['token'][1], "Gday")
    assert resp.status_code == SUCCESS
    resp_data = json.loads(resp.text)
    print(resp_data['messages'])
    
    assert len(resp_data['messages']) == 4 # Usually would be 5
    
    for message in resp_data['messages']:
        #if "Gday dm 3!" in message['message']:
        #    assert False
        assert "Gday dm 3!" not in message['message']

    pass

#@pytest.mark.skip
def test_left_channel_messages(init_users, init_channel_id, init_dm_id, init_msg_id):
    """
    Test whether it returns messages from channels which the user has left
    """
    # Leave channel 3
    resp = requests.post(config.url + 'channel/leave/v1',
                         json={'token': init_users['token'][1],
                               'channel_id': init_channel_id[3]})
    # Search for "Gday channel 3!" message
    resp = get_search(init_users['token'][1], "Gday")
    assert resp.status_code == SUCCESS
    resp_data = json.loads(resp.text)
    
    for message in resp_data['messages']:
        if "Gday channel 3!" in message['message']:
            assert False
            
    assert len(resp_data['messages']) == 4 # Usually would be 5
    
#@pytest.mark.skip   
def test_removed_messages(init_users, init_channel_id, init_dm_id, init_msg_id):
    """
    Test whether it returns messages which have been removed
    """
    # Remove "Gday dm 3! from dm 3
    resp = requests.delete(config.url + 'message/remove/v1',
                         json={'token': init_users['token'][1],
                               'message_id': init_msg_id[7]})
    # Search for "Gday dm 3!" message
    resp = get_search(init_users['token'][1], "Gday")
    assert resp.status_code == SUCCESS
    resp_data = json.loads(resp.text)
    
    for message in resp_data['messages']:
        #if "Gday dm 3!" in message['message']:
        #    assert False
        assert not ("Gday dm 3!" in message['message'])

    assert len(resp_data['messages']) == 4 # Usually would be 5
    
#@pytest.mark.skip   
def test_removed_user(init_users, init_channel_id, init_dm_id, init_msg_id):
    """
    If a removed user does a search, it should return an access error, as the
    token is no longer valid.
    """
    # Make user 3 a global owner
    requests.post(config.url + 'admin/userpermission/change/v1',
                  json={'token': init_users['token'][1],
                        'u_id': init_users['user_id'][3],
                        'permission_id': 1}) # GLOBAL_OWNER
    # Remove user 1
    resp = requests.delete(config.url + 'admin/user/remove/v1',
                         json={'token': init_users['token'][3],
                               'u_id': init_users['user_id'][1]})
    # User 1 tries to search
    resp = get_search(init_users['token'][1], "Gday")
    assert resp.status_code == ACCESS_ERROR
    
    pass

#@pytest.mark.skip
def test_return_format(init_users, init_channel_id, init_dm_id, init_msg_id):
    """
    Test if it returns a "List of dictionaries, where each dictionary contains
    types { message_id, u_id, message, time_created, reacts, is_pinned"  }
    """
    resp = get_search(init_users['token'][1], "channel")
    assert resp.status_code == SUCCESS
    resp_data = json.loads(resp.text)
    
    assert type(resp_data) == dict
    
    assert type(resp_data['messages']) == list
    
    for message in resp_data['messages']:
        assert type(message['message_id']) == int
        assert type(message['u_id']) == int
        assert type(message['message']) == str
        assert type(message['time_created']) in (int, float)
        assert type(message['reacts']) == list
        assert type(message['is_pinned']) == bool
        
        for react in message['reacts']:
            assert type(react['react_id']) == int
            assert type(react['u_ids']) == list
            assert type(react['is_this_user_reacted']) == bool



















