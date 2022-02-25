from src.data_store import data_store
from src.error import AccessError, InputError
from src.other import user_exists, get_members_details

def users_all_v1(auth_user_id):
    """
    Returns a list of all users and their associated details.

    Arguments:
        <auth_user_id> (int)   - The u_id of the user attempting to receive all users details

    Exceptions:
        AccessError - Occurs when auth_user_id (token) is an invalid u_id (token) and does not exist

    Return Value:
        Returns a list of dictionaries where each dictionary contains users
    """

    store = data_store.get()
    user_list = store["users"]

    # # Raise AccessError if invalid auth_user_id
    # if not user_exists(user_list, auth_user_id):
    #     raise AccessError("Invalid user id")

    # Make a list of all u_ids
    all_u_ids = []
    for user in user_list:
        all_u_ids.append(user['auth_user_id'])
    
    return {'users': get_members_details(all_u_ids)}

def user_profile_v1(auth_user_id, u_id):
    """
    For a valid user, returns information about their user_id, email, first name, last name, and handle

    Arguments:
        <auth_user_id> (int)   - The u_id of the user attempting to receive a users details
        <u_id>         (int)   - The u_id of the user whom their profile will be retrieved

    Exceptions:
        InputError - Occurs when u_id does not refer to a valid user
        AccessError - Occurs when auth_user_id is an invalid u_id and does not exist

    Return Value:
        Returns a dictionary containing the u_id, email, name_first, name_last, handle_str of a user
    """
    store = data_store.get()
    user_list = store["users"]
    # # Raise AccessError if invalid auth_user_id
    # if not user_exists(user_list, auth_user_id):
    #     raise AccessError("Invalid auth user id")

    # Raise InputError if invalid u_id
    if not user_exists(user_list, u_id):
        raise InputError("Invalid user id")

    # Put u_id into a list so it can be passed into get_member_details functions which takes in a list of u_ids
    list_with_one_id = [u_id]
    # Access first dictionary since there is only 1
    return {'user': get_members_details(list_with_one_id)[0]}
