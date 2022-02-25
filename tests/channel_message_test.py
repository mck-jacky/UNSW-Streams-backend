# import pytest

# from src.channel import channel_messages_v1
# from src.error import AccessError, InputError
# from src.other import clear_v1
# from src.auth import auth_register_v1
# from src.channels import channels_create_v1
# from src.data_store import data_store

# """
# InputError when any of:
      
#     channel_id does not refer to a valid channel
#     start is greater than the total number of messages in the channel
      
# AccessError when:
      
#     the authorised user is not a member of the channel
# """

# @pytest.fixture
# def initialize():
#     clear_v1()
#     auth_user_id_1 = auth_register_v1("email1@gmail.com", "password", "name_first1", "name_last1")["auth_user_id"]
#     auth_user_id_2 = auth_register_v1("email2@gmail.com", "password", "name_first2", "name_last2")["auth_user_id"]
#     auth_user_id_3 = auth_register_v1("email3@gmail.com", "password", "name_first3", "name_last3")["auth_user_id"]
#     channel_id_1 = 1
#     channel_id_2 = 2
#     channel_id_3 = 3

#     store = data_store.get()
#     channel_list = store["channels"]

#     new_channel = {
#             'channel_id': channel_id_1,
#             'name': "channel_1",
#             'is_public': True,
#             'owner_members': [auth_user_id_1],
#             'all_members': [auth_user_id_1],
#             'messages': [
#                 {
#                 "message_id": 0, 
#                 "u_id": 0, 
#                 "message": "hello world", 
#                 "time_created": 1349
#                 }
#             ]
#     }
#     channel_list.append(new_channel)

#     new_channel = {
#             'channel_id': channel_id_2,
#             'name': "channel_1",
#             'is_public': True,
#             'owner_members': [auth_user_id_2],
#             'all_members': [auth_user_id_2],
#             'messages': [
#                 {
#                 "message_id": 3, 
#                 "u_id": 0, 
#                 "message": "hello world", 
#                 "time_created": 1351
#                 },
#                 {
#                 "message_id": 2, 
#                 "u_id": 0, 
#                 "message": "hello world world", 
#                 "time_created": 1350
#                 },
#                 {
#                 "message_id": 1, 
#                 "u_id": 0, 
#                 "message": "hello world world world", 
#                 "time_created": 1349
#                 },
#             ]
#     }
#     channel_list.append(new_channel)

#     new_channel = {
#             'channel_id': channel_id_3,
#             'name': "channel_1",
#             'is_public': True,
#             'owner_members': [auth_user_id_3],
#             'all_members': [auth_user_id_1, auth_user_id_2, auth_user_id_3],
#             'messages': [
#             ]
#     }
#     channel_list.append(new_channel)

# # Give InputError when channel_id does not refer to a valid channel
# def test_channel_id_invalid(initialize):
#     with pytest.raises(InputError):
#         channel_messages_v1(1, 0, 1)
#     with pytest.raises(InputError):
#         channel_messages_v1(1, 4, 1)
#     with pytest.raises(InputError):
#         channel_messages_v1(1, 5, 1)

# # Give InputError when start is greater or equal to the total number of messages in the channel
# def test_channel_start_excess(initialize):
#     with pytest.raises(InputError):
#         channel_messages_v1(1, 1, 2)
#     with pytest.raises(InputError):
#         channel_messages_v1(1, 1, 1)
#     with pytest.raises(InputError):
#         channel_messages_v1(2, 2, 4)
#     with pytest.raises(InputError):
#         channel_messages_v1(2, 2, 3)   
#     with pytest.raises(InputError):
#         channel_messages_v1(3, 3, 1)

# # Give AccessError when the authorised user is not a member of the channel
# def test_channel_access_error(initialize):
#     with pytest.raises(AccessError):
#         channel_messages_v1(1, 2, 1)
#     with pytest.raises(AccessError):
#         channel_messages_v1(2, 1, 1)
#     with pytest.raises(AccessError):
#         channel_messages_v1(3, 1, 1)
#     with pytest.raises(AccessError):
#         channel_messages_v1(3, 2, 1)

# # If input implies that both errors should be thrown, throw an AccessError
# def test_both_error(initialize):
#     with pytest.raises(AccessError):
#         channel_messages_v1(1, 2, 4)
#     with pytest.raises(AccessError):
#         channel_messages_v1(3, 2, 6)

# # Test when the authorised user is a member of the channel,
# # the channel_id is refer to a valid channel,
# # the start index is less than or equal to the total number of messages in the chat.
# def test_channel_id_access_valid():
#     assert channel_messages_v1(2, 2, 0) == {'messages': [{"message_id": 3, 
#                                                           "u_id": 0, 
#                                                           "message": "hello world", 
#                                                           "time_created": 1351},
#                                                          {"message_id": 2, 
#                                                           "u_id": 0, 
#                                                           "message": "hello world world", 
#                                                           "time_created": 1350},
#                                                          {"message_id": 1, 
#                                                           "u_id": 0, 
#                                                           "message": "hello world world world", 
#                                                           "time_created": 1349}],
#                                             'start': 0,
#                                             'end': -1
#                                             }

#     assert channel_messages_v1(1, 1, 0) == {'messages': [{"message_id": 0, 
#                                                           "u_id": 0, 
#                                                           "message": "hello world", 
#                                                           "time_created": 1349}],
#                                             'start': 0,
#                                             'end': -1
#                                             }

#     assert channel_messages_v1(2, 2, 1) == {'messages': [{"message_id": 2, 
#                                                           "u_id": 0, 
#                                                           "message": "hello world world", 
#                                                           "time_created": 1350},
#                                                          {"message_id": 1, 
#                                                           "u_id": 0, 
#                                                           "message": "hello world world world", 
#                                                           "time_created": 1349}],
#                                             'start': 1,
#                                             'end': -1
#                                             }

#     assert channel_messages_v1(2, 2, 2) == {'messages': [{"message_id": 1, 
#                                                           "u_id": 0, 
#                                                           "message": "hello world world world", 
#                                                           "time_created": 1349}],
#                                             'start': 2,
#                                             'end': -1
#                                             }
    
# ### Alex's Tests: ###

# """
# Given a channel with ID channel_id that the authorised user is a member of,
# return up to 50 messages between index "start" and "start + 50". 
# Message with index 0 is the most recent message in the channel. 
# """



# @pytest.fixture
# def initialise_empty():
#     clear_v1()
#     global auth_user_id_1
#     global auth_user_id_2
#     global auth_user_id_3
#     auth_user_id_1 = auth_register_v1("email1@gmail.com", "password", "name_first1", "name_last1")["auth_user_id"]
#     auth_user_id_2 = auth_register_v1("email2@gmail.com", "password", "name_first2", "name_last2")["auth_user_id"]
#     auth_user_id_3 = auth_register_v1("email3@gmail.com", "password", "name_first3", "name_last3")["auth_user_id"]
#     global channel_id_1
#     global channel_id_2
#     global channel_id_3
#     channel_id_1 = channels_create_v1(auth_user_id_1, "channel1", True)['channel_id']
#     channel_id_2 = channels_create_v1(auth_user_id_1, "channel2", True)['channel_id']
#     channel_id_3 = channels_create_v1(auth_user_id_1, "channel3", True)['channel_id']
#     # User 1 in a owner member of channels 1,2 and 3. 
#     # User 1 is a global owner.
    
# def new_message(i):
#     new_mess = {
#         'message_id': i, 
#         'u_id': 1, 
#         'message': "Hello" + str(i), 
#         'time_created': i**i
#     }
#     return new_mess

# def create_messages(num_of_messages, channel_id):
#     """ Creates a number of messages in the channel corresponding to channel_id """
#     store = data_store.get()
#     channels = store['channels']
    
#     list_of_messages = []
    
#     for channel in channels:
#         if channel['channel_id'] == channel_id:
#             for i in range(num_of_messages):
#                 new_mess = new_message(i)
#                 channel['messages'].append(new_mess)
#                 list_of_messages.append(new_mess)
#     return list_of_messages
    
# def test_1_messages(initialise_empty):
#     num_messages = 1
    
#     list_of_messages = create_messages(num_messages, channel_id_2)
    
#     return_value = channel_messages_v1( auth_user_id_1, channel_id_2, 0)
    
#     assert return_value['start'] == 0
#     assert return_value['end'] == -1
#     assert len(return_value['messages']) == 1
#     assert return_value['messages'] == list_of_messages
#     check_return_value_types(return_value)
    
# def test_25_messages(initialise_empty):
    
#     list_of_messages = create_messages(25, channel_id_2)
    
#     return_value = channel_messages_v1( auth_user_id_1, channel_id_2, 0)
    
#     assert return_value['start'] == 0
#     assert return_value['end'] == -1
#     assert len(return_value['messages']) == 25
#     assert return_value['messages'] == list_of_messages[0:50]
#     check_return_value_types(return_value)
    
# def test_50_messages(initialise_empty):
    
#     list_of_messages = create_messages(50, channel_id_2)
    
#     return_value = channel_messages_v1( auth_user_id_1, channel_id_2, 0)
    
#     assert return_value['start'] == 0
#     assert return_value['end'] == -1
#     assert len(return_value['messages']) == 50
#     assert return_value['messages'] == list_of_messages[0:50]
#     check_return_value_types(return_value)
    
# def test_51_messages(initialise_empty):
    
#     list_of_messages = create_messages(51, channel_id_2)
    
#     return_value = channel_messages_v1( auth_user_id_1, channel_id_2, 0)
#     assert return_value['start'] == 0
#     assert return_value['end'] == 50
#     assert len(return_value['messages']) == 50
#     assert return_value['messages'] == list_of_messages[0:50]
#     check_return_value_types(return_value)

#     return_value = channel_messages_v1( auth_user_id_1, channel_id_2, return_value['end'])
#     assert return_value['start'] == 50
#     assert return_value['end'] == -1
#     assert len(return_value['messages']) == 1
#     assert return_value['messages'] == [list_of_messages[50]]
#     check_return_value_types(return_value)
    
# def test_52_messages(initialise_empty):
#     num_messages = 52
    
#     list_of_messages = create_messages(num_messages, channel_id_2)
    
#     return_value = channel_messages_v1( auth_user_id_1, channel_id_2, 0)
#     assert return_value['start'] == 0
#     assert return_value['end'] == 50
#     assert len(return_value['messages']) == 50
#     assert return_value['messages'] == list_of_messages[0:50]
#     check_return_value_types(return_value)

#     return_value = channel_messages_v1( auth_user_id_1, channel_id_2, return_value['end'])
#     assert return_value['start'] == 50
#     assert return_value['end'] == -1
#     assert len(return_value['messages']) == 2
#     assert return_value['messages'] == list_of_messages[50::]
#     check_return_value_types(return_value)

# def test_100_messages(initialise_empty):
#     num_messages = 100
    
#     list_of_messages = create_messages(num_messages, channel_id_2)
    
#     return_value = channel_messages_v1( auth_user_id_1, channel_id_2, 0)
#     assert return_value['start'] == 0
#     assert return_value['end'] == 50
#     assert len(return_value['messages']) == 50
#     assert return_value['messages'] == list_of_messages[0:50]

#     return_value = channel_messages_v1( auth_user_id_1, channel_id_2, return_value['end'])
#     assert return_value['start'] == 50
#     assert return_value['end'] == -1
#     assert len(return_value['messages']) == 50
#     assert return_value['messages'] == list_of_messages[50::]
    
# def test_101_messages(initialise_empty):
#     num_messages = 101
    
#     list_of_messages = create_messages(num_messages, channel_id_2)
    
#     return_value = channel_messages_v1( auth_user_id_1, channel_id_2, 0)
#     assert return_value['start'] == 0
#     assert return_value['end'] == 50
#     assert len(return_value['messages']) == 50
#     assert return_value['messages'] == list_of_messages[0:50]
#     check_return_value_types(return_value)

#     return_value = channel_messages_v1( auth_user_id_1, channel_id_2, return_value['end'])
#     assert return_value['start'] == 50
#     assert return_value['end'] == 100
#     assert len(return_value['messages']) == 50
#     assert return_value['messages'] == list_of_messages[50:100]   
#     check_return_value_types(return_value)
    
#     return_value = channel_messages_v1( auth_user_id_1, channel_id_2, return_value['end'])
#     assert return_value['start'] == 100
#     assert return_value['end'] == -1
#     assert len(return_value['messages']) == 1
#     assert return_value['messages'] == [list_of_messages[100]]   
#     check_return_value_types(return_value)

# """
# Testing return values:
# the channel_messages function returns a new index "end" which is the value of "start + 50", or,
# if this function has returned the least recent messages in the channel,
# returns -1 in "end" to indicate there are no more messages to load after this return.
# """
# def check_return_value_types(return_value):
#     assert type(return_value) == type({})
#     assert type(return_value['messages']) == type([])
#     assert type(return_value['start']) == type(1)
#     assert type(return_value['end']) == type(1)
    
#     for message in return_value['messages']:
#         assert type(message) == type({})
#         assert type(message['message_id']) == type(1)
#         assert type(message['u_id']) == type(1)
#         assert type(message['message']) == type("Hello")
#         assert type(message['time_created']) == type(1)

# def test_return_value_types(initialize):
#     auth_user_id = 1
#     channel_id = 1
#     start = 0

#     return_value = channel_messages_v1( auth_user_id, channel_id, start)
    
#     check_return_value_types(return_value)

    

# def test_start_value(initialize):
#     auth_user_id = 2
#     channel_id = 2
    
#     # start at the beginning
#     start = 0

#     return_value = channel_messages_v1( auth_user_id, channel_id, start)
    
#     assert return_value['start'] == start
#     assert (return_value['end'] == -1)

#     # start at end
#     start = 2

#     return_value = channel_messages_v1( auth_user_id, channel_id, start)
    
#     assert return_value['start'] == start
#     assert (return_value['end'] == -1)
    
#     # start past the end
#     start = 3
#     with pytest.raises(InputError):
#         return_value = channel_messages_v1( auth_user_id, channel_id, start)
        
#     # negative start value
#     start = -1
#     return_value = channel_messages_v1( auth_user_id, channel_id, start)
    

# def test_empty_messages(initialise_empty):
#     auth_user_id = 1
#     channel_id = 1
    
#     start = 0
    
#     return_value = channel_messages_v1( auth_user_id, channel_id, start)
#     assert return_value['start'] == start
#     assert (return_value['end'] == -1)
#     assert return_value['messages'] == []
