# Tests for dm_create_v1 function
# Written by Andy Wu z5363503

import pytest

from src.error import InputError, AccessError
from src.channels import channels_create_v1
from src.other import clear_v1
from src.auth import auth_register_v1
from src.dm import dm_create_v1

from src.data_store import data_store

# InputError when any of:
#     - Occurs when any u_id in u_ids does not refer to a valid user
# AccessError when any of:
#     - auth_user_id does not belong to any user's id

# Clears list of users, channels and dms, registers 3 new users
@pytest.fixture
def clear_and_register():
    clear_v1()
    auth_register_v1("hellothere@gmail.com", "thisismypassword", "Luke", "Skywalker")
    auth_register_v1("helloagain@gmail.com", "newpassword", "Han", "Solo")
    auth_register_v1("myemail@hotmail.com", "insanepassword", "Anakin", "Skywalker")

# Testing each member creating a dm with the other users
def test_simple(clear_and_register):
    assert dm_create_v1(1, [2,3])['dm_id'] == 1
    assert dm_create_v1(2, [1,3])['dm_id'] == 2
    assert dm_create_v1(3, [1,2])['dm_id'] == 3
    assert dm_create_v1(3, [1])['dm_id'] == 4

# Test creation of dm with a list of no ids
def test_one_member(clear_and_register):
    assert dm_create_v1(1, [])['dm_id'] == 1

# Test repeated creation of dms with a list of no ids
def test_one_member_repeat(clear_and_register):
    assert dm_create_v1(1, [])['dm_id'] == 1
    assert dm_create_v1(1, [])['dm_id'] == 2
    assert dm_create_v1(1, [])['dm_id'] == 3

# Raise InputError when a u_id in given list is invalid
def test_invalid_user(clear_and_register):
    with pytest.raises(InputError):
        assert dm_create_v1(1, [2,3,4])['dm_id']

# Raise InputError when all u_ids in given list is invalid
def test_all_invalid_user(clear_and_register):
    with pytest.raises(InputError):
        assert dm_create_v1(1, [4,5,6])['dm_id']

# # Raise AccessError when auth_user_id is invalid
# def test_invalid_auth_id(clear_and_register):
#     with pytest.raises(AccessError):
#         assert dm_create_v1(4, [1,2,3])['dm_id']

# Test repeated creations of same dms but each have unique id
def test_repeat_create(clear_and_register):
    assert dm_create_v1(1, [2,3])['dm_id'] == 1
    assert dm_create_v1(1, [2,3])['dm_id'] == 2
    assert dm_create_v1(1, [2,3])['dm_id'] == 3
    assert dm_create_v1(1, [2,3])['dm_id'] == 4

# Testing internal storage of dms is correct - not blackbox testing
def test_dm_storage(clear_and_register):
    assert dm_create_v1(1, [2,3])['dm_id'] == 1

    store = data_store.get()
    dms = store["dms"][0]

    assert dms['dm_id'] == 1
    assert dms['owner_id'] == 1
    assert dms['u_ids'] == [1,2,3]
    assert dms['name'] == "anakinskywalker, hansolo, lukeskywalker"
    assert dms['messages'] == []