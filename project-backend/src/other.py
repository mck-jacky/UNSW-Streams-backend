from src.data_store import data_store
from src.error import AccessError, InputError
import jwt

SUPERSECRETPASSWORD = "StampsWithAlpacas"

def notifications_get_v1(auth_user_id):
    """
    Return the user's most recent 20 notifications, ordered from most recent to least recent.
    
    Argument: auth_user_id (int) - the user id of the logged in user
    
    Exceptions:
        None
    
    Return:
    {
        'notifications': []
            this is a list of dictionaries, where each dictionary contains
            { channel_id (int), dm_id (int), notification_message (str)} and
            channel_id or dm_id = -1 if not applicable.
    } 
    """
    store = data_store.get()
    
    for user in store['users']:
        if auth_user_id == user['auth_user_id']:
            notifications = user['notifications']
    #print(data_store.get())
    return {'notifications': notifications[:20]}

def notification_send(auth_user_id, user_id, message, channel_id = -1, dm_id = -1):
    """
    A function to insert a notification into the data store. Notifications are
    stored from most recent to least recent.
    
    Arguments:
        auth_user_id (int) - the user sending/creating the notification
        user_id (int) - referrs to the user which is recieving the notification.
        message (str) - the notification message (without the user handle)
        channel_id = -1 (int) - the channel id related to the notification.
        dm_id = -1 (int) - the dm id related to the notification.
        
    """
    store = data_store.get()
    
    # Add the name handle to the message:
    for user in store['users']:
        if user['auth_user_id'] == auth_user_id:
            message = user['name_handle'] + message
    
    # Create the notification dict
    new_notification = {
        'channel_id': channel_id,
        'dm_id': dm_id,
        'notification_message': message
    }
    
    # Insert the notification into the user's data_store
    for user in store['users']:
        if user['auth_user_id'] == user_id:
            user['notifications'].insert(0, new_notification)

    # Save to data_store
    data_store.set(store)
    
    #return {}

def clear_v1():
    """
    Resets the internal data of the application to its initial state.

    The defaut blank template for this project is:
    store["users"] = []
    store["channels"] = []
    store["dms"] = []
    store["session_id"] = 0
    store["message_id"] = 0
    store["dm_id"] = 0

    Arguments:
        None

    Exceptions:
        None

    Return Value:
        Returns <empty dictionary> on <clear completion>
    """

    store = data_store.get()
    
    store["users"] = []
    store["channels"] = []
    store["dms"] = []
    store["session_id"] = 0
    store["message_id"] = 0
    store["dm_id"] = 0
    
    data_store.set(store)

    return {}

def search_v1(auth_user_id, query_str):
    """
    Given a query string, return a collection of messages in all of the 
    channels/DMs that the user has joined that contain the query.
    
    Arguments:
        <auth_user_id> (int) - the user id of the current user
        <query_str>    (str) - the string to search for in the user's messages.
    
    Exceptions:
        InputError  - Occurs when length of query_str is less than 1 or over
                      1000 characters.
    
    Return: a dictionary with one key 'messages', which is a list of dictionaries.
    i.e:
    return {
        'messages': [
            {
                'message_id', (int)
                u_id, (int)
                message, (str)
                time_created, (int)
                reacts: [
                    {
                        react_id, (int)
                        u_ids, (list of ints)
                        is_this_user_reacted (bool)
                    }
                ]
                is_pinned (bool)
            }
        ]
    }
    """
    
    # Input error:
    if len(query_str) < 1 or len(query_str) > 1000:
        raise InputError("Inputted query must be between 1 and 1000 characters")

    # Find messages:
    store = data_store.get()
    messages = []
    
    for channel in store['channels']:
        if auth_user_id in channel['all_members']:
            for message in channel['messages']:
                if query_str in message['message']:
                    # collect this message.
                    messages.append(format_message(message, auth_user_id))
    
    for dm in store['dms']:
        if auth_user_id in dm['u_ids'] or auth_user_id == dm['owner_id']:
            for message in dm['messages']:
                if query_str in message['message']:
                    # collect this message.
                    messages.append(format_message(message, auth_user_id))
    return {
        'messages': messages
    }

def format_message(message, auth_user_id):
    """
    A function to correct the formatting of dm message and channel messages.
    Inputs can be a message within a channel or dm.
    
    Return: {
                'message_id', (int)
                u_id, (int)
                message, (str)
                time_created, (int)
                reacts: [
                    {
                        react_id, (int)
                        u_ids, (list of ints)
                        is_this_user_reacted (bool)
                    }
                ]
                is_pinned (bool)
            }
    """
    formatted_msg = {
        'message_id': message['message_id'],
        'u_id': message['u_id'],
        'message': message['message'],
        'time_created': message['time_created'],
        'reacts': [],
        'is_pinned': False
    }
    
    # insert "is_this_user_reacted" key
    for react in message['reacts']:
        is_this_user_reacted = False
        if auth_user_id in react['u_ids']:
            is_this_user_reacted = True
            
        formatted_msg['reacts'].append(
            {
                'react_id': react['react_id'],
                'u_ids': react['u_ids'],
                'is_this_user_reacted': is_this_user_reacted
            }
        )
    
    # Convert is_pinned from integer to boolean.
    if message['is_pinned'] == 1: # True if = 1
        formatted_msg['is_pinned'] = True
    
    return formatted_msg

def channel_exists(channel_list, channel_id):
    """
    Arguments:
    <channel_list> (list of channel dictionaries) - <a list of channel>
    <channel_id>   (integer)                      - <id of a channel>
    ...

    Return Value:
    Returns <True> on <Channel exist>
    Returns <False> on <Channel does not exist>
    """

    for channel in channel_list:
        if channel['channel_id'] == channel_id:
            # Channel exist
            return True
    # Channel does not exist
    return False

# Check if auth_user_id is a member of the channel
def user_is_member(auth_user_id, channels, channel_id):
    for channel in channels:
        if channel['channel_id'] == channel_id:
            #print (channel['all_members'])
            if auth_user_id in channel['all_members']:
                # Already in the channel.
                #print(f"User {auth_user_id} is in channel {channel['name']}")
                return True
            else:
                #print(f"User {auth_user_id} is not in channel {channel['name']}")
                return False
    # Channel does not exist
    return False

def num_of_messages(channel_list, channel_id):
    """
    Arguments:
    <channel_list> (list of channel dictionaries)    - <a list of channel>
    <channel_id> (integer)      - <id of a channel>
    ...

    Return Value:
    Returns <the number of messages of a channel>
    """

    for channel in channel_list:
        if channel["channel_id"] == channel_id:
            return len(channel.get("messages"))

def user_exists(users, user_id):
    """
    Arguments:
    <users> (list of user dictionaries)    - <a list of users>
    <user_id> (integer)  - <id of a user>
    ...

    Return Value:
    Returns <True> on <user exist>
    Returns <False> on <user does not exist>
    """

    for user in users:
        if user['auth_user_id'] == user_id:
            return True
    return False

# Gets all details of members in a list except their password
def get_members_details(list_of_members):
    # We receive a list of user_id's eg. [1,2,3,4]
    members_details = []
    for u_id in list_of_members:
        # Find corresponding user and create a dictionary with specific details 
        for user in data_store.get()['users']:
            if  u_id == user['auth_user_id']:
                details = {}
                details['u_id'] = user['auth_user_id']
                details['email'] = user['email']
                details['name_first'] = user['name_first']
                details['name_last'] = user['name_last']
                details['handle_str'] = user['name_handle']
                members_details.append(details)
    return members_details

# Creates the dm name: an alphabetically-sorted, comma-and-space-separated list of user handles, e.g. 'ahandle1, bhandle2, chandle3'
# u_ids is a list of VALID u_ids since they are checked before this function is called in dm_create_v1
# Assumption: In our data store, the dm['u_ids'] will contain the auth_user_id
def create_dm_name(auth_user_id, u_ids):
    user_list = data_store.get()['users']
    handles_list = []

    # Make auth_user_id the first id in the list
    u_ids.insert(0, auth_user_id)
    
    # Create an unsorted list of all the users' name handles
    for u_id in u_ids:
        for user in user_list:
            if u_id == user['auth_user_id']:
                handles_list.append(user['name_handle'])

    # Sort the list name handles alphabetically 
    handles_list = sorted(handles_list)

    # Create string of name handles separated with a comma and space
    dm_name = ""
    for i in range(len(handles_list)):
        if i == len(handles_list) - 1:
            dm_name += handles_list[i]
        else:
            dm_name += handles_list[i] + ", "

    return dm_name
    
def check_if_valid_dm(dm_id):
    """
    Used for raising an InputError when dm_id does not refer to a valid DM.

    Arguments:
        dm_id (int) - Can be valid or invalid; will be checked first.

    Exceptions:
        None

    Return Value:
        Returns (bool) True if DM is valid, else returns False.
    """

    # Get and extract data from the data_store
    store = data_store.get()      # { [ { } ] }
    store_dms = store['dms']      # Is a list of dictionaries

    # Looping through individual dms (dict) in the store_dms list
    for indv_dms in store_dms:
        # If dm_id == this current dm_id, then DM exists and is valid
        if int(dm_id) == int(indv_dms['dm_id']):
            return True
    return False

def check_if_member_of_dm(auth_user_id, dm_id):
    """
    Used for raising an AccessError when dm_id is valid and the authorised user
    is not the original DM creator. Returns 0, 1 or 2 depending on the relation
    of the auth_user with the DM. To be used only on valid auth_users and DMs.

    Arguments:
        auth_user_id (int/str) - Can be valid or invalid; will be checked first.
        dm_id (int) - Can be valid or invalid; will be checked first.

    Exceptions:
        AccessError - token is invalid.
        AccessError - dm_id is valid and the authorised user is not the original
         DM creator
        InputError - dm_id does not refer to a valid DM.

    Return Value:
        Returns (int) 0, if DM is valid and auth_user is not a member of DM.
        Returns (int) 1, if DM is valid and auth_user is the owner.
        Returns (int) 2, if DM is valid and auth_user is a member.
    """

    # Get and extract data from the data_store
    store = data_store.get()      # { [ { } ] }
    store_dms = store['dms']      # Is a list of dictionaries

    # Looping through individual dms (dict) in the store_dms list
    for indv_dms in store_dms:

        # If auth_user == owner of DM and dm_id == this current dm_id
        if int(auth_user_id) == int(indv_dms['owner_id']) and \
            int(dm_id) == int(indv_dms['dm_id']):

            # Owner of DM found
            return 1
        
        # If auth_user is in the DM's member's list (can include the owner)
        elif int(auth_user_id) in indv_dms['u_ids'] and \
            int(dm_id) == int(indv_dms['dm_id']):

            # Member or owner of DM found
            return 2
    
    # auth_user not part of given DM
    return 0

def decrypt_token(token):
    """
    Try to decrypt token, and returns a dictionary with auth_user_id and
    session_id, if valid. Valid if token is a valid format (A.B.C), valid
    encryption password and valid auth_user_id with corresponding valid
    session_id.

    Return info (dict) with auth_user_id and session_id key-value (int) pairs.
    """
    try:
        info = jwt.decode(token, SUPERSECRETPASSWORD, algorithms=["HS256"])
    except (jwt.InvalidSignatureError, jwt.DecodeError) as e:
        # InvalidSignatureError is when the encrypt password is wrong
        # DecodeError is when the token is not a valid format. E.g. "InvalidToken"
        raise AccessError("Invalid token") from e 
        # this "as e" and "from e" is for pylint

    info['auth_user_id'] = int(info['auth_user_id'])
    info['session_id'] = int(info['session_id'])

    if is_valid_token(info) == False:
        raise AccessError("Token is not valid.") 

    return info
    
def is_valid_token(authid_seshid):
    user_id = int(authid_seshid['auth_user_id'])
    sesh_id = int(authid_seshid['session_id'])

    store = data_store.get()
    users = store['users']
    
    for user in users:
        if user['auth_user_id'] == user_id:
            if sesh_id in user['session_ids']:
                # User exists and session is valid.
                return True
            else:
                # Session id is invalid.
                return False
    # If we get to this point, user doesn't exist.
    return False

def is_global_owner(auth_user_id):
    """
    Used to check the the owner is the global owner of the stream.

    Arguments:
    auth_user_id (integer)  - <id of a user>
    ...

    Return Value:
    Returns <True> on <user is a global owner>
    Returns <False> on <user is not a global owner>
    """

    store = data_store.get()
    user_list = store["users"]
    GLOBAL_OWNER = 1

    for user in user_list:
        if user["auth_user_id"] == auth_user_id:
            if user["permission_id"] == GLOBAL_OWNER:
                return True
    
    return False
