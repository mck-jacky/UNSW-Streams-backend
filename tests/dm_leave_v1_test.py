# """
# Pytest for the dm_leave_v1() function.
# """

# import json
# import pytest
# import requests
# from src import config

# @pytest.fixture
# def clear_and_create_new_values():
#     # 1. Clear()
#     requests.delete(config.url + 'clear/v1')

#     # 2. Register 3 users
#     requests.post(config.url + 'auth/register/v2',
#         json = {'email': '1@em.com',
#                 'password': 'password1',
#                 'name_first': 'NF1',
#                 'name_last': 'NL1'})
    
#     requests.post(config.url + 'auth/register/v2',
#         json = {'email': '2@em.com',
#                 'password': 'password2',
#                 'name_first': 'NF2',
#                 'name_last': 'NL2'})
    
#     requests.post(config.url + 'auth/register/v2',
#         json = {'email': '3@em.com',
#                 'password': 'password3',
#                 'name_first': 'NF3',
#                 'name_last': 'NL3'})

#     # 3. Create DMs
#     requests.post(config.url + 'dm/create/v1',
#         json = {'token': 't0', 'u_ids': []})  # Need to add users into u_ids #######
    
#     # 4. Need to send some messages first ##########################################

# def test_invalid_token(clear_and_create_new_values):
#     """
#     Test whether an invalid token raises AccessErrors.
#     """

#     resp = requests.get(config.url + 'dm/messages/v1',
#         params = {'token': 't9', 'dm_id': 0, 'start': 0})

#     assert(resp.status_code == 403)  # AccessError

# def test_successful_dm_return(clear_and_create_new_values):
#     """
#     Test whether a DM is successfully returned; by comparing both the dictionary
#     values, and the status code (200).
#     """

#     resp = requests.get(config.url + 'dm/messages/v1',
#         params = {'token': 't0', 'dm_id': 0, 'start': 0})

#     assert(resp.status_code == 200)  # OK
    
#     # Another assert() for the dictionary itself
