from src.data_store import data_store
from src.error import AccessError, InputError
from src.other import user_exists

def channels_list_v1(auth_user_id):
    """
    Provide a list of all channels (and their associated details) that the
    authorised user is part of.

    Arguments:
        <auth_user_id> (str/int) - Input argument can be a <str> or <int>. Will
         be converted appropriately within the function. <auth_user_id> can also
         be valid or invalid, as it will be checked within the function.

    Exceptions:
        AccessError - Occurs when auth_user_id is invalid.

    Return Value:
        Returns populated <auth_user_part_of> if user is valid, that the user is
         part of, and data_store['channels'] contains non-empty channels data.
        Returns empty <auth_user_part_of> if user is valid and
         data_store['channels'] is empty.
        Raises AccessError exception if user is not valid.
    """
    
    # Get and extract data from the data_store
    store = data_store.get()            # { [ { } ] }
    # store_user = store['users']         # Is a list
    store_channels = store['channels']  # Is a list of dictionaries

    # Raise AccessError if invalid auth_user_id
    # if not user_exists(store_user, auth_user_id):
    #     raise AccessError('Invalid user id')
    
    # Initialise return value
    auth_user_part_of = {'channels': []}

    # Looping through individual channels (dict) in the store_channels list
    for indv_channel in store_channels:
        # Owner of channel also in all_members
        for member in indv_channel['all_members']:
            if int(member) == int(auth_user_id):
                # A temp new dictionary, with only channel_id & name key fields
                filtered_channel = {}
                filtered_channel['channel_id'] = indv_channel['channel_id']
                filtered_channel['name'] = indv_channel['name']

                # Take the valid channel (dict) and append to return value
                auth_user_part_of['channels'].append(filtered_channel)

    return auth_user_part_of

def channels_listall_v1(auth_user_id):
    """
    Provide a list of all channels, including private channels,
    (and their associated details).

    Arguments:
        <auth_user_id> (str/int) - Input argument can be a <str> or <int>. Will
         be converted appropriately within the function. <auth_user_id> can also
         be valid or invalid, as it will be checked within the function.

    Exceptions:
        AccessError - Occurs when auth_user_id is invalid.

    Return Value:
        Returns populated <auth_user_part_of> if user is valid and
         data_store['channels'] contains non-empty channels data.
        Returns empty <auth_user_part_of> if user is valid and
         data_store['channels'] is empty
        Raises AccessError exception if user is not valid.
    """

    # Get and extract data from the data_store
    store = data_store.get()            # { [ { } ] }
    # store_user = store['users']         # Is a list
    store_channels = store['channels']  # Is a list of dictionaries

    # Raise AccessError if invalid auth_user_id
    # if not user_exists(store_user, auth_user_id):
    #     raise AccessError('Invalid user id')

    # Initialise return value
    return_all_channels = {'channels': []}
    
    # Looping through individual channels (dict) in the store_channels list
    for indv_channel in store_channels:
        # A temp new dictionary, with only channel_id & name key fields
        filtered_channel = {}
        filtered_channel['channel_id'] = indv_channel['channel_id']
        filtered_channel['name'] = indv_channel['name']

        # Take all channels (dict) and append to return value
        return_all_channels['channels'].append(filtered_channel)

    return return_all_channels

def channels_create_v1(auth_user_id, name, is_public):
    """
    User creates a private or public channel given a name and becomes an owner member of it

    Arguments:
        <auth_user_id> (int)    - The u_id of the user creating the channel
        <name>         (str)    - The name the user wants to call the created channel
        <is_public>    (bool)   - Determines whether the user wants to create a public or private channel

    Exceptions:
        InputError  - Occurs when name of channel is less than 1 char or more than 20
                    - Occurs when name of channel is the same as an existing channel
        AccessError - Occurs when auth_user_id is an invalid u_id and does not exist

    Return Value:
        Returns a dictionary with the key 'channel_id' containing the id of the created channel on success
    """
    # Raise AccessError if invalid auth_user_id
    # store = data_store.get()
    # user_list = store["users"]
    # if not user_exists(user_list, auth_user_id):
    #     raise AccessError("Invalid user id")

    # InputError when name of channel is less than 1 char or more than 20
    if len(name) < 1 or len(name) > 20:
        raise InputError('Channel name must be between 1 and 20 characters')

    # New channel id = Number of current channels + 1
    new_channel_id = len(data_store.get()["channels"]) + 1
    new_channel = {
        'channel_id': new_channel_id,
        'name': name,
        'is_public': is_public,
        'owner_members': [auth_user_id],
        'all_members': [auth_user_id],
        'messages': []
    }
    # Store new channel in data_store
    data_copy = data_store.get()
    data_copy['channels'].append(new_channel)
    data_store.set(data_copy)
    return {
        'channel_id': new_channel_id,
    }
    