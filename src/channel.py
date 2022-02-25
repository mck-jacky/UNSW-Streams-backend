from src.data_store import data_store
from src.error import AccessError, InputError
from src.other import channel_exists, user_exists, user_is_member, \
                      num_of_messages, get_members_details, notification_send, format_message

def channel_details_v1(auth_user_id, channel_id):
    """
    Given a channel with ID channel_id that the authorised user is a member of, provide basic details about the channel.

    Arguments:
        <auth_user_id> (int)    - The u_id of the user creating the channel
        <channel_id>   (int)    - The id of the specified channel the user wants to get details from

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel
        AccessError - Occurs when channel_id is valid but the authorised user is not a member of the channel
                    - Occurs when auth_user_id is an invalid u_id and does not exist

    Return Value:
        Returns a dictionary with the key 'channel_id' containing the id of the created channel on success
    """
    # Raise AccessError if invalid auth_user_id
    store = data_store.get()
    # user_list = store["users"]
    # if not user_exists(user_list, auth_user_id):
    #     raise AccessError("Invalid user id")
    
    channel_exists = False
    user_is_member = False
    chosen_channel = {}
    for channel in store['channels']:
        # Check if channel id is an existing channel
        if channel['channel_id'] == channel_id:
            channel_exists = True
            # Check if auth_user_id is in specified channel
            for u_id in channel['all_members']:  
                if auth_user_id == u_id:
                    user_is_member = True
            chosen_channel = channel
            break

    # InputError - channel_id does not refer to a valid channel
    if channel_exists == False: 
        raise InputError('channel_id does not refer to a valid channel')
    # AccessError - channel_id is valid but the authorised user is not a member of the channel
    if channel_exists and user_is_member == False:
        raise AccessError('Authorised user is not a member of the channel')

    return {
        'name': chosen_channel['name'],
        'is_public': chosen_channel['is_public'],
        'owner_members': get_members_details(chosen_channel['owner_members']),
        'all_members': get_members_details(chosen_channel['all_members']),
    }

def channel_messages_v1(auth_user_id, channel_id, start):
    """
    Given a channel with ID channel_id that the authorised user is a member of,
    return up to 50 messages between index "start" and "start + 50". Message
    with index 0 is the most recent message in the channel. This function
    returns a new index "end" which is the value of "start + 50", or, if this
    function has returned the least recent messages in the channel, returns -1
    in "end" to indicate there are no more messages to load after this return.
    
    Arguments:
    <auth_user_id> (<int>)  - <the id of a user>
    <channel_id>   (<int>)  - <the channel id>
    <start>        (<int>)  - <index of the first message to print>
    ...

    Exceptions:
    InputError  - Occurs when channel_id does not refer to a valid channel
                - Occurs when start is greater than the total number of messages in the channel
    AccessError - Occurs when channel_id is valid and the authorised user is not a member of the channel

    Return Value:
    Returns {messages, start, end}
    """
    store = data_store.get()
    channel_list = store["channels"]
    total_messages = num_of_messages(channel_list, channel_id)
    temp_list = []
    messages_list = []

    # AccessError check if the channel_id is valid and the authorised user is not a member of the channel
    if not channel_exists(channel_list, channel_id):
        raise InputError("Invalid Channel id")
    
    if not user_is_member(auth_user_id, channel_list, channel_id):
        raise AccessError("Inputted user is not a member of this channel")

    if total_messages == 0 and start == 0:
        end = -1
        return {'messages': messages_list, 'start': int(start), 'end': int(end)}

    # InputError start index >= total number of messages
    if start >= total_messages:
        raise InputError("Inputted Start index is greater than the total number of messages in the channel")

    # Get the channel with channel_id
    for channel in channel_list:
        if channel["channel_id"] == channel_id:
            target_channel = channel

    temp_list = target_channel["messages"][start : start + 50]

    for message in temp_list:
        messages_list.append(format_message(message, auth_user_id))

    end = int(start) + 50
    if end >= total_messages:
        end = -1
        
    return {'messages': messages_list, 'start': int(start), 'end': int(end)}


#### Channel Join Feature ####
        
# Check if user is a global owner  
def is_global_owner(users, auth_user_id):
    for user in users:
        if user['auth_user_id'] == auth_user_id:
            if user['permission_id'] == 1: # permission_id = 1 for global owners
                return True
            else:
                return False
    #raise InputError("Could not find user in data base") #shouldn't reach here in most cases
    #return False
            

# Check if channel_id refers to a private channel, and if user is an
# owner of that channel.
# Does not check if channel is exists (shouldn't raise an access error if 
# channel doesn't exist)
def is_private_channel(channels, channel_id):
    for channel in channels:
        if channel['channel_id'] == channel_id:
            if channel['is_public'] == False:
                # Channel is private
                return True
            else:
                # Channel is public
                return False
    #raise InputError("Could not find channel in data base") #shouldn't reach here in most cases
    #return False

def user_is_channel_owner(auth_user_id, channels, channel_id):
    for channel in channels:
        if channel['channel_id'] == channel_id:
            if auth_user_id in channel['owner_members']:
                return True
            else:
                return False
            
    #raise InputError("Could not find channel in data base") #shouldn't reach here in most cases
    #return False

""" MOVED TO other.py
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
"""

# Given a channel_id of a channel that the authorised user can join,
# adds them to that channel.
def channel_join_v1(auth_user_id, channel_id):
    """
    Insert auth_user_id into channel_id's "all_members" list, if authorised to do so.
    Authorised when the channel is public, or if the channel is private auth_user_id
    must refer to a user who is a channel owner or a global owner.

    Arguments:
        auth_user_id (integer)  - the user id of the member joining the channel
        channel_id   (integer)  - the channel_id of the channel being joined
        
    Exceptions:
        InputError  - Occurs when:
            a) channel_id does not refer to a valid channel
            b) auth_user_id refers to a user who is already a member of the channel
        AccessError - Occurs when:
            a) channel_id refers to a channel that is private and the authorised
            user is not already a channel member and is not a global owner.

    Return Value:
        Returns {} always. (an empty dictionary)
    """
    
    store = data_store.get()
    users = store['users']
    channels = store['channels']
    
    # Checks:
    # if not user_exists(users, auth_user_id):
    #     raise AccessError("User does not exist")

    if not channel_exists(channels, channel_id):
        raise InputError("Inputted channel does not exist")
        
    if user_is_member(auth_user_id, channels, channel_id):
        raise InputError("User is already a member of the channel to be joined.")
    
    #if not (user_is_private_owner(auth_user_id, channels, channel_id) or \
    #    is_global_owner(users, auth_user_id)):
    if is_private_channel(channels, channel_id) and not is_global_owner(users, auth_user_id):
        raise AccessError("User is not authorised to join this private channel.")
        # Don't need to check if user is a channel owner, as there will never
        # be any channel owners since they are not in the channel yet.

    
    # Add user to channel:
    for channel in channels:
        if channel['channel_id'] == channel_id: # find the right channel
            channel['all_members'].append(auth_user_id) # add user id to channel
    
    store['channels'] = channels
    data_store.set(store)
    
    return {
    }

#### channel addowner feature ####

def channel_addowner_v1(auth_user_id, channel_id, u_id):
    """
    'auth_user_id' invites 'u_id' to be an owner of 'channel_id'. Works if auth_user_id
    has owner permissions

    Arguments:
        auth_user_id (integer)  - the user id of the admin/channel owner
        channel_id   (integer)  - the channel_id of the channel 
        u_id         (integer)  - the user id of the member having their permissions changed

    Exceptions:
        InputError  - Occurs when:
            a) channel_id does not refer to a valid channel
            b) u_id does not refer to a valid user
            c) u_id refers to a user who is not a member of the channel
            d) u_id refers to a user who is already an owner of the channel
        AccessError - Occurs when:
            a) channel_id is valid and the authorised user does not have owner permissions in the channel
            
    Return Value:
        Returns {} always. (an empty dictionary)
    """
    store = data_store.get()
    users = store['users']
    channels = store['channels']
    
    # Check auth_user_id is an existing user
    # if not user_exists(users, auth_user_id):
    #     raise AccessError("User doing the inviting does not exist")
    
    # Check channel_id is an existing channel
    if not channel_exists(channels, channel_id):
        raise InputError("Inputted channel does not exist")

    # Check auth_user_id has permission. NOTE: "Channel owner permissions" means
    # the user is a channel owner, or a user is a global owner AND a channel member.
    elif not (user_is_channel_owner(auth_user_id, channels, channel_id) or 
              (is_global_owner(users, auth_user_id) and 
               user_is_member(auth_user_id, channels, channel_id))): 
        raise AccessError("User does not have permission change permissions in this channel")
    
    # Check u_id is an existing user
    if not user_exists(users, u_id):
        raise InputError("User to have their permission changed does not exist")
    
    # Check if u_id is in channel_id 
    if not user_is_member(u_id, channels, channel_id):
        raise InputError("User can not be made a channel owner as they are not a member yet")
    
    # Check if u_id is already a channel owner of channel_id
    if user_is_channel_owner(u_id, channels, channel_id):
        raise InputError("User is already a channel owner")
        
    # add u_id as a channel owner of channel_id
    for channel in channels:
        if channel['channel_id'] == channel_id:
            channel['owner_members'].append(u_id)
    
    # Store the new data:
    store['channels'] = channels
    data_store.set(store)
    #print(store)
    
    return {}



#### Channel Invite Feature ####

""" MOVED TO other.py
# Check if user exists
def user_exists(users, user_id):
    for user in users:
        if user['auth_user_id'] == user_id:
            return True
    return False
"""

    

def channel_invite_v1(auth_user_id, channel_id, u_id):
    """
    'auth_user_id' invites 'u_id' to join 'channel_id'. Works if auth_user_id is
    a member of channel_id.

    Arguments:
        auth_user_id (integer)  - the user id of the member doing the inviting
        channel_id   (integer)  - the channel_id of the channel being invited to
        u_id         (integer)  - the user id of the member being invited

    Exceptions:
        InputError  - Occurs when:
            a) channel_id does not refer to a valid channel
            b) u_id does not refer to a valid user
            c) u_id refers to a user who is already a member of the channel
        AccessError - Occurs when:
            a) channel_id is valid and the authorised user is not a member of the channel
            b) auth_user_id does not refer to a valid user

    Return Value:
        Returns {} always. (an empty dictionary)
    """

    store = data_store.get()
    users = store['users']
    channels = store['channels']
    
    # Check auth_user_id is an existing user
    # if not user_exists(users, auth_user_id):
    #     raise AccessError("User doing the inviting does not exist")
    
    # Check channel_id is an existing channel
    if not channel_exists(channels, channel_id):
        raise InputError("Inputted channel does not exist")

    # Check auth_user_id is a member of channel_id (i.e. has permission to invite)
    elif not user_is_member(auth_user_id, channels, channel_id):
        raise AccessError("User does not have permission to invite to this channel")
        #pass
        
    # Check u_id is an existing user
    if not user_exists(users, u_id):
        raise InputError("User to be invited does not exist")
    
    # Check if u_id is already in channel_id 
    if user_is_member(u_id, channels, channel_id):
        raise InputError("User to be invited is already a member of this channel")
    
    # Add user to channel:
    for channel in channels:
        if channel['channel_id'] == channel_id: # find the right channel
            #print (f"{channel['name']} had members: {channel['all_members']}")
            channel['all_members'].append(u_id) # add u_id to channel
            #print (f"{channel['name']} has members: {channel['all_members']}")
            
            # Send notification to u_id:
            notification_send(auth_user_id, u_id, f" added you to {channel['name']}",
                              channel_id = channel_id)
    
    
    
    
    store['channels'] = channels
    data_store.set(store)



    return {
    }



##### Channel Leave Feature ######

def channel_leave_v1(auth_user_id, channel_id):
    """
    Allows a user to leave a channel

    Arguments:
        auth_user_id (string)   - the auth_user_id of the user id trying to leave
        channel_id   (integer)  - the channel_id of the channel being left

    Exceptions:
        InputError  - Occurs when:
            a) channel_id does not refer to a valid channel
        AccessError - Occurs when:
            a) channel_id is valid and the authorised user is not a member of the channel
            b) auth_user_id does not refer to a valid/existing user.

    Return Value:
        Returns {} always. (an empty dictionary)
    """
    store = data_store.get()
    # users = store['users']
    channels = store['channels']
    
    # Check if user exists:
    # if not user_exists(users, auth_user_id):
    #     raise AccessError("auth_user_id does not refer to an existing user.")
    
    # Check if channel exists:
    if not channel_exists(channels, channel_id):
        raise InputError("Channel does not exist")
        
    # Check if user is a member of the channel
    if not user_is_member(auth_user_id, channels, channel_id):
        raise AccessError("User cannot leave a channel which they are not a member of.")
        
    # Leave the channel (remove auth_user_id from 'all_members' and 'owner_members', if it is part of the lists)
    for channel in channels:
        if channel_id == channel['channel_id']:
            channel['owner_members'] = list(filter(lambda m: m != auth_user_id, channel['owner_members']))
            channel['all_members']   = list(filter(lambda m: m != auth_user_id, channel['all_members']))
    
    # Store the new data:
    store['channels'] = channels
    data_store.set(store)
    
    return {}

#### Channel removeowner feature ####
def has_one_owner(channels, channel_id):
    
    for channel in channels:
        if channel['channel_id'] == channel_id:
            if len(channel['owner_members']) == 1:
                return True
            else:
                return False
    # Should reach here, but if it does it is because channel_id doesn't exist.
    #raise InputError("Channel_id doesn't exist")
    #return False



def channel_removeowner_v1(auth_user_id, channel_id, u_id):
    """
    'auth_user_id' removes the channel owner permission from 'u_id'.
    Works if auth_user_id has owner permissions.

    Arguments:
        auth_user_id (integer)  - the user id of the admin/channel owner
        channel_id   (integer)  - the channel_id of the channel 
        u_id         (integer)  - the user id of the member having their permissions removed

    Exceptions:
        InputError  - Occurs when:
            a) channel_id does not refer to a valid channel
            b) u_id does not refer to a valid user
            c) u_id refers to a user who is not an owner of the channel
            d) u_id refers to a user who is currently the only owner of the channel
        AccessError - Occurs when:
            a) channel_id is valid and the authorised user does not have owner permissions in the channel
            
    Return Value:
        Returns {} always. (an empty dictionary)
    """

    store = data_store.get()
    users = store['users']
    channels = store['channels']
    
    # Check auth_user_id is an existing user:
    # if not user_exists(users, auth_user_id):
    #     raise AccessError("User doing the inviting does not exist")
    
    # Check channel_id is an existing channel:
    if not channel_exists(channels, channel_id):
        raise InputError("Inputted channel does not exist")

    # Check auth_user_id has permission:
    elif not ( user_is_channel_owner(auth_user_id, channels, channel_id) or \
               (is_global_owner(users, auth_user_id) and 
               user_is_member(auth_user_id, channels, channel_id)) ):
        raise AccessError("User does not have permission change permissions in this channel")
    
    # Check u_id is an existing user:
    if not user_exists(users, u_id):
        raise InputError("User to have their permission changed does not exist")
    
    # Check if u_id is the sole channel owner:
    if user_is_channel_owner(u_id, channels, channel_id) and has_one_owner(channels, channel_id):
        raise InputError("The sole channel owner cannot be removed")
    
    """ 
    May not need this as we already check if user is a channel owner, since
    you can't be a channel owner without being a member in iteration 2.
    # Check if u_id is in channel_id 
    if not user_is_member(u_id, channels, channel_id):
        raise InputError("User can not be made a channel owner as they are not a member yet")
    """
    
    # Check if u_id is already a channel owner of channel_id
    if not user_is_channel_owner(u_id, channels, channel_id):
        raise InputError("User is already not a channel owner")
        
    # Remove channel owner permissions from u_id in channel_id:
    for channel in channels:
        if channel['channel_id'] == channel_id:
            channel['owner_members'] = list(filter(lambda n: n != u_id, channel['owner_members']))
    
    # Store the new data:
    store['channels'] = channels
    data_store.set(store)
    
    print(store)
    
    return {}
