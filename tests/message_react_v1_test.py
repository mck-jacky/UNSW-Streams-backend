import pytest

from src.error import AccessError, InputError
from src.other import clear_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.message import message_send_v1, message_edit_v1, message_senddm_v1, message_react_v1
from src.dm import dm_create_v1
from src.data_store import data_store
from src.channel import channel_join_v1
import requests
import json
from src import config

"""
InputError when any of:

    - message_id is not a valid message within a channel or DM that the authorised user has joined
    - react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1
    - the message already contains a react with ID react_id from the authorised user

"""

@pytest.fixture
def initialize():
    clear_v1()
    global user_1
    global user_2
    global user_3
    user_1 = auth_register_v1("email1@gmail.com", "password", "name_first1", "name_last1")["auth_user_id"]
    user_2 = auth_register_v1("email2@gmail.com", "password", "name_first2", "name_last2")["auth_user_id"]
    user_3 = auth_register_v1("email3@gmail.com", "password", "name_first3", "name_last3")["auth_user_id"]
    global channel_id_1
    channel_id_1 = channels_create_v1(user_1, "channel1", True)['channel_id']
    channel_join_v1(user_2, channel_id_1)

    global message_id_1
    global message_id_2
    message_id_1 = message_send_v1(user_1, channel_id_1, "hello world")["message_id"]
    message_id_2 = message_send_v1(user_2, channel_id_1, "hello")["message_id"]

    global dm_id_1
    dm_id_1 = dm_create_v1(user_1, [user_2])["dm_id"]
    
    global message_id_3
    global message_id_4
    message_id_3 = message_senddm_v1(user_1, dm_id_1, "hi")["message_id"]
    message_id_4 = message_senddm_v1(user_2, dm_id_1, "hihi")["message_id"]

    global LIKE 
    LIKE = 1

def test_message_id_invalid(initialize):
    # message_id is not a valid message within a channel or DM that the authorised user has joined
    with pytest.raises(InputError):
        message_react_v1(user_3, message_id_1, LIKE)
    with pytest.raises(InputError):
        message_react_v1(user_3, message_id_2, LIKE)
    with pytest.raises(InputError):
        message_react_v1(user_3, message_id_3, LIKE)
    with pytest.raises(InputError):
        message_react_v1(user_3, message_id_4, LIKE)

def test_invalid_react_id(initialize):
    # react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1
    with pytest.raises(InputError):
        message_react_v1(user_1, message_id_1, 2)
    with pytest.raises(InputError):
        message_react_v1(user_1, message_id_2, 3)
    with pytest.raises(InputError):
        message_react_v1(user_2, message_id_3, 4)
    with pytest.raises(InputError):
        message_react_v1(user_2, message_id_4, 5)

def test_already_reacted(initialize):
    # the message already contains a react with ID react_id from the authorised user
    message_react_v1(user_1, message_id_1, LIKE)
    with pytest.raises(InputError):
        message_react_v1(user_1, message_id_1, LIKE)
    message_react_v1(user_2, message_id_3, LIKE)
    with pytest.raises(InputError):
        message_react_v1(user_2, message_id_3, LIKE)

def test_react_successfully(initialize):
    # message react successfully
    assert message_react_v1(user_1, message_id_1, LIKE) == {}
    assert message_react_v1(user_1, message_id_2, LIKE) == {}
    assert message_react_v1(user_1, message_id_3, LIKE) == {}
    assert message_react_v1(user_1, message_id_4, LIKE) == {}
    assert message_react_v1(user_2, message_id_1, LIKE) == {}
    assert message_react_v1(user_2, message_id_2, LIKE) == {}
    assert message_react_v1(user_2, message_id_3, LIKE) == {}
    assert message_react_v1(user_2, message_id_4, LIKE) == {}
    
    

