import pytest

from src.error import AccessError, InputError
from src.other import clear_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.message import message_send_v1, message_edit_v1, message_senddm_v1
from src.dm import dm_create_v1
from src.data_store import data_store
from src.channel import channel_join_v1
import requests
import json
from src import config

"""
InputError when any of:

    - length of message is over 1000 characters
    - message_id does not refer to a valid message within a channel/DM that the authorised user has joined

AccessError when message_id refers to a valid message in a joined channel/DM and none of the following are true:

    - the message was sent by the authorised user making this request
    - the authorised user has owner permissions in the channel/DM
"""

@pytest.fixture
def initialize():
    clear_v1()
    global token_1
    global token_2
    global token_3
    token_1 = auth_register_v1("email1@gmail.com", "password", "name_first1", "name_last1")["auth_user_id"]
    token_2 = auth_register_v1("email2@gmail.com", "password", "name_first2", "name_last2")["auth_user_id"]
    token_3 = auth_register_v1("email3@gmail.com", "password", "name_first3", "name_last3")["auth_user_id"]
    global channel_id_1
    global channel_id_2
    channel_id_1 = channels_create_v1(token_1, "channel1", True)['channel_id']
    channel_join_v1(token_3, channel_id_1)
    channel_id_2 = channels_create_v1(token_2, "channel2", True)['channel_id']
    channel_join_v1(token_3, channel_id_2)

    global dm_id1
    global dm_id2
    global dm_id3
    dm_id1 = dm_create_v1(token_1, [token_2, token_3])["dm_id"]
    dm_id2 = dm_create_v1(token_2, [token_3])["dm_id"]
    dm_id3 = dm_create_v1(token_2, [token_1, token_3])["dm_id"]

    global message_id_1
    global message_id_2
    global message_id_3
    global message_id_4
    global message_id_5
    global message_id_6
    global message_id_7
    global message_id_8
    message_id_1 = message_send_v1(token_1, channel_id_1, "hello world")["message_id"]
    message_id_2 = message_send_v1(token_1, channel_id_1, "hello")["message_id"]
    message_id_3 = message_send_v1(token_2, channel_id_2, "hello world")["message_id"]
    message_id_4 = message_send_v1(token_3, channel_id_1, "hello world")["message_id"]
    message_id_5 = message_send_v1(token_3, channel_id_2, "hello world")["message_id"]
    message_id_6 = message_senddm_v1(token_1, dm_id1, "hello world")["message_id"]
    message_id_7 = message_senddm_v1(token_2, dm_id2, "hello world")["message_id"]
    message_id_8 = message_senddm_v1(token_2, dm_id3, "hello")["message_id"]


def test_message_length_too_long(initialize):
    with pytest.raises(InputError):
        message_edit_v1(token_1, message_id_1, "2GviF7jE64u10ZU0BmW8Vi8Mb7Y2nv9CbBYnuG4baoI2nClp8qhXKduGF2V1wW\
        q87TpldZFY9KvK3HwA1XovwbxqVxRtZnqxxM28CaHHNmFpaDsvbkZp3vLrODOFRYfxehP2so6ZIB8Ucdm7hEWcNCDVWm4ka7Vk8zO6\
        5VFzXu68Mod64AcD6z5pgiqrbA2VmM3ta2KUkZEdusDtdSKVuHxVEd31kWAR4KWe2KvCpOl6oMjpgBPvHJdnqjVkKfkcmOGte3M3Aq\
        S2T84DXCUH3VbPPCzhpC4yhekSQ6MtHikTpowT19epCaJjVGo8jEAy0jgNqtMyvIoZvpthPA6qYPd9YOVm6Hvo5aaLiC3tX0L7Y7P8\
        IVdCcSLSmt3wzV2YEo68CuYL1AD19Gxq7IZUpCwZ89JP0g38lSphRuMFUnQOoftxmI9wK98dwNMdKMmhgAYOx1UbZbHJPjY6cQqJew\
        lb9s6QzY1M9TxjiJ8sXnoTvTTQijKuI9Exesdmw89CDk7xi7KfyulFRJO6CPJ62uaOTAOptSP34R7Sdf8fgGrQVEXN98z5HO97RKmQ\
        FjTTnz92gFBFkrfP7189ysnMRioN6KqqEel98ZsjRLXSUWRQQlgPoM2rjnGekcksjeO8D1gcfymzcZcKgAjoXH3mdS6GAHzeFsER0O\
        tKzerX6n9plHXpmoTWsqN1OAN9XJefrovYJ1U47G04788kvTplAHeMIb1iiiVxObdV9jUEsHADEKEPryuOgKnE1MwWAibZRKUfK1wT\
        yDDfKqwfaRm2frMlMQTJUWGqHCB0h12mtJth3TIKwvX263T8iQPBN8U8H8COOxm5QdXsdjKKiivGKbqYz7l1OaWnc2oXhnMK7r43We\
        6M2b3s5BgnQpFtOlN8WzprqChD6GwPKq7gT12ikHsbpFcUFt7KLoNmb62v5DDZ4xUeERymUjFAIQhEve5GTQ0Zp0vi3yo7qQaQKvRU\
        tRmmQgNJtqWBPe8xicSeQ")
    
def test_message_id_invalid(initialize):
    with pytest.raises(InputError):
        message_edit_v1(token_1, message_id_3, "hi")
    with pytest.raises(InputError):
        message_edit_v1(token_1, 9, "hi")
    with pytest.raises(InputError):
        message_edit_v1(token_2, message_id_1, "hi")
    with pytest.raises(InputError):
        message_edit_v1(token_2, message_id_2, "hi")
    with pytest.raises(InputError):
        message_edit_v1(token_1, message_id_7, "hi")

def test_access_error(initialize):
    with pytest.raises(AccessError):
        message_edit_v1(token_3, message_id_1, "hi")
    with pytest.raises(AccessError):
        message_edit_v1(token_3, message_id_2, "hi")
    with pytest.raises(AccessError):
        message_edit_v1(token_3, message_id_3, "hi")
    with pytest.raises(AccessError):
        message_edit_v1(token_2, message_id_6, "hi")
    with pytest.raises(AccessError):
        message_edit_v1(token_3, message_id_7, "hi")
    with pytest.raises(AccessError):
        message_edit_v1(token_1, message_id_8, "hi")
    
def test_valid_edit(initialize):
    assert message_edit_v1(token_1, message_id_1, "hi1") == {}
    assert message_edit_v1(token_1, message_id_2, "hi2") == {}
    assert message_edit_v1(token_2, message_id_3, "hi3") == {}
    assert message_edit_v1(token_3, message_id_4, "hi4") == {}
    assert message_edit_v1(token_3, message_id_5, "hi5") == {}
    assert message_edit_v1(token_1, message_id_4, "hi6") == {}
    assert message_edit_v1(token_2, message_id_5, "hi7") == {}
    assert message_edit_v1(token_1, message_id_6, "hi8") == {}
    assert message_edit_v1(token_2, message_id_7, "hi9") == {}

def test_combine(initialize):
    message_edit_v1(token_1, message_id_1, "hi1") 
    
    store = data_store.get()
    channel_list = store["channels"]

    for channel in channel_list:
        for msg in channel["messages"]:
            if (msg["message_id"] == message_id_1):
                assert msg["message"] == "hi1"

    message_edit_v1(token_1, message_id_1, "")

    with pytest.raises(InputError):
        message_edit_v1(token_1, message_id_1, "hi1") 

    message_edit_v1(token_1, message_id_4, "testing")
    for channel in channel_list:
        for msg in channel["messages"]:
            if (msg["message_id"] == message_id_4):
                assert msg["message"] == "testing"

    message_edit_v1(token_3, message_id_5, "testing123")
    for channel in channel_list:
        for msg in channel["messages"]:
            if (msg["message_id"] == message_id_5):
                assert msg["message"] == "testing123"

def test_combine2(initialize):
    message_edit_v1(token_1, message_id_6, "hi1")

    store = data_store.get()
    dm_list = store["dms"]

    for dm in dm_list:
        for msg in dm["messages"]:
            if (msg["message_id"] == message_id_6):
                assert msg["message"] == "hi1"
    
    message_edit_v1(token_1, message_id_6, "")

    with pytest.raises(InputError):
        message_edit_v1(token_1, message_id_6, "hi1")

@pytest.fixture
def initialize2():
    clear_v1()
    global user_1
    global user_2
    global user_3
    user_1 = auth_register_v1("email1@gmail.com", "password", "name_first1", "name_last1")["auth_user_id"]
    user_2 = auth_register_v1("email2@gmail.com", "password", "name_first2", "name_last2")["auth_user_id"]
    user_3 = auth_register_v1("email3@gmail.com", "password", "name_first3", "name_last3")["auth_user_id"]
    global channel_1
    channel_1 = channels_create_v1(user_2, "channel2", True)['channel_id']
    channel_join_v1(user_1, channel_id_1)
    channel_join_v1(user_3, channel_id_1)

    global message_1
    global message_2
    global message_3

    message_1 = message_send_v1(user_1, channel_1, "hello world")["message_id"]
    message_2 = message_send_v1(user_2, channel_1, "hello")["message_id"]
    message_3 = message_send_v1(user_3, channel_1, "hello world")["message_id"]

    # user_1 is the global owner of the stream
    # channel_1 owner: user_2
    # channel_1 memeber: user_1, user_2, user_3

def test_global_owner_can_edit_members_message_channel(initialize2):
    assert message_edit_v1(user_1, message_1, "hi1") == {}
    assert message_edit_v1(user_1, message_2, "hi2") == {}
    assert message_edit_v1(user_1, message_3, "hi3") == {}

@pytest.fixture
def flask_initialize():
    requests.delete(config.url + 'clear/v1')
    
    r1 = requests.post(config.url + 'auth/register/v2', json={'email': 'email1@gmail.com', 'password': 'password', 'name_first': 'name_first1', 'name_last': 'name_last1'})
    r2 = requests.post(config.url + 'auth/register/v2', json={'email': 'email2@gmail.com', 'password': 'password', 'name_first': 'name_first2', 'name_last': 'name_last2'})
    r3 = requests.post(config.url + 'auth/register/v2', json={'email': 'email3@gmail.com', 'password': 'password', 'name_first': 'name_first3', 'name_last': 'name_last3'})
    r1_token = json.loads(r1.text)['token']
    r2_token = json.loads(r2.text)['token']
    r3_token = json.loads(r3.text)['token']

    requests.post(config.url + 'channels/create/v2', json={'token': r1_token, 'name': 'channel1', 'is_public': True})
    requests.post(config.url + 'channel/join/v2', json={'token': r3_token, 'channel_id': 1})
    requests.post(config.url + 'channels/create/v2', json={'token': r2_token, 'name': 'channel2', 'is_public': True})
    requests.post(config.url + 'channel/join/v2', json={'token': r3_token, 'channel_id': 2})

    requests.post(config.url + 'dm/create/v1', json={'token': r1_token, 'u_ids': [2, 3]})
    requests.post(config.url + 'dm/create/v1', json={'token': r2_token, 'u_ids': [3]})
    requests.post(config.url + 'dm/create/v1', json={'token': r2_token, 'u_ids': [1, 3]})

    requests.post(config.url + 'message/send/v1', json={'token': r1_token, 'channel_id': 1, 'message': "hello world"})
    requests.post(config.url + 'message/send/v1', json={'token': r1_token, 'channel_id': 1, 'message': "hello"})
    requests.post(config.url + 'message/send/v1', json={'token': r2_token, 'channel_id': 2, 'message': "hello world"})
    requests.post(config.url + 'message/send/v1', json={'token': r3_token, 'channel_id': 1, 'message': "hello world"})
    requests.post(config.url + 'message/send/v1', json={'token': r3_token, 'channel_id': 2, 'message': "hello world"})
    requests.post(config.url + 'message/senddm/v1', json={'token': r1_token, 'dm_id': 1, 'message': "hello world"})
    requests.post(config.url + 'message/senddm/v1', json={'token': r2_token, 'dm_id': 2, 'message': "hello world"})
    requests.post(config.url + 'message/senddm/v1', json={'token': r2_token, 'dm_id': 3, 'message': "hello world"})

    return [r1_token, r2_token, r3_token]

def test_flask_message_length_too_long(flask_initialize):
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[0], 'message_id': 1, 'message': "2GviF7jE64u10ZU\
            0BmW8Vi8Mb7Y2nv9CbBYnuG4baoI2nClp8qhXKduGF2V1wWtRmmQgNJtqWBPe8xicSeQ0vi3yo7qQaQKvRUFAIQhEve5GTQ0ZpERym\
            q87TpldZFY9KvK3HwA1XovwbxqVxRtZnqxxM28CaHHNmFpaDsvbkZp3vLrODOFRYfxehP2so6ZIB8Ucdm7hEWcNCDVWm4ka7Vk8zO6\
            5VFzXu68Mod64AcD6z5pgiqrbA2VmM3ta2KUkZEdusDtdSKVuHxVEd31kWAR4KWe2KvCpOl6oMjpgBPvHJdnqjVkKfkcmOGte3M3Aq\
            S2T84DXCUH3VbPPCzhpC4yhekSQ6MtHikTpowT19epCaJjVGo8jEAy0jgNqtMyvIoZvpthPA6qYPd9YOVm6Hvo5aaLiC3tX0L7Y7P8\
            IVdCcSLSmt3wzV2YEo68CuYL1AD19Gxq7IZUpCwZ89JP0g38lSphRuMFUnQOoftxmI9wK98dwNMdKMmhgAYOx1UbZbHJPjY6cQqJew\
            lb9s6QzY1M9TxjiJ8sXnoTvTTQijKuI9Exesdmw89CDk7xi7KfyulFRJO6CPJ62uaOTAOptSP34R7Sdf8fgGrQVEXN98z5HO97RKmQ\
            FjTTnz92gFBFkrfP7189ysnMRioN6KqqEel98ZsjRLXSUWRQQlgPoM2rjnGekcksjeO8D1gcfymzcZcKgAjoXH3mdS6GAHzeFsER0O\
            tKzerX6n9plHXpmoTWsqN1OAN9XJefrovYJ1U47G04788kvTplAHeMIb1iiiVxObdV9jUEsHADEKEPryuOgKnE1MwWAibZRKUfK1wT\
            yDDfKqwfaRm2frMlMQTJUWGqHCB0h12mtJth3TIKwvX263T8iQPBN8U8H8COOxm5QdXsdjKKiivGKbqYz7l1OaWnc2oXhnMK7r43We\
            6M2b3s5BgnQpFtOlN8WzprqChD6GwPKq7gT12ikHsbpFcUFt7KLoNmb62v5DDZ4xUe"})
    assert resp.status_code == 400

def test_flask_message_id_invalid(flask_initialize):
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[0], 'message_id': 3, 'message': "hi"})
    assert resp.status_code == 400
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[0], 'message_id': 9, 'message': "hi"})
    assert resp.status_code == 400
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[1], 'message_id': 1, 'message': "hi"})
    assert resp.status_code == 400
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[1], 'message_id': 2, 'message': "hi"})
    assert resp.status_code == 400
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[0], 'message_id': 7, 'message': "hi"})
    assert resp.status_code == 400

def test_flask_access_error(flask_initialize):
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[2], 'message_id': 1, 'message': "hi"})
    assert resp.status_code == 403
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[2], 'message_id': 2, 'message': "hi"})
    assert resp.status_code == 403
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[2], 'message_id': 3, 'message': "hi"})
    assert resp.status_code == 403
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[1], 'message_id': 6, 'message': "hi"})
    assert resp.status_code == 403
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[2], 'message_id': 7, 'message': "hi"})
    assert resp.status_code == 403
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[0], 'message_id': 8, 'message': "hi"})
    assert resp.status_code == 403

def test_flask_valid_edit(flask_initialize):
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[0], 'message_id': 1, 'message': "hi1"})
    assert resp.json() == {}
    assert resp.status_code == 200
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[0], 'message_id': 2, 'message': "hi2"})
    assert resp.json() == {}
    assert resp.status_code == 200
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[1], 'message_id': 3, 'message': "hi3"})
    assert resp.json() == {}
    assert resp.status_code == 200
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[2], 'message_id': 4, 'message': "hi4"})
    assert resp.json() == {}
    assert resp.status_code == 200
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[2], 'message_id': 5, 'message': "hi5"})
    assert resp.json() == {}
    assert resp.status_code == 200
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[0], 'message_id': 4, 'message': "hi6"})
    assert resp.json() == {}
    assert resp.status_code == 200
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[1], 'message_id': 5, 'message': "hi7"})
    assert resp.json() == {}
    assert resp.status_code == 200
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[0], 'message_id': 6, 'message': "hi8"})
    assert resp.json() == {}
    assert resp.status_code == 200
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[1], 'message_id': 7, 'message': "hi9"})
    assert resp.json() == {}
    assert resp.status_code == 200

def test_flask_remove(flask_initialize):
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[0], 'message_id': 4, 'message': ""})
    assert resp.json() == {}
    assert resp.status_code == 200
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[1], 'message_id': 5, 'message': ""})
    assert resp.json() == {}
    assert resp.status_code == 200
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[0], 'message_id': 6, 'message': ""})
    assert resp.json() == {}
    assert resp.status_code == 200
    resp = requests.put(config.url + 'message/edit/v1', json={'token': flask_initialize[1], 'message_id': 7, 'message': ""})
    assert resp.json() == {}
    assert resp.status_code == 200
