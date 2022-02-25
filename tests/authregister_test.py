import pytest

from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import InputError
from src.data_store import data_store


def test_auth_register_invalid_email():
    """
    The test function uses an email address without '@'.
    """
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('aaa', 'password', 'Name', 'Name')

def test_auth_register_other_invalid_email():
    """
    The test function uses an email address without domain '.ending'.
    """
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('sample@gmail', 'password', 'Name', 'Name')

def test_auth_register_another_invalid_email():
    """
    The test function uses an email address without domain 'ending'.
    """
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('sample@gmail.', 'password', 'Name', 'Name')

def test_register_duplicate_email():
    """
    The test function tries to register a second user with an already used 
    email address.
    """
    clear_v1()
    auth_register_v1('sample@gmail.au', 'password', 'Name', 'Name')
    with pytest.raises(InputError):
        auth_register_v1('sample@gmail.au', 'password', 'Other', 'Other')

def test_too_short_password():
    """
    The test function uses a password, which is only 5 chars long.
    """
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('sample@gmail.au', 'passw', 'Name', 'Name')

def test_too_long_name():
    """
    The test function uses a family name that is too long.
    """
    clear_v1()
    with pytest.raises(InputError):                             # these are exactly 51 chars
        auth_register_v1('sample@gmail.au', 'password', 'Name', 'Namenamenamenamenamenamenamenamenamenamenamenamenam') 

def test_no_first_name_given():
    """
    The test function uses an empty string for the first name.
    """
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('sample@gmail.au', 'password', '', 'Name')

def test_no_family_name_given():
    """
    The test function uses an empty string for the last name.
    """
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('sample@gmail.au', 'password', 'Name', '')

def test_check_if_name_handle_is_formed_correctly():
    clear_v1()
    
    auth_register_v1('sample@gmail.au', 'password', 'Name', 'Name')
    auth_register_v1('saple@gmail.au', 'password', 'Name', 'Name')
    auth_register_v1('samle@gmail.au', 'password', 'Name', 'Name')
    auth_register_v1('sampl@gmail.au', 'password', 'Name', 'Name')
    
    for user in data_store.get()['users']:
        if user['auth_user_id'] == 1:
            print(data_store.get()['users'])
            assert user['name_handle'] == "namename"
            assert user ['auth_user_id'] == 1
        if user['auth_user_id'] == 2:
            assert user['name_handle'] == "namename0"
            assert user ['auth_user_id'] == 2
        if user['auth_user_id'] == 3:
            assert user ['auth_user_id'] == 3
            assert user['name_handle'] == "namename1"
        if user['auth_user_id'] == 4:
            assert user ['auth_user_id'] == 4
            assert user['name_handle'] == "namename2"



### The following functions assume that we know that we know that the user_id's
### of newly registered users start with 1 and increment. 

def test_valid_auth_register_input():
    """
    Test function uses valid input to register 2 users.
    """
    clear_v1()
    assert(auth_register_v1('sample@gmail.au', 'password', 'Name', 'Name')['auth_user_id'] == 1)
    assert(auth_register_v1('other@gmail.au', 'password', 'Other', 'Other')['auth_user_id'] == 2)

def test_valid_auth_register_inputs_with_ints():
    """
    Test function uses valid input to register a user.
    The input is mostly composed of numbers.
    """
    clear_v1()
    assert(auth_register_v1('1111111@1.au', '123456', '123', '123')['auth_user_id'] == 1)



################################jacky's test######################################

def test_already_used():
    # test that tests registering with the same email address multiple times
    clear_v1()
    auth_register_v1("testing@gmail.com", "password", "namefirst", "namelast")
    with pytest.raises(InputError):
        auth_register_v1("testing@gmail.com", "123456", "namefirst", "namelast")
    
def test_valid_register():
    # tests with valid input
    clear_v1()
    assert(auth_register_v1('123@gmail.com', '123456', 'namefirst', 'namelast')['auth_user_id'] == 1)
    assert(auth_register_v1('testing@gmail.com', 'a12345', 'CcRJtKV5f2jcfws4lkgtf4xnZK0hCB8htUoPMnQpEwdM2PIkiO', 'O')['auth_user_id'] == 2)
    assert(auth_register_v1('123@gmail.hk', 'password', 'x', 'CcRJtKV5f2jcfws4lkgtf4xnZK0hCB8htUoPMnQpEwdM2PIkiO')['auth_user_id'] == 3)
    assert(auth_register_v1('testing@gmail.au', 'password', 'SJPrvRVbL1EJkc587HyEV69gLZFOW4dJi1a47Jgxz4W2EiBFsU', 'SJPrvRVbL1EJkc587HyEV69gLZFOW4dJi1a47Jgxz4W2EiBFsU')['auth_user_id'] == 4)
    assert(auth_register_v1('testing@gmail.org', 'password', 'S', 'U')['auth_user_id'] == 5)    

