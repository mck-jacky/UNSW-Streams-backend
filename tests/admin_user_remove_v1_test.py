# """
# Pytest for the admin_user_remove_v1() function.
# """

# import pytest
# from src.admin import admin_user_remove_v1
# from src.auth import auth_register_v1
# from src.dm import dm_create_v1
# from src.error import AccessError, InputError
# from src.other import clear_v1
# from src.user import user_profile_v1

# GLOBAL_OWNER = 1
# GLOBAL_MEMBER = 2

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

#     # [1, 2, 3]
#     return [user1, user2, user3]

# def test_invalid_user(clear_and_create_new_values):
#     """
#     Test whether an invalid user raises an InputError.
#     """

#     with pytest.raises(InputError):
#         assert(admin_user_remove_v1(-1, -1))

# def test_not_a_global_owner(clear_and_create_new_values):
#     """
#     Test whether a valid user, who is not a global owner, and tries to remove a
#     user, raises an AccessError.
#     """

#     # [user1, user2, user3]
#     # [1, 2, 3]
#     fixList = clear_and_create_new_values

#     with pytest.raises(AccessError):
#         assert(admin_user_remove_v1(fixList[1], fixList[2]))

# def test_global_owner_removing_himself(clear_and_create_new_values):
#     """
#     Test whether the only valid global owner left can remove himself. Should
#     raise an InputError.
#     """

#     # [user1, user2, user3]
#     # [1, 2, 3]
#     fixList = clear_and_create_new_values

#     # Global owner user1 trying to remove himself
#     with pytest.raises(InputError):
#         assert(admin_user_remove_v1(fixList[0], fixList[0]))

# def test_simple_user_removal_then_retrieve_profile(clear_and_create_new_values):
#     """
#     Test whether a global owner sucessfully removes a global member user. The
#     removed user should not be able to do things a member can do after removal.
#     """

#     # [user1, user2, user3]
#     # [1, 2, 3]
#     fixList = clear_and_create_new_values

#     # Global owner user1 removing user2
#     admin_user_remove_v1(fixList[0], fixList[1])

#     expected_return = {
#         'u_id': 2,
#         'email': '',
#         'name_first': 'Removed',
#         'name_last': 'user',
#         'handle_str': ''
#         }

#     # Updated profile of user2
#     assert(user_profile_v1(fixList[0], fixList[1]) == expected_return)

# def test_simple_user_removal_then_do_stuff(clear_and_create_new_values):
#     """
#     Test whether a global owner sucessfully removes a global member user. The
#     removed user should not be able to do things a member can do after removal.
#     """

#     # [user1, user2, user3]
#     # [1, 2, 3]
#     fixList = clear_and_create_new_values

#     # Global owner user1 removing user2
#     admin_user_remove_v1(fixList[0], fixList[1])

#     # user2 trying to create a DM with user3
#     with pytest.raises(InputError):
#         assert(dm_create_v1(fixList[1], [fixList[2]]))
#     """
#     Hmm... did not raise an error. We left the auth_user_id alone, but functions
#     only check for valid auth_user_id, so a removed user can still do stuff?
#     """
