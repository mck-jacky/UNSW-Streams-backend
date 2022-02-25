# Tests for channels_create_v1 function
# Written by Andy Wu z5363503

import pytest

from src.error import InputError, AccessError
from src.channels import channels_create_v1
from src.other import clear_v1
from src.auth import auth_register_v1

# InputError when any of:
#     - Name of new channel is less than 1 character
#     - Name of new channel is more than 20 characters
#     - Name of new channel is the same name as an existing public/private channel
# AccessError when any of:
#     - auth_user_id does not belong to any user's id

# Clears list of users and channels, registers 3 new users
@pytest.fixture
def clear_and_register():
    clear_v1()
    auth_register_v1("hellothere@gmail.com", "thisismypassword", "Luke", "Skywalker")
    auth_register_v1("helloagain@gmail.com", "newpassword", "Han", "Solo")
    auth_register_v1("myemail@hotmail.com", "insanepassword", "Anakin", "Skywalker")

# # AccessError when auth_user_id does not belong to any user's id
# def test_channels_create_v1_invalid_user():
#     with pytest.raises(AccessError):
#         assert channels_create_v1(52, "Channel Name", True)

# Testing 1 character channel name 
def test_channels_create_v1_valid_short_name(clear_and_register):
    assert channels_create_v1(2, "K", True)["channel_id"] == 1

# InputError when user enters an empty name for new channel
def test_channels_create_v1_invalid_no_name(clear_and_register):
    with pytest.raises(InputError):
        assert channels_create_v1(3, "", True)

# InputError when user enters name of > 20 character for new channel
def test_channels_create_v1_invalid_long_name(clear_and_register):
    with pytest.raises(InputError):
        assert channels_create_v1(3, "This is a really long channel name and should be invalid.", True)

# Testing 20 character channel name
def test_channels_create_v1_invalid_20_char_name(clear_and_register):
    assert channels_create_v1(3, "Abetalipoproteinemia", True)["channel_id"] == 1

# InputError when user enters name of an existing channel
def test_channels_create_v1_existing_channel(clear_and_register):
    assert channels_create_v1(1, "General", True)["channel_id"] == 1
    assert channels_create_v1(2, "Discussions", True)["channel_id"] == 2
    assert channels_create_v1(3, "General", True)["channel_id"] == 3
    assert channels_create_v1(2, "Ideas", True)["channel_id"] == 4

# Testing simple valid cases
def test_channels_create_v1_simple(clear_and_register):
    assert channels_create_v1(1, "General", True)["channel_id"] == 1
    assert channels_create_v1(2, "Discussions", True)["channel_id"] == 2
    assert channels_create_v1(3, "Ideas", True)["channel_id"] == 3
    assert channels_create_v1(1, "Announcements", True)["channel_id"] == 4

# Extra tests from Botan

def test_correct_key_name():
    """
    Test whether correct key name "channel_id" is in the return dictionary.
    """
    
    clear_v1()
    auth_register_v1("e1@m.com", "password1", "NF1", "NL1")
    created_channel = channels_create_v1(1, "AAA", True)

    assert("channel_id" in created_channel)

def test_number_of_keys():
    """
    Test whether the number of keys (not the name specifically) in the return
    dictionary matches the specifications (i.e. 1).
    """
    
    clear_v1()
    auth_register_v1("e1@m.com", "password1", "NF1", "NL1")
    created_channel = channels_create_v1(1, "AAA", True)

    assert(len(created_channel.keys()) == 1)
