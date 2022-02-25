import pytest

from src.error import AccessError, InputError
from src.other import clear_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.message import message_send_v1, message_senddm_v1, message_pin_v1, message_unpin_v1
from src.dm import dm_create_v1
from src.data_store import data_store
from src.channel import channel_join_v1

"""
InputError when any of:
      
    - message_id is not a valid message within a channel or DM that the authorised user has joined
    - the message is not already pinned
      
AccessError when:
      
    - message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM

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
    channel_id_2 = channels_create_v1(user_2, "channel2", True)['channel_id']
    channel_join_v1(user_2, channel_id_1)
    channel_join_v1(user_1, channel_id_2)
    channel_join_v1(user_3, channel_id_2)

    global message_id_1
    global message_id_2
    global message_id_3
    global message_id_4
    global message_id_5
    global message_id_6
    global message_id_7

    global dm_id_1
    global dm_id_2

    dm_id_1 = dm_create_v1(user_1, [user_2])["dm_id"]
    dm_id_2 = dm_create_v1(user_2, [user_1, user_3])["dm_id"]

    message_id_1 = message_send_v1(user_1, channel_id_1, "hello world")["message_id"]
    message_id_2 = message_send_v1(user_2, channel_id_1, "hello")["message_id"]
    message_id_3 = message_senddm_v1(user_1, dm_id_1, "hi")["message_id"]
    message_id_4 = message_senddm_v1(user_2, dm_id_1, "hihi")["message_id"]
    message_id_5 = message_send_v1(user_2, channel_id_2, "message from user2")["message_id"]
    message_id_6 = message_send_v1(user_3, channel_id_2, "message from user3")["message_id"]
    message_id_7 = message_senddm_v1(user_2, dm_id_2, "hello")["message_id"]

def test_message_id_invalid(initialize):
    # message_id is not a valid message within a channel or DM that the authorised user has joined
    with pytest.raises(InputError):
        message_unpin_v1(user_3, message_id_1)
    with pytest.raises(InputError):
        message_unpin_v1(user_3, message_id_2)
    with pytest.raises(InputError):
        message_unpin_v1(user_3, message_id_3)
    with pytest.raises(InputError):
        message_unpin_v1(user_3, message_id_4)

def test_message_is_not_already_pinned(initialize):
    # the message is not already pinned
    with pytest.raises(InputError):
        message_unpin_v1(user_1, message_id_1)
    with pytest.raises(InputError):
        message_unpin_v1(user_1, message_id_3)
    with pytest.raises(InputError):
        message_unpin_v1(user_1, message_id_5)

def test_user_dont_have_permission_to_unpin(initialize):
    # message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM
    message_pin_v1(user_1, message_id_1)
    with pytest.raises(AccessError):
        message_unpin_v1(user_2, message_id_1)
    message_pin_v1(user_1, message_id_3)
    with pytest.raises(AccessError):
        message_unpin_v1(user_2, message_id_3)
    message_pin_v1(user_1, message_id_5)
    with pytest.raises(AccessError):
        message_unpin_v1(user_3, message_id_5)
    message_pin_v1(user_2, message_id_7)
    with pytest.raises(AccessError):
        message_unpin_v1(user_1, message_id_7)

def test_user_unpin_successfully(initialize):
    assert message_pin_v1(user_1, message_id_1) == {}
    assert message_unpin_v1(user_1, message_id_1) == {}
    assert message_pin_v1(user_1, message_id_2) == {}
    assert message_unpin_v1(user_1, message_id_2) == {}
    assert message_pin_v1(user_1, message_id_6) == {}
    assert message_unpin_v1(user_1, message_id_6) == {}
    assert message_pin_v1(user_2, message_id_5) == {}
    assert message_unpin_v1(user_2, message_id_5) == {}
    assert message_pin_v1(user_2, message_id_7) == {}
    assert message_unpin_v1(user_2, message_id_7) == {}