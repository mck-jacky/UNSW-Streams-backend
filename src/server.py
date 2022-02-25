# Python Imports
import jwt
import signal
import sys
import re
import requests
from flask import Flask, request
from flask_cors import CORS
from json import dumps

# Server Configuration Import
from src import config

# Iteration 1 & 2 Function Imports
from src.admin import admin_userpermission_change_v1
from src.auth import auth_register_v1, auth_login_v1, name_has_incorrect_length, email_is_invalid
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.channel import channel_details_v1, channel_join_v1, channel_leave_v1, channel_invite_v1, channel_addowner_v1, channel_removeowner_v1, channel_messages_v1
from src.auth import auth_register_v1, auth_login_v1
from src.message import message_send_v1, message_edit_v1, message_remove_v1, message_senddm_v1, message_react_v1, message_unreact_v1, message_pin_v1, message_unpin_v1, message_share_v1
from src.admin import admin_userpermission_change_v1, admin_user_remove_v1
from src.data_store import data_store
from src.error import InputError
from src.dm import dm_create_v1, dm_remove_v1, dm_list_v1, dm_details_v1, dm_leave_v1, dm_messages_v1
from src.other import clear_v1, decrypt_token, is_valid_token, search_v1, notifications_get_v1
from src.user import user_profile_v1, users_all_v1

#### Token Encrypt/Decrypt Key #################################################

SUPERSECRETPASSWORD = "StampsWithAlpacas"

################################################################################

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS ########################

# Example
# @APP.route("/echo", methods=['GET'])
# def echo():
#     data = request.args.get('data')
#     if data == 'echo':
#    	    raise InputError(description='Cannot echo "echo"')
#     return dumps({
#         'data': data
#     })

@APP.route("/auth/login/v2", methods=['POST'])
def auth_login_v2():
    data = request.get_json()
    response = auth_login_v1(data['email'], data['password'])
    return dumps({
        'token': response['token'],
        'auth_user_id': response['auth_user_id']
    })

@APP.route("/auth/register/v2", methods=['POST'])
def auth_register_v2():
    data = request.get_json()
    
    ret = auth_register_v1(data['email'], data['password'], data['name_first'], data['name_last'])
    
    return dumps({
        'token': ret['token'],
        'auth_user_id': ret['auth_user_id']
    })

@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout_v1():
    """
    Given an active token, invalidates the token to log the user out.

    Http request body input:
        token: <token>
            The token is a string with a header, body and signature that is generated and
            returned when logging in. It is used to verify a user, when he makes requests.
            
    Return Value:
        Returns an empty json dictionary.
    """
    data = request.get_json()
    # decode the token
    decoded_token = decrypt_token(data['token'])

    data_save = data_store.get()
    # find the user, to which the token belongs to and delete the token from the
    # session_ids list
    for user in data_save['users']:
        if decoded_token['auth_user_id'] == user['auth_user_id']:
            user['session_ids'].remove(decoded_token['session_id'])
    data_store.set(data_save)
    return dumps({})

@APP.route("/channels/create/v2", methods=['POST'])
def channels_create_v2():
    data = request.get_json()

    info = decrypt_token(data['token'])
    
    ret = channels_create_v1(int(info['auth_user_id']), data['name'], data['is_public'])
    return dumps({
        'channel_id': ret['channel_id']
    })

@APP.route("/channels/list/v2", methods=['GET'])
def list_channels_v2():
    token = request.args.get('token')

    info = decrypt_token(token)
    
    ret = channels_list_v1(int(info['auth_user_id']))
    return dumps({
        'channels': ret['channels']
    })

@APP.route("/channels/listall/v2", methods=['GET'])
def listall_channels_v2():
    token = request.args.get('token')

    info = decrypt_token(token)
    
    ret = channels_listall_v1(int(info['auth_user_id']))
    return dumps({
        'channels': ret['channels']
    })

@APP.route("/channel/details/v2", methods=['GET'])
def channel_details_v2():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')

    info = decrypt_token(token)
    
    ret = channel_details_v1(int(info['auth_user_id']), int(channel_id))
    return dumps({
        'name': ret['name'],
        'is_public': ret['is_public'],
        'owner_members': ret['owner_members'],
        'all_members': ret['all_members']
    })

@APP.route("/channel/join/v2", methods=['POST'])
def channel_join_v2():
    data = request.get_json()
    token = data['token']
    authid_sessionid = decrypt_token(token)
        
    channel_join_v1(int(authid_sessionid['auth_user_id']), int(data['channel_id']))
    
    return dumps({})

@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_v2():
    data = request.get_json()
    token = data['token']
    authid_seshid = decrypt_token(token)
        
    channel_invite_v1(int(authid_seshid['auth_user_id']), int(data['channel_id']),
                          int(data['u_id']))
    
    return dumps({})

@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages_v2():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    start = request.args.get('start')

    info = decrypt_token(token)
    
    ret = channel_messages_v1(int(info['auth_user_id']), int(channel_id), int(start))
    return dumps({
        'messages': ret['messages'],
        'start': ret['start'],
        'end': ret['end']
    })
    

@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave():
    data = request.get_json()
    token = data['token']
    authid_sessionid = decrypt_token(token)
    
    channel_leave_v1(int(authid_sessionid['auth_user_id']), int(data['channel_id']))
    
    return dumps({})

@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner():
    data = request.get_json()
    token = data['token']
    authid_sessionid = decrypt_token(token)
    
    channel_addowner_v1(int(authid_sessionid['auth_user_id']), int(data['channel_id']),
                        int(data['u_id']))
    
    return dumps({})

@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner():
    data = request.get_json()
    token = data['token']
    authid_sessionid = decrypt_token(token)
    
    channel_removeowner_v1(int(authid_sessionid['auth_user_id']),
                           int(data['channel_id']), int(data['u_id']))
    
    return dumps({})

@APP.route("/message/send/v1", methods=['POST'])
def message_send():
    data = request.get_json()
    
    info = decrypt_token(data['token'])
    
    ret = message_send_v1(int(info['auth_user_id']), int(data['channel_id']), data['message'])
    return dumps({"message_id": ret["message_id"]})

@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit():
    data = request.get_json()

    info = decrypt_token(data['token'])
    
    message_edit_v1(int(info['auth_user_id']), int(data["message_id"]), data["message"])
    return dumps({})

@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove():
    data = request.get_json()

    info = decrypt_token(data['token'])
    
    message_remove_v1(int(info['auth_user_id']), int(data["message_id"]))
    return dumps({})

@APP.route("/dm/create/v1", methods=['POST'])
def create_dm_v1():
    data = request.get_json()

    info = decrypt_token(data['token'])
    
    ret = dm_create_v1(int(info['auth_user_id']), data['u_ids'])
    return dumps({
        'dm_id': ret['dm_id']
    })

@APP.route("/dm/list/v1", methods=['GET'])
def list_dm_v1():
    token = request.args.get('token')

    info = decrypt_token(token)
    
    ret = dm_list_v1(int(info['auth_user_id']))
    return dumps({
        'dms': ret['dms']
    })

@APP.route("/dm/remove/v1", methods=['DELETE'])
def remove_dm_v1():
    data = request.get_json()

    info = decrypt_token(data['token'])
    
    dm_remove_v1(int(info['auth_user_id']), int(data['dm_id']))
    return dumps({})

@APP.route("/dm/details/v1", methods=['GET'])
def details_dm_v1():
    token = request.args.get('token')
    dm_id = request.args.get('dm_id')

    info = decrypt_token(token)
    
    ret = dm_details_v1(int(info['auth_user_id']), int(dm_id))
    return dumps({
        'name': ret['name'],
        'members': ret['members']
    })

@APP.route("/dm/leave/v1", methods=['POST'])
def leave_dm_v1():
    data = request.get_json()
    token = data['token']
    authid_sessionid = decrypt_token(token)
    
    dm_leave_v1(int(authid_sessionid['auth_user_id']), int(data['dm_id']))
    
    return dumps({})

@APP.route("/dm/messages/v1", methods=['GET'])
def messages_dm_v1():
    token = request.args.get('token')
    dm_id = request.args.get('dm_id')
    start = request.args.get('start')

    info = decrypt_token(token)
    
    ret = dm_messages_v1(int(info['auth_user_id']), int(dm_id), int(start))
    return dumps({
        'messages': ret['messages'],
        'start': ret['start'],
        'end': ret['end']
    })

@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm():
    data = request.get_json()

    info = decrypt_token(data['token'])
    
    ret = message_senddm_v1(int(info["auth_user_id"]), int(data["dm_id"]), data["message"])
    return dumps({"message_id": ret["message_id"]})

@APP.route("/users/all/v1", methods=['GET'])
def all_users_details():
    token = request.args.get('token')

    info = decrypt_token(token)
    
    ret = users_all_v1(int(info['auth_user_id']))
    return dumps(ret)

@APP.route("/user/profile/v1", methods=['GET'])
def user_profile():
    token = request.args.get('token')
    u_id = request.args.get('u_id')

    info = decrypt_token(token)
    
    ret = user_profile_v1(int(info['auth_user_id']), int(u_id))
    return dumps(ret)
    
@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_setname_v1():
    """
    Updates the authorised user's first and last name, according to the user's input.

    Http request body input:
        token: <token>
            The token is a string with a header, body and signature that is generated and
            returned when logging in. It is used to verify a user, when he makes requests.
        name_first: <name_first>
            The first name is a string of ASCII characters,
            that has a length of 1-50 chars.
        name_last: <name_last>
            The last name is a string of ASCII characters,
            that has a length of 1-50 chars.

    Exceptions:
        InputError - The input error occurs if
         - the first or last name does not meet the required length

    Return Value:
        Returns an empty json dictionary.
    """
    data = request.get_json()
    
    # check if the name length is correct
    if name_has_incorrect_length(data['name_first'], data['name_last']):
        raise InputError('Entered name has to be between 1 and 50 chars long')

    # decode the token
    decoded_token = decrypt_token(data['token'])
    
    data_save = data_store.get()

    # find the user in the list of users and update the first and last name
    for user in data_save['users']:
        if decoded_token['auth_user_id'] == user['auth_user_id']:
            user['name_first'] = data['name_first']
            user['name_last'] = data['name_last']
    data_store.set(data_save)
    
    return dumps({})

@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_setemail_v1():    
    """
    Updates the authorised user's email, according to the user's input.

    Http request body input:
        email: <email>
            The email is a string with a very particular design.
            Regarding the string design, see description of auth_register_v1. 
        token: <token>
            The token is a string with a header, body and signature that is generated and
            returned when logging in. It is used to verify a user, when he makes requests.

    Exceptions:
        InputError - The input error occurs if
         - the email does not fit the previously described format
         - the email that is used, already exists

    Return Value:
        Returns an empty json dictionary.
    """

    data = request.get_json()

    # decode the token
    decoded_token = decrypt_token(data['token'])

    # check if the email is valid and not yet taken
    if email_is_invalid(data['email'], decoded_token['auth_user_id']):
        raise InputError('email is not valid or taken')

    # find the user in the list of users and update the email
    data_save = data_store.get()
    for user in data_save['users']:
        if decoded_token['auth_user_id'] == user['auth_user_id']:
            user['email'] = data['email']
    data_store.set(data_save)
    return dumps({})

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_sethandle_v1(): 
    """
    Updates the authorised user's name handle, according to the user's input.

    Http request body input:
        handle_str: <handle_str>
            The user's handle is a alphanumeric string between 3 and 20 chars, that is
            used as display name. It mustn't be taken by another user.
        token: <token>
            The token is a string with a header, body and signature that is generated and
            returned when logging in. It is used to verify a user, when he makes requests.

    Exceptions:
        InputError - The input error occurs if
         - handle_str contains characters that are not alphanumeric
         - the handle is already used by another user
         - length of handle_str is not between 3 and 20 characters inclusive

    Return Value:
        Returns an empty json dictionary.
    """

    data = request.get_json()
    
    # check if the handle_str has the correct length
    if len(str(data['handle_str'])) < 3 or len(str(data['handle_str'])) > 20:
        raise InputError('handle_str has to be between 3 and 20 chars inclusive')
    
    # check if the handle_str is alphanumeric
    if re.search(r'\W|_', str(data['handle_str'])):
        raise InputError('handle_str must be alphanumeric')

    # decode the token
    decoded_token = decrypt_token(data['token'])

    # browse throught the list of users to assess whether the handle_str is
    # already taken
    data_save = data_store.get()
    for user in data_save['users']:
        if user['name_handle'] == str(data['handle_str']) and decoded_token['auth_user_id'] != user['auth_user_id']:
            raise InputError('handle_str is already used by another user')

    # find the user in the list of users and update the handle_str
    for user in data_save['users']:
        if decoded_token['auth_user_id'] == user['auth_user_id']:
            user['name_handle'] = str(data['handle_str'])
    data_store.set(data_save)
    return dumps({})

@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_remove_user_v1():
    data = request.get_json()

    info = decrypt_token(data['token'])
    
    admin_user_remove_v1(int(info['auth_user_id']), data['u_id'])
    return dumps({})

@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def admin_userpermission_change():
    data = request.get_json()
    token = data['token']
    authid_seshid = decrypt_token(token)
    
    admin_userpermission_change_v1(authid_seshid['auth_user_id'], data['u_id'],
                                   data['permission_id'])
    return dumps({})

@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    clear_v1()
    return dumps({})


@APP.route("/notifications/get/v1", methods=["GET"])
def notifications_get():
    token = request.args.get('token')
    auth_user_id = decrypt_token(token)['auth_user_id']
    
    return dumps(notifications_get_v1(auth_user_id))

"""

"""
@APP.route("/search/v1", methods=["GET"])
def search_route():
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    
    auth_user_id = decrypt_token(token)['auth_user_id']
    
    return dumps(search_v1(auth_user_id, query_str))
    
@APP.route("/message/share/v1", methods=["POST"])
def message_share():
    data = request.get_json()
    
    info = decrypt_token(data['token'])

    ret = message_share_v1(int(info['auth_user_id']), int(data['og_message_id']), data['message'], int(data['channel_id']), int(data['dm_id']))
    return dumps({'shared_message_id': ret['shared_message_id']})

@APP.route("/message/react/v1", methods=["POST"])
def message_react():
    data = request.get_json()
    
    info = decrypt_token(data['token'])

    message_react_v1(int(info['auth_user_id']), int(data["message_id"]), int(data["react_id"]))
    return dumps({})

@APP.route("/message/unreact/v1", methods=["POST"])
def message_unreact():
    data = request.get_json()
    
    info = decrypt_token(data['token'])

    message_unreact_v1(int(info['auth_user_id']), int(data["message_id"]), int(data["react_id"]))
    return dumps({})

@APP.route("/message/pin/v1", methods=["POST"])
def message_pin():
    data = request.get_json()
    
    info = decrypt_token(data['token'])

    message_pin_v1(int(info['auth_user_id']), int(data["message_id"]))
    return dumps({})

@APP.route("/message/unpin/v1", methods=["POST"])
def message_unpin():
    data = request.get_json()
    
    info = decrypt_token(data['token'])

    message_unpin_v1(int(info['auth_user_id']), int(data["message_id"]))
    return dumps({})

"""
@APP.route("/message/sendlater/v1", methods=["POST"])

@APP.route("/message/sendlaterdm/v1", methods=["POST"])

@APP.route("/standup/start/v1", methods=["POST"])

@APP.route("/standup/active/v1", methods=["GET"])

@APP.route("/standup/send/v1", methods=["POST"])

@APP.route("/auth/passwordreset/request/v1", methods=["POST"])

@APP.route("/auth/passwordreset/reset/v1", methods=["POST"])

@APP.route("/user/profile/uploadphoto/v1", methods=["POST"])

@APP.route("/user/stats/v1", methods=["GET"])

@APP.route("/users/stats/v1", methods=["GET"])

"""

#### NO NEED TO MODIFY BELOW THIS POINT ########################################

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(debug=False,port=config.port) # Do not edit this port
