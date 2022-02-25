# """
# Pytest for the dm_list_v1() function.
# """

# import src.dm
# import pytest
# from src.auth import auth_register_v1
# from src.data_store import data_store
# from src.error import AccessError, InputError
# from src.other import clear_v1

# @pytest.fixture
# def clear_and_create_new_values():
#     """
#     1. Clears all existing details in data_store.
#     2. Creates three new users.
#     3. Creates a DM from user1 to user2 and from user1 to user2 and user3.
#     """
    
#     clear_v1()

#     user1 = auth_register_v1("e@mail1.com", "hunter1", "General", "Kenobi")\
#         ["auth_user_id"]
#     user2 = auth_register_v1("e@mail2.com", "hunter2", "Bold", "One")\
#         ["auth_user_id"]
#     user3 = auth_register_v1("e@mail3.com", "hunter3", "IAM", "THESENATE")\
#         ["auth_user_id"]

#     dm1 = src.dm.dm_create_v1(user1, [user2])
#     dm2 = src.dm.dm_create_v1(user1, [user2, user3])

#     # [1, 2, 3, {'dm_id': 1}, {'dm_id': 2}]
#     return [user1, user2, user3, dm1, dm2]

# def test_invalid_user(clear_and_create_new_values):
#     """
#     Test whether an invalid user raises an AccessError.
#     """

#     with pytest.raises(AccessError):
#         assert(src.dm.dm_list_v1("nonexistent_user"))

# def test_valid_user_no_dms(clear_and_create_new_values):
#     """
#     If user not owner or member of a DM, but is a valid user.
#     Should return a dictionary of this format: {'dms': []}.
#     """

#     expected_return = {'dms': []}

#     user4 = auth_register_v1("e@mail4.com", "hunter4", "Anakin", "Skywalker")\
#         ["auth_user_id"]

#     assert(src.dm.dm_list_v1(user4) == expected_return)

# def test_valid_user_part_of_dm(clear_and_create_new_values):
#     """
#     Test whether the length of a one-on-one DM is two (because the members list
#     of a DM contains both the receiver(s) and the owner.)
#     """

#     # [user1, user2, user3, dm1, dm2]
#     # [1, 2, 3, {'dm_id': 1}, {'dm_id': 2}]
#     fixList = clear_and_create_new_values 

#     user1_dm_dict = src.dm.dm_list_v1(fixList[0])
#     user1_dm_dict_len = len(user1_dm_dict['dms'])

#     assert(user1_dm_dict_len == 2)  # user1 is part of 2 DMs

#     user3_dm_dict = src.dm.dm_list_v1(fixList[2])
#     user3_dm_dict_len = len(user3_dm_dict['dms'])

#     assert(user3_dm_dict_len == 1)  # user3 is part of 1 DM
