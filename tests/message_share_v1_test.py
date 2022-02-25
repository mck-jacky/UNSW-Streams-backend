import pytest

from src.error import AccessError, InputError
from src.other import clear_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.message import message_send_v1, message_edit_v1, message_senddm_v1, message_react_v1, message_unreact_v1,\
                        message_pin_v1, message_unpin_v1, message_share_v1
from src.dm import dm_create_v1
from src.data_store import data_store
from src.channel import channel_join_v1
import requests
import json
from src import config

"""
InputError when any of:

    - both channel_id and dm_id are invalid
    - neither channel_id nor dm_id are -1
    - og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
    - length of message is more than 1000 characters

AccessError when:

    - the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and the authorised user 
    has not joined the channel or DM they are trying to share the message to
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
    global channel_id_2
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

def test_both_channel_and_dm_id_invalid(initialize):
    # both channel_id and dm_id are invalid
    with pytest.raises(InputError):
        message_share_v1(user_1, message_id_1, "", -1, -1)
    with pytest.raises(InputError):
        message_share_v1(user_2, message_id_5, "", 100, -1)
    with pytest.raises(InputError):
        message_share_v1(user_3, message_id_7, "", -1, -100)

def test_neither_negative_one(initialize):
    # neither channel_id nor dm_id are -1
    with pytest.raises(InputError):
        message_share_v1(user_1, message_id_1, "", channel_id_1, dm_id_1)
    with pytest.raises(InputError):
        message_share_v1(user_2, message_id_1, "testing", channel_id_2, dm_id_2)

def test_user_dont_have_permission_to_og_message(initialize):
    # og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
    with pytest.raises(InputError):
        message_share_v1(user_3, message_id_1, "", channel_id_2, -1)
    with pytest.raises(InputError):
        message_share_v1(user_3, message_id_3, "", -1, dm_id_2)

def test_length_of_msg_too_long(initialize):
    # length of message is more than 1000 characters
    with pytest.raises(InputError):
        message_share_v1(user_1, message_id_1, "6RHkMaUjBHhn6K9WKtI6MnEo7OziC06QJUYuYCh17aE\
        g6bxIXFk0CFdXCSn4iHxMo952QjvKGyKYKL1NDaWxf44CvXlsl8OmvyHAKUsMoh73vVbUkhUFwzl4RuujXAe2SRALNXuj1txlo7vJ\
        77b6g0GNyGvZbqOTpR5m6ezhrbgkLaYssYqytuxpac1sOvGerHpxQG7MgYZq25HxCTQkT4vGMh7M5EW6DubNGAgLxgSB3k5XIT5me\
        qrtU3amds6XPuTiX7IUBvxj8yiRU8ewL4lKEtuNN7Yspa4bmOm7HA3FRkoANQAKWpknhwQmWXzPTbJqO9z6k6bcraZlh7o1mqtVJw\
        eCTitHhWr0BOzOfo9KgzLuF6CFZxOcAWmiIKXqj7IWLzhXD2v9Df6colREbyXuYclLt0j4oDr7SVQpXpYiBrMmtOQtqnHA0rMaWwD\
        nNzvRtSRtD1egCjN3rtb90YnnD4ZzVazzRFYiVt2j7eBa6DQZAxflqYhuFcaybTWqlgoOLjdowyg5CJhMTLjNaCWDbCQ7fIHkeid3\
        OfWSkO8heBQ0uVA9UAymBF1cQ7pJ01CG7MbscR2LXgB82gPJSwdoxj3YH6fhsHL7WTZHI4zdWNxwDaFlPRGHDAov2WiJebxTK9ZMw\
        PwwW8jIU3FJdjAEV4PjUyDhX21Z2ZqPWm4fi9ENUxZN8wtOsVKxTiEDJqGVexyltkNAXenm9FqWuvD6cZZhnXOTE0bweeZATHUUNo\
        ulHcMJWkZGxISMayRTG5bvvxJZnktQnGXdskuSTkkS6H0WLVsiSJd73Gvlp5JuslU7n01Wur8YqnngaX0Xma8nDsSKuRcDZPJbx30\
        o5PEt80f2q6llHHFUULn9tgS7fvWK2h1ov4NUUtD9RATH1wmB3ySnfJmMKGElSHhUyJVX6odRKcBXndzJ9SNA5oqbce0k8hlz6Rmn\
        X8766BwGE4F2oFONn7ZABEodj6WyuxpmDjhLGDeXdVWhjIaCm", channel_id_2, -1)

def test_user_has_not_joined_the_channel_or_dm_they_are_trying_to_share_to(initialize):
    # the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and 
    # the authorised user has not joined the channel or DM they are trying to share the message to
    with pytest.raises(AccessError):
        message_share_v1(user_3, message_id_5, "", channel_id_1, -1)
    with pytest.raises(AccessError):
        message_share_v1(user_3, message_id_6, "testing", -1, dm_id_1)
    with pytest.raises(AccessError):
        message_share_v1(user_3, message_id_3, "hi", channel_id_1, -1)
    with pytest.raises(AccessError):
        message_share_v1(user_3, message_id_4, "", -1, dm_id_1)

def test_share_successfully(initialize):
    # channel to channel
    assert message_share_v1(user_1, message_id_1, "testing", channel_id_2, -1)["shared_message_id"] == 8
    # channel to dm
    assert message_share_v1(user_2, message_id_5, "", -1, dm_id_1)["shared_message_id"] == 9
    # dm to dm
    assert message_share_v1(user_3, message_id_7, "1", -1, dm_id_2)["shared_message_id"] == 10
    # dm to channel
    assert message_share_v1(user_2, message_id_4, "", channel_id_1, -1)["shared_message_id"] == 11

