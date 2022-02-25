# """
# Pytest for the channels_list_v1() function.
# """

# import pytest
# from src.error import AccessError, InputError
# from src.auth import auth_register_v1
# from src.channels import channels_create_v1, channels_list_v1
# from src.channel import channel_join_v1
# from src.other import clear_v1

# # Global variables
# guser1 = -1

# @pytest.fixture
# def clear_and_create_new_values():
#     """
#     1. Clears all existing details in data_store.
#     2. Creates three new users.
#     3. Creates two new channels with user1 being the creator of.
#     4. User2 joins channel1 (public), and user3 joins channel2 (private).
#     """

#     # Clear existing data first
#     clear_v1()

#     # Create test users (email, password, name_first, name_last)
#     user1 = auth_register_v1("e@mail1.com", "hunter1", "General", "Kenobi")
#     user2 = auth_register_v1("e@mail2.com", "hunter2", "Bold", "One")
#     user3 = auth_register_v1("e@mail3.com", "hunter3", "IAM", "THESENATE")

#     # Create test channels (auth_user_id, name, is_public)
#     channel1 = channels_create_v1(user1["auth_user_id"], "channel1", True) 
#     channel2 = channels_create_v1(user1["auth_user_id"], "channel2", True) # @Botan i changed this from False to True

#     # Join other users to created channels
#     channel_join_v1(user2["auth_user_id"], channel1['channel_id'])
#     channel_join_v1(user3["auth_user_id"], channel2['channel_id'])

#     global guser1
#     guser1 = user1["auth_user_id"]

# def test_invalid_user(clear_and_create_new_values):
#     """
#     Test whether an invalid user raises an AccessError.
#     """

#     with pytest.raises(AccessError):
#         assert(channels_list_v1('nonexistent_user'))

# def test_is_dict(clear_and_create_new_values):
#     """
#     Test return type is a dictionary.
#     """

#     global guser1

#     assert(type(channels_list_v1(guser1)) is dict)

# def test_valid_user_no_channels(clear_and_create_new_values):
#     """
#     If user not owner or member, but is a valid user.
#     Should return a dictionary of this format: {'channels': []}.
#     """

#     expected_return = {'channels': []}

#     user4 = auth_register_v1("e@mail4.com", "hunter4", "Anakin", "Skywalker")

#     assert(channels_list_v1(user4["auth_user_id"]) == expected_return)

# def test_valid_user_part_of_channels(clear_and_create_new_values):
#     """
#     Input a valid user (user1 in this case), and should expect a return format
#     matching expected_return.
#     """

#     expected_return = {'channels': [{'channel_id': 1, 'name': 'channel1'},
#                                     {'channel_id': 2, 'name': 'channel2'}]}

#     global guser1
#     assert(channels_list_v1(guser1) == expected_return)
    
