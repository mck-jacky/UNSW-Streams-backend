# """
# Pytest for the dm_messages_v1() function.
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
#         assert(src.dm.dm_messages_v1("nonexistent_user", 1, 1))

# def test_valid_user_invalid_dm_id(clear_and_create_new_values):
#     """
#     Test whether an InputError is raised when an invalid dm_id is given with a
#     valid user.
#     """

#     # [user1, user2, user3, dm1, dm2]
#     # [1, 2, 3, {'dm_id': 1}, {'dm_id': 2}]
#     fixList = clear_and_create_new_values

#     with pytest.raises(InputError):
#         assert(src.dm.dm_messages_v1(fixList[0], -1, 1))
