import pytest
import requests

from src.other import clear_v1
from src.data_store import data_store
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.error import InputError
from src.error import AccessError
from src.channel import channel_join_v1
from src import config

def test_clear_successfully():  
    clear_v1()
    
    store = data_store.get()
    """
    key_user = store["users"]
    key_channel = store["channels"]

    # "users" in initial_object should be empty
    assert key_user == []
    # "channels" in initial object should be empty
    assert key_channel == []    
    """
    
    """
    for key in store:
        assert store[key] == []
    """
    
    assert store["users"] == []
    assert store["channels"] == []
    assert store["dms"] == []
    assert store["session_id"] == 0
    assert store["message_id"] == 0
    assert store["dm_id"] == 0
    
### Alex's Tests: ###

@pytest.fixture
def initialise():
    clear_v1()
    global initial_user_id_1 
    global initial_user_id_2
    global initial_user_id_3
    initial_user_id_1 = auth_register_v1("email1@gmail.com", "password", "name_first1", "name_last1")["auth_user_id"]
    initial_user_id_2 = auth_register_v1("email2@gmail.com", "password", "name_first2", "name_last2")["auth_user_id"]
    initial_user_id_3 = auth_register_v1("email3@gmail.com", "password", "name_first3", "name_last3")["auth_user_id"]
    global initial_channel_id_1
    global initial_channel_id_2
    global initial_channel_id_3
    initial_channel_id_1 = channels_create_v1(initial_user_id_1, "channel1", True)['channel_id']
    initial_channel_id_2 = channels_create_v1(initial_user_id_1, "channel2", True)['channel_id']
    initial_channel_id_3 = channels_create_v1(initial_user_id_1, "channel3", True)['channel_id']

def test_user_id_resets(initialise):
    clear_v1()
    new_user_id_1 = auth_register_v1("email4@gmail.com", "password", "newUser1", "lastname1")["auth_user_id"]
    new_user_id_2 = auth_register_v1("email5@gmail.com", "password", "newUser2", "lastname2")["auth_user_id"]
    new_user_id_3 = auth_register_v1("email6@gmail.com", "password", "newUser3", "lastname3")["auth_user_id"]
    
    assert new_user_id_1 == initial_user_id_1
    assert new_user_id_2 == initial_user_id_1 + 1
    assert new_user_id_3 == initial_user_id_1 + 2
    
def test_channel_id_resets(initialise):
    clear_v1()
    new_user_id = auth_register_v1("email4@gmail.com", "password", "newUser", "lastname")["auth_user_id"]
    new_channel_id_1 = channels_create_v1(new_user_id, "channel4", True)['channel_id']
    new_channel_id_2 = channels_create_v1(new_user_id, "channel5", True)['channel_id']
    new_channel_id_3 = channels_create_v1(new_user_id, "channel6", True)['channel_id']
    
    assert new_channel_id_1 == initial_channel_id_1
    assert new_channel_id_2 == initial_channel_id_1 + 1
    assert new_channel_id_3 == initial_channel_id_1 + 2

def test_access_removed():
    clear_v1()
    initial_user_id_1 = auth_register_v1("email1@gmail.com", "password", "name_first1", "name_last1")["auth_user_id"]
    initial_user_id_2 = auth_register_v1("email2@gmail.com", "password", "name_first2", "name_last1")["auth_user_id"]
    channels_create_v1(initial_user_id_2, "channel1", False)['channel_id']
    # user 2 is an owner of private channel 1, user 1 is also a global owner
    clear_v1()
    auth_register_v1("email1@gmail.com", "password", "name_first1", "name_last1")["auth_user_id"]
    user_id_2 = auth_register_v1("email2@gmail.com", "password", "name_first2", "name_last1")["auth_user_id"]
    channel_id_1 = channels_create_v1(initial_user_id_1, "channel1", False)['channel_id']
    # user 1 is an owner of private channel 1. user 1 is also a global owner
    with pytest.raises(AccessError):
        channel_join_v1(user_id_2, channel_id_1)

def test_return_value():
    return_value = clear_v1()
    assert return_value == {}

def test_initialised_correctly(): 
    clear_v1()
    store = data_store.get()
    assert store == {
        'users': [],
        'channels': [],
        'dms': [],
        "session_id": 0,
        "message_id": 0,
        "dm_id": 0
    }

def test_flask_clear_successfully():
    resp = requests.delete(config.url + "clear/v1")
    assert resp.status_code == 200
    assert resp.json() == {}
