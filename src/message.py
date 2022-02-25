from pickle import FALSE, TRUE
from src.error import AccessError, InputError
from src.other import channel_exists, user_exists, user_is_member, check_if_valid_dm, check_if_member_of_dm, is_global_owner, notification_send
from src.data_store import data_store
from datetime import timezone
import datetime

def message_send_v1(auth_user_id, channel_id, message):
    """
    Send a message from the authorised user to the channel specified by channel_id.
    
    Arguments:
    <auth_user_id> (int)    - the user id
    <channel_id>   (int)    - The id of the specified channel the user wants to get details from
    <message>      (string) - message to send

    Exceptions:
    InputError  - Occurs when channel_id does not refer to a valid channel
                - Occurs when length of message is less than 1 or over 1000 characters
    AccessError - Occurs when channel_id is valid and the authorised user is not a member of the channel

    Return Value:
    Returns {message_id}
    """
    store = data_store.get()
    channel_list = store["channels"]

    # check whether the channel id is exist or not
    if not channel_exists(channel_list, channel_id):
        raise InputError("Invalid Channel id")

    # check whether the user is a memeber of this channel or not
    if not user_is_member(auth_user_id, channel_list, channel_id):
        raise AccessError("Inputted user is not a memeber of this channel")

    # check whether the length of message is too short or too long
    if len(message) < 1 or len(message) > 1000:
        raise InputError("the message is too short or too long")

    store["message_id"] += 1
    message_id = store["message_id"]
    
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()

    new_message = {
        "message_id": message_id,
        "u_id": auth_user_id,
        "message": message,
        "time_created": utc_timestamp,
        "reacts": [
            {
            "react_id": 1,
            "u_ids": [],
            }
        ],
        "is_pinned": 0
    }

    for channel in channel_list:
        if channel["channel_id"] == channel_id:
            channel["messages"].insert(0, new_message)
            channel_name = channel['name']
    
    # Send notification to a tagged user:
    for user in store['users']:
        if "@" + user['name_handle'] in message:
            notification_send(auth_user_id, user['auth_user_id'],
                              f" tagged you in {channel_name}: {message[:20]}",
                              channel_id = channel_id)

    data_store.set(store)

    return {"message_id": int(message_id)}

def valid_msg_id_of_user(auth_user_id, message_id):
    store = data_store.get()
    channel_list = store["channels"]
    dm_list = store["dms"]

    for channel in channel_list:
        if user_is_member(auth_user_id, channel_list, channel["channel_id"]):
            for msg in channel["messages"]:
                if (msg["message_id"] == message_id):
                    return True

    for dm in dm_list:
        if check_if_member_of_dm(auth_user_id, dm["dm_id"]) == 1 or check_if_member_of_dm(auth_user_id, dm["dm_id"]) == 2:
            for msg in dm["messages"]:
                if (msg["message_id"] == message_id):
                    return True

    return False

def message_access_permission(auth_user_id, message_id):
    store = data_store.get()
    channel_list = store["channels"]
    dm_list = store["dms"]

    for channel in channel_list:
        if user_is_member(auth_user_id, channel_list, channel["channel_id"]):
            for msg in channel["messages"]:
                if (msg["message_id"] == message_id):
                    if (msg["u_id"] == auth_user_id) or (auth_user_id in channel["owner_members"]) or (is_global_owner(auth_user_id)):
                        return True

    for dm in dm_list:
        for msg in dm["messages"]:
            if (msg["message_id"] == message_id):
                if (msg["u_id"] == auth_user_id ) or (auth_user_id == dm["owner_id"]):
                    return True

    return False

def message_edit_v1(auth_user_id, message_id, message):
    """
    Given a message, update its text with new text. If the new message is an empty string, the message is deleted.
    
    Arguments:
    <auth_user_id> (int)    - the user id
    <message_id>   (int)    - The id of a specified message
    <message>      (string) - message to update

    Exceptions:
    InputError  - Occurs when length of message is over 1000 characters
                - Occurs when message_id does not refer to a valid message within a channel/DM that the authorised user has joined
    AccessError - Occurs when message_id refers to a valid message in a joined channel/DM and none of the following are true:
                  * the message was sent by the authorised user making this request
                  * the authorised user has owner permissions in the channel/DM

    Return Value:
    Returns {}
    """

    # check whether the length of message is too long or not
    if len(message) > 1000:
        raise InputError("length of message is over 1000 characters")
    
    # message_id does not refer to a valid message within a channel/DM that the authorised user has joined
    if not valid_msg_id_of_user(auth_user_id, message_id):
        raise InputError("Invalid message id")

    # check whether user can access this message or not
    if not message_access_permission(auth_user_id, message_id):
        raise AccessError("You don't have permission to access this message")

    store = data_store.get()
    channel_list = store["channels"]
    dm_list = store["dms"]

    for channel in channel_list:
        for msg in channel["messages"]:
            if (msg["message_id"] == message_id):
                if len(message) == 0:
                    channel["messages"].remove(msg)
                    break
                msg["message"] = message
                break
    
    for dm in dm_list:
        for msg in dm["messages"]:
            if (msg["message_id"] == message_id):
                if len(message) == 0:
                    dm["messages"].remove(msg)
                    break
                msg["message"] = message
                break

    data_store.set(store)

    return {}

def message_remove_v1(auth_user_id, message_id):
    """
    Given a message_id for a message, this message is removed from the channel/DM.
    
    Arguments:
    <auth_user_id> (int)    - the user id
    <message_id>   (int)    - The id of a specified message

    Exceptions:
    InputError  - Occurs when message_id does not refer to a valid message within a channel/DM that the authorised user has joined
    AccessError - Occurs when message_id refers to a valid message in a joined channel/DM and none of the following are true:
                  * the message was sent by the authorised user making this request
                  * the authorised user has owner permissions in the channel/DM

    Return Value:
    Returns {}
    """

    # message_id does not refer to a valid message within a channel/DM that the authorised user has joined
    if not valid_msg_id_of_user(auth_user_id, message_id):
        raise InputError("Invalid message id")

    # check whether user can access this message or not
    if not message_access_permission(auth_user_id, message_id):
        raise AccessError("You don't have permission to access this message")

    store = data_store.get()
    channel_list = store["channels"]
    dm_list = store["dms"]

    for channel in channel_list:
        for msg in channel["messages"]:
            if (msg["message_id"] == message_id):
                channel["messages"].remove(msg)
                break

    for dm in dm_list:
        for msg in dm["messages"]:
            if (msg["message_id"] == message_id):
                dm["messages"].remove(msg)

    data_store.set(store)

    return {}

def message_senddm_v1(auth_user_id, dm_id, message):
    """
    Send a message from authorised_user to the DM specified by dm_id. Note: Each message should have it's own unique ID, 
    i.e. no messages should share an ID with another message, even if that other message is in a different channel or DM.
    
    Arguments:
    <auth_user_id> (int)    - the user id
    <dm_id>        (int)    - The id of a dm chat
    <message_id>   (int)    - The id of a specified message

    Exceptions:
    InputError  - Occurs when dm_id does not refer to a valid DM
                - Occurs when length of message is less than 1 or over 1000 characters
    AccessError - Occurs when dm_id is valid and the authorised user is not a member of the DM

    Return Value:
    Returns {message_id}
    """
    store = data_store.get()
    dm_list = store["dms"]

    # check whether dm_id is valid or not 
    if not check_if_valid_dm(dm_id):
        raise InputError("Invalid dm id")

    # check whether user is a member of dm or not
    if check_if_member_of_dm(auth_user_id, dm_id) == 0:
        raise AccessError("Inputted user is not a memeber of this dm")

    # check whether the length of message is too short or too long
    if len(message) < 1 or len(message) > 1000:
        raise InputError("the message is too short or too long")

    store["message_id"] += 1
    message_id = store["message_id"]

    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()

    new_message = {
        "message_id": message_id,
        "u_id": auth_user_id,
        "message": message,
        "time_created": utc_timestamp,
        "reacts": [
            {
            "react_id": 1,
            "u_ids": [],
            }
        ],
        "is_pinned": 0
    }

    for dm in dm_list:
        if dm["dm_id"] == dm_id:
            dm["messages"].insert(0, new_message)
            dm_name = dm['name']

    # Send notification to a tagged user:
    for user in store['users']:
        if "@" + user['name_handle'] in message:
            notification_send(auth_user_id, user['auth_user_id'],
                              f" tagged you in {dm_name}: {message[:20]}",
                              dm_id = dm_id)

    data_store.set(store)

    return {"message_id": message_id}
    
def is_valid_react_id(message_id, react_id):
    store = data_store.get()
    channel_list = store["channels"]
    dm_list = store["dms"]

    for channel in channel_list:
        for msg in channel["messages"]:
            if msg["message_id"] == message_id:
                for react in msg["reacts"]:
                    if react["react_id"] == react_id:
                        return True

    for dm in dm_list:
        for msg in dm["messages"]:
            if msg["message_id"] == message_id:
                for react in msg["reacts"]:
                    if react["react_id"] == react_id:
                        return True
    
    return False

def already_contain_react(auth_user_id, message_id, react_id):
    store = data_store.get()
    channel_list = store["channels"]
    dm_list = store["dms"]

    for channel in channel_list:
        for msg in channel["messages"]:
            if msg["message_id"] == message_id:
                for react in msg["reacts"]:
                    if react["react_id"] == react_id and auth_user_id in react["u_ids"]:
                        return True

    for dm in dm_list:
        for msg in dm["messages"]:
            if msg["message_id"] == message_id:
                for react in msg["reacts"]:
                    if react["react_id"] == react_id and auth_user_id in react["u_ids"]:
                        return True

    return False

def message_react_v1(auth_user_id, message_id, react_id):
    """
    Given a message within a channel or DM the authorised user is part of, add a "react" to that particular message.
    
    Arguments:
    <auth_user_id> (int)    - the user id
    <message_id>   (int)    - The id of a message
    <react_id>     (int)    - The id of a react

    Exceptions:
    InputError  - Occurs when message_id is not a valid message within a channel or DM that the authorised user has joined
                - Occurs when react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1
                - Occurs when the message already contains a react with ID react_id from the authorised user
    Return Value:
    Returns {}
    """
    store = data_store.get()
    channel_list = store["channels"]
    dm_list = store["dms"]

    # message_id does not refer to a valid message within a channel/DM that the authorised user has joined.
    if not valid_msg_id_of_user(auth_user_id, message_id):
        raise InputError("Invalid message id")

    # check whether react_id is a valid react ID or not. 
    if not is_valid_react_id(message_id, react_id):
        raise InputError("Invalid react id")
    
    # check whether the message already contains a react with ID react_id from the authorised user or not.
    if already_contain_react(auth_user_id, message_id, react_id):
        raise InputError("This message already contain same react id from the same user")

    for channel in channel_list:
        for msg in channel["messages"]:
            if msg["message_id"] == message_id:
                for react in msg["reacts"]:
                    if react["react_id"] == react_id:
                        react["u_ids"].append(auth_user_id)
                # Send notification to the owner of the message:
                notification_send(
                    auth_user_id, msg['u_id'],
                    f" reacted to your message in {channel['name']}", channel_id = channel['channel_id']
                )
    
    
    for dm in dm_list:
        for msg in dm["messages"]:
            if msg["message_id"] == message_id:
                for react in msg["reacts"]:
                    if react["react_id"] == react_id:
                        react["u_ids"].append(auth_user_id)
                # Send notification to the owner of the message:
                notification_send(
                    auth_user_id, msg['u_id'],
                    f" reacted to your message in {dm['name']}", dm_id = dm['dm_id']
                )

    

    data_store.set(store)
    return {}

def message_unreact_v1(auth_user_id, message_id, react_id):
    """
    Given a message within a channel or DM the authorised user is part of, add a "react" to that particular message.
    
    Arguments:
    <auth_user_id> (int)    - The user id
    <message_id>   (int)    - The id of a message
    <react_id>     (int)    - The id of a react

    Exceptions:
    InputError  - Occurs when message_id is not a valid message within a channel or DM that the authorised user has joined
                - Occurs when react_id is not a valid react ID
                - Occurs when the message does not contain a react with ID react_id from the authorised user
    Return Value:
    Returns {}
    """
    store = data_store.get()
    channel_list = store["channels"]
    dm_list = store["dms"]

    # message_id does not refer to a valid message within a channel/DM that the authorised user has joined.
    if not valid_msg_id_of_user(auth_user_id, message_id):
        raise InputError("Invalid message id")

    # check whether react_id is a valid react ID or not. 
    if not is_valid_react_id(message_id, react_id):
        raise InputError("Invalid react id")

    if not already_contain_react(auth_user_id, message_id, react_id):
        raise InputError("The message does not contain this react")

    for channel in channel_list:
        for msg in channel["messages"]:
            if msg["message_id"] == message_id:
                for react in msg["reacts"]:
                    if react["react_id"] == react_id:
                        react["u_ids"].remove(auth_user_id)

    for dm in dm_list:
        for msg in dm["messages"]:
            if msg["message_id"] == message_id:
                for react in msg["reacts"]:
                    if react["react_id"] == react_id:
                        react["u_ids"].remove(auth_user_id)

    data_store.set(store)
    return {}

def message_already_pinned(message_id):
    store = data_store.get()
    channel_list = store["channels"]
    dm_list = store["dms"]
    PINNED = 1

    for channel in channel_list:
        for msg in channel["messages"]:
            if msg["message_id"] == message_id:
                if msg["is_pinned"] == PINNED:
                    return True

    for dm in dm_list:
        for msg in dm["messages"]:
            if msg["message_id"] == message_id:
                if msg["is_pinned"] == PINNED:
                    return TRUE

    return False

def user_has_owner_permission_to_this_msg(auth_user_id, message_id):
    store = data_store.get()
    channel_list = store["channels"]
    dm_list = store["dms"]

    for channel in channel_list:
        for msg in channel["messages"]:
            if (msg["message_id"] == message_id):
                if (auth_user_id in channel["owner_members"]) or (is_global_owner(auth_user_id)):
                    return True

    for dm in dm_list:
        for msg in dm["messages"]:
            if (msg["message_id"] == message_id):
                if auth_user_id == dm["owner_id"]:
                    return True

    return False

def message_pin_v1(auth_user_id, message_id):
    """
    Given a message within a channel or DM, mark it as "pinned".
    
    Arguments:
    <auth_user_id> (int)    - The user id
    <message_id>   (int)    - The id of a message

    Exceptions:
    InputError  - Occurs when message_id is not a valid message within a channel or DM that the authorised user has joined
                - Occurs when the message is already pinned
                - Occurs when message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM
    Return Value:
    Returns {}
    """
    store = data_store.get()
    channel_list = store["channels"]
    dm_list = store["dms"]
    PINNED = 1

    # check whether user can access this message or not
    if not user_has_owner_permission_to_this_msg(auth_user_id, message_id) and valid_msg_id_of_user(auth_user_id, message_id):
        raise AccessError("User don't have permission to pin this message")

    # message_id does not refer to a valid message within a channel/DM that the authorised user has joined.
    if not valid_msg_id_of_user(auth_user_id, message_id):
        raise InputError("Invalid message id")

    # check whether the message is already pinned or not.
    if message_already_pinned(message_id):
        raise InputError("Message is already pinned")

    for channel in channel_list:
        for msg in channel["messages"]:
            if msg["message_id"] == message_id:
                msg["is_pinned"] = PINNED

    for dm in dm_list:
        for msg in dm["messages"]:
            if msg["message_id"] == message_id:
                msg["is_pinned"] = PINNED

    data_store.set(store)
    return {}

def message_unpin_v1(auth_user_id, message_id):
    """
    Given a message within a channel or DM, mark it as "pinned".
    
    Arguments:
    <auth_user_id> (int)    - the user id
    <message_id>   (int)    - the id of a message

    Exceptions:
    InputError  - Occurs when message_id is not a valid message within a channel or DM that the authorised user has joined
                - Occurs when the message is not already pinned
                - Occurs when message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM
    Return Value:
    Returns {}
    """
    store = data_store.get()
    channel_list = store["channels"]
    dm_list = store["dms"]
    UNPINNED = 0

    # check whether user can access this message or not
    if not user_has_owner_permission_to_this_msg(auth_user_id, message_id) and valid_msg_id_of_user(auth_user_id, message_id):
        raise AccessError("User don't have permission to pin this message")

    # message_id does not refer to a valid message within a channel/DM that the authorised user has joined.
    if not valid_msg_id_of_user(auth_user_id, message_id):
        raise InputError("Invalid message id")

    # check whether the message is already pinned or not.
    if not message_already_pinned(message_id):
        raise InputError("Message is not already pinned")

    for channel in channel_list:
        for msg in channel["messages"]:
            if msg["message_id"] == message_id:
                msg["is_pinned"] = UNPINNED

    for dm in dm_list:
        for msg in dm["messages"]:
            if msg["message_id"] == message_id:
                msg["is_pinned"] = UNPINNED

    data_store.set(store)
    return {}

def message_share_v1(auth_user_id, og_message_id, message, channel_id, dm_id):
    """
    og_message_id is the ID of the original message. channel_id is the channel that the message is being shared to, 
    and is -1 if it is being sent to a DM. dm_id is the DM that the message is being shared to, and is -1 if it is being sent to a channel. 
    message is the optional message in addition to the shared message, and will be an empty string '' if no message is given.
    
    Arguments:
    <auth_user_id> (int)    - The user id
    <og_message_id>(int)    - The id of the original message
    <message>      (string) - The optional message in addition to the shared message
    <channel_id>   (int)    - The id of a channel
    <dm_id>        (int)    - The id of a dm

    Exceptions:
    InputError  - Occurs when both channel_id and dm_id are invalid
                - Occurs when neither channel_id nor dm_id are -1
                - Occurs when og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
                - Occurs when length of message is more than 1000 characters

    AccessError - Occurs the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and 
                  the authorised user has not joined the channel or DM they are trying to share the message to
    
    Return Value:
    Returns {shared_message_id}
    """
    store = data_store.get()
    channel_list = store["channels"]
    dm_list = store["dms"]

    # neither channel_id nor dm_id are -1
    if channel_id != -1 and dm_id != -1:
        raise InputError("neither channel_id nor dm_id are -1")

    # both channel_id and dm_id are invalid
    if not ((channel_id == -1 and check_if_valid_dm(dm_id)) or (channel_exists(channel_list, channel_id) and dm_id == -1)):
        raise InputError("invalid channel_id or dm_id")
    
    # the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and the authorised user has not joined the channel or 
    # DM they are trying to share the message to
    if (not user_is_member(auth_user_id, channel_list, channel_id) and dm_id == -1) or (channel_id == -1 and check_if_member_of_dm(auth_user_id, dm_id) == 0):
        raise AccessError("user don't have permission to forward messages to this channel")

    # og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
    if not valid_msg_id_of_user(auth_user_id, og_message_id):
        raise InputError("invalid og_message_id")

    # length of message is more than 1000 characters
    if len(message) > 1000:
        raise InputError("length of message is more than 1000 characters")

    for channel in channel_list:
        for msg in channel["messages"]:
            if msg["message_id"] == og_message_id:
                new_message_content = msg["message"]

    for dm in dm_list:
        for msg in dm["messages"]:
            if msg["message_id"] == og_message_id:
                new_message_content = msg["message"]


    # Appending the additional message to the end of original shared message
    if len(message) > 0:
        new_message_content = new_message_content + message

    if dm_id == -1:
        shared_message_id = message_send_v1(auth_user_id, channel_id, new_message_content)["message_id"]
    
    if channel_id == -1:
        shared_message_id = message_senddm_v1(auth_user_id, dm_id, new_message_content)["message_id"]
    
    return {"shared_message_id": shared_message_id}