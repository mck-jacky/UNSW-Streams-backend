import pytest

from src.auth import auth_register_v1
from src.auth import auth_login_v1
from src.other import clear_v1
from src.error import InputError


def test_login_wrong_password():
    """
    The test function tries to login a user, who entered a wrong password.
    """
    clear_v1()
    auth_register_v1('sample@gmail.au', 'password', 'Name', 'Name')
    with pytest.raises(InputError):
        auth_login_v1('sample@gmail.au', 'passwordo')

def test_login_without_account():
    """
    The test function tries to login a user, even though no account exists.
    """
    clear_v1()
    with pytest.raises(InputError):
        auth_login_v1('sample@gmail.au', 'password')

def test_login_with_other_users_password():
    """
    The test function tries to login a user, who uses the password of a
    different user.
    """
    clear_v1()
    auth_register_v1('sample@gmail.au', 'password', 'Name', 'Name')
    auth_register_v1('other@gmail.au', 'passwordo', 'Other', 'Other')
    with pytest.raises(InputError):
        auth_login_v1('sample@gmail.au', 'passwordo')

def test_login_without_password():
    """
    The test function tries to login a user, who did not enter a password.
    """
    clear_v1()
    auth_register_v1('sample@gmail.au', 'password', 'Name', 'Name')
    with pytest.raises(InputError):
        auth_login_v1('sample@gmail.au', '')

def test_login_without_email():
    """
    The test function tries to login a user, who did not enter his/her email.
    """
    clear_v1()
    auth_register_v1('sample@gmail.au', 'password', 'Name', 'Name')
    with pytest.raises(InputError):
        auth_login_v1('', 'password')





### The following functions assume that we know that we know that the user_id's
### of newly registered users start with 1 and increment. 

def test_valid_auth_login_input():
    """
    The test function logs in a user, who entered valid input.
    """
    clear_v1()
    auth_register_v1('sample@gmail.au', 'password', 'Name', 'Name')
    assert(auth_login_v1('sample@gmail.au', 'password')['auth_user_id'] == 1)

def test_valid_auth_login_with_two_consecutive_logins():
    """
    The same user logs in twice with the same valid input.
    """
    clear_v1()
    auth_register_v1('sample@gmail.au', 'password', 'Name', 'Name')
    assert(auth_login_v1('sample@gmail.au', 'password')['auth_user_id'] == 1)
    assert(auth_login_v1('sample@gmail.au', 'password')['auth_user_id'] == 1)

def test_valid_auth_login_with_two_logins_with_different_accounts():
    """
    The test function logs in two user consecutively.
    """
    clear_v1()
    auth_register_v1('sample@gmail.au', 'password', 'Name', 'Name')
    assert(auth_login_v1('sample@gmail.au', 'password')['auth_user_id'] == 1)
    auth_register_v1('other@gmail.au', 'passwordo', 'Other', 'Other')
    assert(auth_login_v1('other@gmail.au', 'passwordo')['auth_user_id'] == 2)

################################jacky's test######################################
def test_wrong_email():
    clear_v1()
    auth_register_v1('122@gmail.com', 'abcdef', 'namefirst', 'namelast')
    auth_register_v1('123@gmail.com', '123456', 'namefirst', 'namelast')
    auth_register_v1('testing@gmail.com', '123456', 'namefirst', 'namelast')
    with pytest.raises(InputError):
        auth_login_v1('122@gmail.com', '123456')
    with pytest.raises(InputError):
        auth_login_v1('123@gmailcom', 'abcdef')
    with pytest.raises(InputError):
        auth_login_v1('testing@gmail.com', '1234567')

def test_wrong_password():
    # tests in which we try to login with password that does not match
    # the account
    clear_v1()
    auth_register_v1('123@gmail.com', '123456', 'namefirst', 'namelast')
    auth_register_v1('testing@gmail.com', '1234567', 'namefirst', 'namelast')
    with pytest.raises(InputError):
        auth_login_v1('123@gmail.com', '12345')
    with pytest.raises(InputError):  
        auth_login_v1('123@gmail.com', '1234567')
    with pytest.raises(InputError):  
        auth_login_v1('testing@gmail.com', '123456')
