import pytest

from src.error import AccessError, InputError
from src.other import clear_v1
from src.auth import auth_register_v1
from src.message import message_senddm_v1
from src.data_store import data_store
from src.dm import dm_create_v1
from src.other import check_if_member_of_dm, check_if_valid_dm
import requests
import json
from src import config


"""
InputError when any of:

    - dm_id does not refer to a valid DM
    - length of message is less than 1 or over 1000 characters

AccessError when any of:

    - dm_id is valid and the authorised user is not a member of the DM
"""

@pytest.fixture
def initialize():
    clear_v1()
    global user_id1
    global user_id2
    global user_id3
    user_id1 = auth_register_v1("email1@gmail.com", "password", "name_first1", "name_last1")["auth_user_id"]
    user_id2 = auth_register_v1("email2@gmail.com", "password", "name_first2", "name_last2")["auth_user_id"]
    user_id3 = auth_register_v1("email3@gmail.com", "password", "name_first3", "name_last3")["auth_user_id"]
    
    global dm_id1
    global dm_id2
    dm_id1 = dm_create_v1(user_id1, [user_id2])["dm_id"]
    dm_id2 = dm_create_v1(user_id2, [user_id3])["dm_id"]

def test_message_too_long_or_short(initialize):
    with pytest.raises(InputError):
        # length of message is less than 1 
        message_senddm_v1(user_id1, dm_id1, "")
    with pytest.raises(InputError):
        # length of message is more than 1000 
        message_senddm_v1(user_id1, dm_id1, "pVcDHXx5cWLdQNIcqdo6thKpLHpC4fY9QPlAbSLIMOlC5yYdTQnYqzG1EZMYiBNV\
        einVz8U51XZ42ZlG6pkcsAdEL7WOokrIoWhNarfFvIahP29jvsEMmRPKSxTXScwB8884mOBQEJzFCWeN7odA7oKa3EXPQR8WVMzdZ\
        s1Qn2OX8LDVsFFnRgIyQNtcUsVkxc2jLgfjALoXaX7s9eDpgt4nIrUVOBPDuzYEa6vhUC9NzQ8zmqiYZv3ksqLgdIHJ3ziMGdLR9s\
        CmUdgPiQBSSPwCwVkAcfadve4lIf63kx90YkkljU7Gd22V2iHOlZVI4GHgbYRLb3eRiqosExee6k6giiDIYDEYlS52tnC0TLAy1v2\
        AtmZ3JBrTxPzUX1c2nUaSYYsihGDTuN3z1qorQTF5C9CqsSOBjKSkFQPzq9VwLJQ9yd03NGwNjcaYotA8SxVRW7WhnIENFb1n3gkG\
        ikaIzKfRueF9sySomZD6HPaYVBx6gsQtia5liGnh0SUoGa2VLnP0IaNllzKjlYzAZWiv4DHbkRtzcc0BIOhta9S3ohaAtFtp3V0gv\
        YW9Gf6uILJ7FWBbjChjMDLJIA4rh9ZoyaAb6XcrjnspvVTnvx815PGeiO8v7j7Az9I3HpDwgQrcWsLbpGPGHb0r7kVE7KW21p4aPm\
        94j7JmDGYS4B3oU9rIQ9XspOPowwHjfQepRxTK7swJt7uSLs1Ge2g5KP7q3Ho6AgfQk4oEStNvjzUqnGrHb9c83OyaVNfBUbG0i4J\
        vJRkIjscmAnrdyJMx4BCjKFZaDM7evoel6hLaNmzhcdpTLBq8iVZdsEVkOOhNtIumhOolQ12AgigRiNG9WYMwBNNpLgeAUtYwS3p0\
        IT5TjHoJ1ks6wZDDGgKOHoZglxa4BzAVawvkJa8RIhttTnRnThYOagzaDaI3IlFMbvE7HN2cT757EInfY3dPzGJU60rwnsKLSfzah\
        DPXzfhNS85ylgFQ1eW3GKwKMT9y8")

def test_invalid_dm_id(initialize):
    with pytest.raises(InputError):
        message_senddm_v1(user_id1, 3, "hi")
    with pytest.raises(InputError):
        message_senddm_v1(user_id2, 3, "hi")

def test_not_memeber_of_dm(initialize):
    with pytest.raises(AccessError):
        message_senddm_v1(user_id1, dm_id2, "hi")
    with pytest.raises(AccessError):
        message_senddm_v1(user_id3, dm_id1, "hi")   

def test_valid_message(initialize):
    assert message_senddm_v1(user_id1, dm_id1, "hi")["message_id"] == 1
    assert message_senddm_v1(user_id2, dm_id1, "hi")["message_id"] == 2
    assert message_senddm_v1(user_id2, dm_id2, "hi")["message_id"] == 3
    assert message_senddm_v1(user_id3, dm_id2, "hi")["message_id"] == 4

@pytest.fixture
def flask_initialize():
    requests.delete(config.url + 'clear/v1')

    r1 = requests.post(config.url + 'auth/register/v2', json={'email': 'email1@gmail.com', 'password': 'password', 'name_first': 'name_first1', 'name_last': 'name_last1'})
    r2 = requests.post(config.url + 'auth/register/v2', json={'email': 'email2@gmail.com', 'password': 'password', 'name_first': 'name_first2', 'name_last': 'name_last2'})
    r3 = requests.post(config.url + 'auth/register/v2', json={'email': 'email3@gmail.com', 'password': 'password', 'name_first': 'name_first3', 'name_last': 'name_last3'})
    r1_token = json.loads(r1.text)['token']
    r2_token = json.loads(r2.text)['token']
    r3_token = json.loads(r3.text)['token']

    requests.post(config.url + 'dm/create/v1', json={'token': r1_token, 'u_ids': [2]})
    requests.post(config.url + 'dm/create/v1', json={'token': r2_token, 'u_ids': [3]})

    return [r1_token, r2_token, r3_token]

def test_flask_message_too_long_or_short(flask_initialize):
    resp = requests.post(config.url + 'message/senddm/v1', json={'token': flask_initialize[0], 'dm_id': 1, 'message': ""})
    assert resp.status_code == 400
    resp = requests.post(config.url + 'message/senddm/v1', json={'token': flask_initialize[0], 'dm_id': 1, 'message': "p\
        einVz8U51XZ42ZlG6pkcsAdEL7WOokrIoWhNarfFvIahP29jvsEMmRPKSxTXScwB8884mOBQEJzFCWeN7odA7oKa3EXPQR8WVMzdZ\
        s1Qn2OX8LDVsFFnRgIyQNtcUsVkxc2jLgfjALoXaX7s9eDpgt4nIrUVOBPDuzYEa6vhUC9NzQ8zmqiYZv3ksqLgdIHJ3ziMGdLR9s\
        CmUdgPiQBSSPwCwVkAcfadve4lIf63kx90YkkljU7Gd22V2iHOlZVI4GHgbYRLb3eRiqosExee6k6giiDIYDEYlS52tnC0TLAy1v2\
        AtmZ3JBrTxPzUX1c2nUaSYYsihGDTuN3z1qorQTF5C9CqsSOBjKSkFQPzq9VwLJQ9yd03NGwNjcaYotA8SxVRW7WhnIENFb1n3gkG\
        ikaIzKfRueF9sySomZD6HPaYVBx6gsQtia5liGnh0SUoGa2VLnP0IaNllzKjlYzAZWiv4DHbkRtzcc0BIOhta9S3ohaAtFtp3V0gv\
        YW9Gf6uILJ7FWBbjChjMDLJIA4rh9ZoyaAb6XcrjnspvVTnvx815PGeiO8v7j7Az9I3HpDwgQrcWsLbpGPGHb0r7kVE7KW21p4aPm\
        94j7JmDGYS4B3oU9rIQ9XspOPowwHjfQepRxTK7swJt7uSLs1Ge2g5KP7q3Ho6AgfQk4oEStNvjzUqnGrHb9c83OyaVNfBUbG0i4J\
        vJRkIjscmAnrdyJMx4BCjKFZaDM7evoel6hLaNmzhcdpTLBq8iVZdsEVkOOhNtIumhOolQ12AgigRiNG9WYMwBNNpLgeAUtYwS3p0\
        IT5TjHoJ1ks6wZDDGgKOHoZglxa4BzAVawvkJa8RIhttTnRnThYOagzaDaI3IlFMbvE7HN2cT757EInfY3dPzGJU60rwnsKLSfzah\
        DPXzfhNS85ylgFQ1eW3GKwKMT9y8VcDHXx5cWLdQNIcqdo6thKpLHpC4fY9QPlAbSLIMOlC5yYdTQnYqzG1EZMYiBNV"})
    assert resp.status_code == 400

def test_flask_invalid_dm_id(flask_initialize):
    resp = requests.post(config.url + 'message/senddm/v1', json={'token': flask_initialize[0], 'dm_id': 3, 'message': "hi"})
    assert resp.status_code == 400
    resp = requests.post(config.url + 'message/senddm/v1', json={'token': flask_initialize[1], 'dm_id': 3, 'message': "hi"})
    assert resp.status_code == 400

def test_flask_not_memeber_of_dm(flask_initialize):
    resp = requests.post(config.url + 'message/senddm/v1', json={'token': flask_initialize[0], 'dm_id': 2, 'message': "hi"})
    assert resp.status_code == 403
    resp = requests.post(config.url + 'message/senddm/v1', json={'token': flask_initialize[2], 'dm_id': 1, 'message': "hi"})
    assert resp.status_code == 403

def test_flask_valid_message(flask_initialize):
    resp = requests.post(config.url + 'message/senddm/v1', json={'token': flask_initialize[0], 'dm_id': 1, 'message': "hi"})
    assert resp.json() == {"message_id": 1}
    assert resp.status_code == 200
    resp = requests.post(config.url + 'message/senddm/v1', json={'token': flask_initialize[1], 'dm_id': 1, 'message': "hi"})
    assert resp.json() == {"message_id": 2}
    assert resp.status_code == 200
    resp = requests.post(config.url + 'message/senddm/v1', json={'token': flask_initialize[1], 'dm_id': 2, 'message': "hi"})
    assert resp.json() == {"message_id": 3}
    assert resp.status_code == 200
    resp = requests.post(config.url + 'message/senddm/v1', json={'token': flask_initialize[2], 'dm_id': 2, 'message': "hi"})
    assert resp.json() == {"message_id": 4}
    assert resp.status_code == 200
