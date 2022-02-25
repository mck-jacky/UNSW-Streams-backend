# A file to store tests' helper functions.

SUCCESS = 200
INPUT_ERROR = 400
ACCESS_ERROR = 403

import pytest
import requests
import json
from src import config
import jwt
import src.other

def post_channel_invite(token, channel_id, u_id):
    return requests.post(
            config.url + 'channel/invite/v2',
            json = {
                'token': token, 
                'channel_id': channel_id,
                'u_id': u_id
            }
        )
        
def post_dm_create(token, u_ids):
    return requests.post(config.url + 'dm/create/v1', 
                         json={'token': token, 'u_ids': u_ids})

def post_message_send(token, channel_id, message):
    return requests.post(
                         config.url + 'message/send/v1',
                         json={'token': token,
                               'channel_id': channel_id,
                               'message': message
                               }
                        )
