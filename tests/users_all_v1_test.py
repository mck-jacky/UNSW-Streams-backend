# import pytest

# from src.error import InputError, AccessError
# from src.other import clear_v1
# from src.auth import auth_register_v1
# from src.user import users_all_v1

# # AccessError when any of: 
# #     - auth_user_id is invalid

# # Clears and registers 3 new users
# @pytest.fixture
# def clear_and_register():
#     clear_v1()
#     auth_register_v1("hellothere@gmail.com", "thisismypassword", "Luke", "Skywalker")
#     auth_register_v1("helloagain@gmail.com", "newpassword", "Han", "Solo")
#     auth_register_v1("myemail@hotmail.com", "insanepassword", "Anakin", "Skywalker")

# # Testing simple case
# def test_simple(clear_and_register):
#     assert users_all_v1(1) == [
#         {
#             'u_id': 1,
#             'email': "hellothere@gmail.com",
#             'name_first': "Luke",
#             'name_last': "Skywalker",
#             'handle_str': "lukeskywalker",
#         },
#         {
#             'u_id': 2,
#             'email': "helloagain@gmail.com",
#             'name_first': "Han",
#             'name_last': "Solo",
#             'handle_str': "hansolo",
#         },
#         {
#             'u_id': 3,
#             'email': "myemail@hotmail.com",
#             'name_first': "Anakin",
#             'name_last': "Skywalker",
#             'handle_str': "anakinskywalker",
#         }
#     ]

# # # AccessError - auth_user_id does not belong to any user's id
# # def test_invalid_auth_id(clear_and_register):
# #     with pytest.raises(AccessError):
# #         assert users_all_v1(4)
    
# # # Testing when there are no users registered 
# # - commented out since in server token decryption will check if auth_user_id is valid (if no users, the auth_user_id is invalid)
# # def test_no_users():
# #     clear_v1()
# #     with pytest.raises(AccessError):
# #         assert users_all_v1(1)

# # Testing when there is only 1 user
# def test_only_one_user():
#     clear_v1()
#     auth_register_v1("hellothere@gmail.com", "thisismypassword", "Luke", "Skywalker")

#     assert users_all_v1(1) == [
#         {
#             'u_id': 1,
#             'email': "hellothere@gmail.com",
#             'name_first': "Luke",
#             'name_last': "Skywalker",
#             'handle_str': "lukeskywalker",
#         }
#     ]
