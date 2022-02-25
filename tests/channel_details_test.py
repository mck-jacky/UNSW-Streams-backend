# Tests for channels_details_v1 function
# Written by Andy Wu z5363503

import pytest

from src.error import InputError, AccessError
from src.channels import channels_create_v1
from src.other import clear_v1
from src.auth import auth_register_v1
from src.channel import channel_details_v1, channel_join_v1

# InputError when any of:
#     - channel_id does not refer to a valid channel
# AccessError when any of: 
#     - channel_id is valid but the authorised user is not a member of the channel

# Clears list of users and channels, registers 3 users, creates 3 channels
@pytest.fixture
def clear_and_create_users_and_channels():
    clear_v1()
    auth_register_v1("hellothere@gmail.com", "thisismypassword", "Luke", "Skywalker")
    auth_register_v1("helloagain@gmail.com", "newpassword", "Han", "Solo")
    auth_register_v1("myemail@hotmail.com", "insanepassword", "Anakin", "Skywalker")

    channels_create_v1(1, "General", True)
    channels_create_v1(2, "Discussions", True)
    channels_create_v1(3, "Ideas", False)

# InputError - channel_id does not refer to a valid channel
def test_channel_details_v1_invalid_channel_id(clear_and_create_users_and_channels):
    with pytest.raises(InputError):
        assert channel_details_v1(1, 4)

# # AccessError - auth_user_id does not belong to any user's id
# def test_channel_details_v1_invalid_user():
#     with pytest.raises(AccessError):
#         assert channel_details_v1(53, 2)
        
# AccessError - channel_id is valid but the authorised user is not a member of the channel
def test_channel_details_v1_non_member_(clear_and_create_users_and_channels):
    with pytest.raises(AccessError):
        assert channel_details_v1(1, 2)

# Testing simple valid case - No channel_join function used
def test_channel_details_v1_no_join(clear_and_create_users_and_channels):
    assert channel_details_v1(1, 1) == {
        'name': "General",
        'is_public': True,
        'owner_members': [
            {
                'u_id': 1,
                'email': "hellothere@gmail.com",
                'name_first': "Luke",
                'name_last': "Skywalker",
                'handle_str': "lukeskywalker",
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'email': "hellothere@gmail.com",
                'name_first': "Luke",
                'name_last': "Skywalker",
                'handle_str': "lukeskywalker",
            }
        ]
    }
    assert channel_details_v1(3, 3) == {
        'name': "Ideas",
        'is_public': False,
        'owner_members': [
            {
                'u_id': 3,
                'email': "myemail@hotmail.com",
                'name_first': "Anakin",
                'name_last': "Skywalker",
                'handle_str': "anakinskywalker",
            }
        ],
        'all_members': [
            {
                'u_id': 3,
                'email': "myemail@hotmail.com",
                'name_first': "Anakin",
                'name_last': "Skywalker",
                'handle_str': "anakinskywalker",
            }
        ]
    }

# Testing simple valid case - channel_join function used
def test_channel_details_v1_join(clear_and_create_users_and_channels):
    channel_join_v1(1, 2)
    channel_join_v1(3, 2)

    assert channel_details_v1(3, 2) == {
        'name': "Discussions",
        'is_public': True,
        'owner_members': [
            {
                'u_id': 2,
                'email': "helloagain@gmail.com",
                'name_first': "Han",
                'name_last': "Solo",
                'handle_str': "hansolo",
            }
        ],
        'all_members': [
            {
                'u_id': 2,
                'email': "helloagain@gmail.com",
                'name_first': "Han",
                'name_last': "Solo",
                'handle_str': "hansolo",
            },
            {
                'u_id': 1,
                'email': "hellothere@gmail.com",
                'name_first': "Luke",
                'name_last': "Skywalker",
                'handle_str': "lukeskywalker",
            },
            {
                'u_id': 3,
                'email': "myemail@hotmail.com",
                'name_first': "Anakin",
                'name_last': "Skywalker",
                'handle_str': "anakinskywalker",
            }
        ]
    }

# Extra tests from Botan

def test_password_key_missing():
    """
    Test whether the password key is not present in the return dictionary.
    """
    
    clear_v1()
    auth_register_v1("e1@m.com", "password1", "NF1", "NL1")
    channels_create_v1(1, "AAA", True)
    detail_of_channel = channel_details_v1(1, 1)

    assert("password" not in detail_of_channel)

def test_number_of_keys():
    """
    Test whether the number of keys (not the name specifically) in the return
    dictionary matches the specifications (i.e. 4).
    """
    
    clear_v1()
    auth_register_v1("e1@m.com", "password1", "NF1", "NL1")
    channels_create_v1(1, "AAA", True)
    detail_of_channel = channel_details_v1(1, 1)

    assert(len(detail_of_channel.keys()) == 4)

def test_correct_key_names():
    """
    Test whether the key names in the return dictionary match the
    specifications.
    """
    
    clear_v1()
    auth_register_v1("e1@m.com", "password1", "NF1", "NL1")
    channels_create_v1(1, "AAA", True)
    detail_of_channel = channel_details_v1(1, 1)

    correct_key_names = ["name", "is_public", "owner_members", "all_members"]

    for key in detail_of_channel:
        assert(key in correct_key_names)

def test_correct_channel_detail_return():
    """
    Test whether the correct channel information of a valid user/valid channel
    is returned. I.e.:
    
    1. Create user1
    2. User1 creates channel1
    3. User1 joins channel1
    4. Call channel_details_v1() to see if the return matches expected return.
    """
    
    clear_v1()
    auth_register_v1("e1@m.com", "password1", "NF1", "NL1")
    channels_create_v1(1, "AAA", True)
    detail_of_channel = channel_details_v1(1, 1)

    # Sorry about the horizontal code length
    expected_return = {'name': 'AAA',
                       'is_public': True,
                       'owner_members':
                       [{'u_id': 1, 'email': 'e1@m.com', 'name_first': 'NF1', 'name_last': 'NL1', 'handle_str': 'nf1nl1'}],
                       'all_members':
                       [{'u_id': 1, 'email': 'e1@m.com', 'name_first': 'NF1', 'name_last': 'NL1', 'handle_str': 'nf1nl1'}]}

    assert(detail_of_channel == expected_return)
