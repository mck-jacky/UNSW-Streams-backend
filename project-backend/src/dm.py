from src.data_store import data_store
from src.error import AccessError, InputError
from src.other import get_members_details, user_exists, create_dm_name, check_if_valid_dm, check_if_member_of_dm, notification_send

def dm_create_v1(auth_user_id, u_ids):
    """
    Given a list of u_ids not including the owner, create a DM. The name is an alphabetically-sorted, comma-and-space-separated list of user handles

    Arguments:
        <auth_user_id> (int)   - The u_id of the user creating the DM
        <u_ids> (list of ints) - A list containing the u_ids that the DM is directed to and will not include the creator

    Exceptions:
        InputError  - Occurs when any u_id in u_ids does not refer to a valid user
        AccessError - Occurs when auth_user_id (token) is an invalid u_id (token) and does not exist

    Return Value:
        Returns a dictionary with the key 'dm_id' containing the id of the created DM on success
    """
    # Raise AccessError if invalid auth_user_id
    store = data_store.get()
    user_list = store["users"]
    dms_list = store["dms"]

    # if not user_exists(user_list, auth_user_id):
    #     raise AccessError("Invalid user id")

    # Make a list of all u_ids
    all_u_ids = []
    for user in user_list:
        all_u_ids.append(user['auth_user_id'])
        
    # Raise InputError if any u_id in u_ids does not refer to a valid user
    for u_id in u_ids:
        if u_id not in all_u_ids:
            raise InputError('At least one u_id is invalid')
        
    #print(f" u_ids: {u_ids}")    

    dm_name = create_dm_name(auth_user_id, u_ids) # This also adds auth_user_id to u_ids
    #print(f" u_ids: {u_ids}")
    store['dm_id'] += 1
    new_dm_id = store['dm_id']
    new_dm = {
        'dm_id': new_dm_id,
        'owner_id': auth_user_id,  
        'u_ids': u_ids,    
        'name': dm_name,     
        'messages': []
    }
    
    # Send notification to u_ids:
    for u_id in u_ids:
        if u_id != auth_user_id:
            notification_send(auth_user_id, u_id, f" added you to {dm_name}",
                              dm_id = new_dm_id)
    #print(f"dm name: {dm_name}, u_ids: {u_ids}")
    
    
    dms_list.append(new_dm)
    data_store.set(store)
    return {
        'dm_id': new_dm_id
    }

def dm_list_v1(auth_user_id):
    """
    Returns the list of DMs that the user is a member of.

    Arguments:
        auth_user_id (int/str) - Can be valid or invalid; will be checked first.

    Exceptions:
        AccessError - When auth_user is invalid.

    Return Value:
        If DMs exist, returns a list of dictionaries, where each dictionary
         contains the keys 'dm_id' and 'name'.
        Else, returns dictionary with an empty list.
    """
    
    # Get and extract data from the data_store
    store = data_store.get()  # { [ { } ] }
    # store_users = store['users']
    store_dms = store['dms']

    # Raise AccessError if invalid auth_user_id
    # if not user_exists(store_users, auth_user_id):
    #     raise AccessError('Invalid user id')

    # {'dms': [ {'dm_id': A, 'name': B}, {'dm_id': C, 'name': D}, ...] }
    return_dm_list = {'dms': []}

    # Looping through individual dms (dict) in the store_dms list
    for indv_dms in store_dms:
        # If auth user is in users-who-can-receive-DM list
        # (Includes the DM owner)
        for member in indv_dms['u_ids']:
            if member == int(auth_user_id):
                # A temp new dictionary, with only 'dm_id' & 'name' keys
                single_dm_dict = {}
                single_dm_dict['dm_id'] = indv_dms['dm_id']
                single_dm_dict['name'] = indv_dms['name']
                return_dm_list['dms'].append(single_dm_dict)

    return return_dm_list

def dm_remove_v1(auth_user_id, dm_id):
    """
    Remove an existing DM, so all members are no longer in the DM. This can only
    be done by the original creator of the DM.

    Arguments:
        auth_user_id (int/str) - Can be valid or invalid; will be checked first.
        dm_id (int) - Can be valid or invalid; will be checked first.

    Exceptions:
        AccessError - When auth_user is invalid.
        AccessError - When dm_id is valid and the authorised user is not the
         original DM creator.
        InputError - When dm_id does not refer to a valid DM.

    Return Value:
        An empty dictionary.

    Assumptions:
        https://edstem.org/au/courses/7025/discussion/633332?comment=1449708
        If we remove members from a DM, DM owner and members are erased, but the
         DM still remains.
        Removed owners are replaced with None.
    """

    # Get and extract data from the data_store
    store = data_store.get()  # { [ { } ] }
    store_users = store['users']
    store_dms = store['dms']

    # Raise AccessError if invalid auth_user_id
    # if not user_exists(store_users, auth_user_id):
    #     raise AccessError('Invalid user id')

    # Raise InputError if DM is not valid
    if check_if_valid_dm(dm_id) == False:
        raise InputError('Invalid DM')
    
    # Raise AccessError if user is not the DM creator
    if check_if_member_of_dm(auth_user_id, dm_id) == 0 or \
        check_if_member_of_dm(auth_user_id, dm_id) == 2:
        
        raise AccessError('User is not creator of DM')

    unwanted_dms_list = []
    wanted_dms_list = []

    # Looping through individual dms (dict) in the store_dms list
    for indv_dms in store_dms:

        # OLD Method: Does not remove the DM dict, but just destroys its user IDs
        # # If auth_user is the owner of this DM
        # if int(auth_user_id) == int(indv_dms['owner_id']) and \
        #     int(dm_id) == int(indv_dms['dm_id']):

        #     # Owner of DM is removed
        #     indv_dms['owner_id'] = -1  # None cannot be iterated over
        #     # DM members list is cleared
        #     indv_dms['u_ids'] = []

        # NEW Method: Destroys the DM dict completely
        # If auth_user is the owner of this DM
        if int(auth_user_id) == int(indv_dms['owner_id']) and \
            int(dm_id) == int(indv_dms['dm_id']):

            unwanted_dms_list.append(indv_dms)

    for indv_dms in store_dms:
        if indv_dms not in unwanted_dms_list:
            wanted_dms_list.append(indv_dms)

    store_dms = wanted_dms_list

    store['users'] = store_users
    store['dms'] = store_dms
    data_store.set(store)

    return {}

def dm_details_v1(auth_user_id, dm_id):
    """
    Given a DM with ID dm_id that the authorised user is a member of, provide
    basic details about the DM.

    Arguments:
        auth_user_id (int/str) - Can be valid or invalid; will be checked first.
        dm_id (int) - Can be valid or invalid; will be checked first.

    Exceptions:
        AccessError - When auth_user is invalid.
        AccessError - When dm_id is valid and the authorised user is not a
         member of the DM.
        InputError - When dm_id does not refer to a valid DM.

    Return Value:
        If DMs exist, returns a list of dictionaries, where each dictionary
         contains the keys 'dm_id' and 'name'.
        Else, returns dictionary with an empty list.
    """

    # Get and extract data from the data_store
    store = data_store.get()  # { [ { } ] }
    # store_users = store['users']
    store_dms = store['dms']

    # Raise AccessError if invalid auth_user_id
    # if not user_exists(store_users, auth_user_id):
    #     raise AccessError('Invalid user id')

    # Raise InputError if DM is not valid
    if check_if_valid_dm(dm_id) == False:
        raise InputError('Invalid DM')
    
    # Raise AccessError if user is not a member of the DM
    if check_if_member_of_dm(auth_user_id, dm_id) == 0:
        raise AccessError('User is a member of the DM')

    # {'name': 'A', 'members': ['A', 'B', ...]}
    return_dm_details = {'name': '', 'members': []}

    # Looping through individual dms (dict) in the store_dms list
    for indv_dms in store_dms:
        # If auth user is in users-who-can-receive-DM list
        # (Includes the DM owner)
        for member in indv_dms['u_ids']:
            if member == int(auth_user_id):
                # Copy over the name and members from data_store into return
                return_dm_details['name'] = indv_dms['name']
                return_dm_details['members'] = get_members_details(indv_dms['u_ids'])
            
    return return_dm_details

def dm_leave_v1(auth_user_id, dm_id):
    """
    Given a DM ID, the user is removed as a member of this DM. The creator is
    allowed to leave and the DM will still exist if this happens. This does not
    update the name of the DM.

    Arguments:
        auth_user_id (int/str) - Can be valid or invalid; will be checked first.
        dm_id (int) - Can be valid or invalid; will be checked first.

    Exceptions:
        AccessError - When auth_user is invalid.
        AccessError - When dm_id is valid and the authorised user is not a
         member of the DM.
        InputError - When dm_id does not refer to a valid DM.

    Return Value:
        An empty dictionary.
    
    Assumptions:
        https://edstem.org/au/courses/7025/discussion/629536
        If we remove members from a DM, DM owner and members are erased, but the
         DM still remains.
        Removed owners are replaced with None.
        Will not test against a left owner who wants to remove a DM.
    """
    
    # Get and extract data from the data_store
    store = data_store.get()  # { [ { } ] }
    store_users = store['users']
    store_dms = store['dms']

    # Raise AccessError if invalid auth_user_id
    # if not user_exists(store_users, auth_user_id):
    #     raise AccessError('Invalid user id')

    # Raise InputError if DM is not valid
    if check_if_valid_dm(dm_id) == False:
        raise InputError('Invalid DM')
    
    # Raise AccessError if user is not a member of the DM
    if check_if_member_of_dm(auth_user_id, dm_id) == 0:
        raise AccessError('User is a not a member of the DM')

    # Looping through individual dms (dict) in the store_dms list
    for indv_dms in store_dms:

        # If auth_user is the owner of this DM
        if int(auth_user_id) == int(indv_dms['owner_id']) and \
            int(dm_id) == int(indv_dms['dm_id']):

            # DM owner is removed
            indv_dms['owner_id'] = -1  # None cannot be iterated over
            
            # DM owner is removed from the list of DM members
            indv_dms['u_ids'].remove(int(auth_user_id))
            
        # If auth_user is a member, not an owner, of this DM
        elif int(auth_user_id) in indv_dms['u_ids'] and \
            int(auth_user_id) != int(indv_dms['owner_id']) and \
            int(dm_id) == int(indv_dms['dm_id']):

            # auth_user is removed from the list of DM members
            indv_dms['u_ids'].remove(int(auth_user_id))
    
    store['users'] = store_users
    store['dms'] = store_dms
    data_store.set(store)

    return {}

def dm_messages_v1(auth_user_id, dm_id, start):
    """
    Given a DM with ID dm_id that the authorised user is a member of, return up
    to 50 messages between index "start" and "start + 50". Message with index 0
    is the most recent message in the DM.
    
    This function returns a new index "end" which is the value of "start + 50",
    or, if this function has returned the least recent messages in the DM,
    returns -1 in "end" to indicate there are no more messages to load after
    this return.

    Arguments:
        auth_user_id (int/str) - Can be valid or invalid; will be checked first.
        dm_id (int) - Can be valid or invalid; will be checked first.
        start (int) - 

    Exceptions:
        AccessError - When auth_user is invalid.
        AccessError - When dm_id is valid and the authorised user is not a
         member of the DM.
        InputError - When dm_id does not refer to a valid DM.
        InputError - When start is greater than the total number of messages in
         the DM.

    Return Value:
        A dictionary containing the keys: 'messages', 'start' and 'end'.
    """

    # # Get and extract data from the data_store
    store = data_store.get()  # { [ { } ] }
    # store_users = store['users']
    store_dms = store['dms']

    # # Raise AccessError if invalid auth_user_id
    # if not user_exists(store_users, auth_user_id):
    #     raise AccessError('Invalid user id')

    # # Raise InputError if DM is not valid
    if check_if_valid_dm(dm_id) == False:
        raise InputError('Invalid DM')
    
    # # Raise AccessError if user is not a member of the DM
    if check_if_member_of_dm(auth_user_id, dm_id) == 0:
        raise AccessError('User is not a member of this DM')

    # Variables storage for later use
    target_dm = None  # I.e., One of the dicts in dms list
    total_dm = 0      # Number of messages in said DM
    dm_list = []      # A list of dictionaries of the DMs

    # Raise InputError if start is greater than total number of DMs
    for indv_dms in store_dms:
        # Found the correct DM
        if int(dm_id) == int(indv_dms['dm_id']):
            target_dm = indv_dms
            total_dm = len(indv_dms['messages'])
            break
    
    if int(start) > total_dm:  # >=
        raise InputError('Start is greater than total number of DMs')

    # If there are no messages, and not an outrageous start, return default
    if total_dm == 0 and int(start) == 0:
        return {'messages': dm_list, 'start': int(start), 'end': -1}

    # Calculating whether there are no more messages after this 50-dm-batch
    end = int(start) + 50
    dm_list = target_dm['messages'][int(start):end]
    if end >= total_dm:
        end = -1

    return {'messages': dm_list, 'start': int(start), 'end': end}
