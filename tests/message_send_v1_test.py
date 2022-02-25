import pytest

from src.error import AccessError, InputError
from src.other import clear_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.message import message_send_v1
from src.data_store import data_store
import requests
import json
from src import config

"""
InputError when any of:
      
    - channel_id does not refer to a valid channel
    - length of message is less than 1 or over 1000 characters
      
AccessError when:
      
    - channel_id is valid and the authorised user is not a member of the channel
"""

@pytest.fixture
def initialize():
    clear_v1()
    global token_1
    global token_2
    token_1 = auth_register_v1("email1@gmail.com", "password", "name_first1", "name_last1")["auth_user_id"]
    token_2 = auth_register_v1("email2@gmail.com", "password", "name_first2", "name_last2")["auth_user_id"]
    global channel_id_1
    global channel_id_2
    channel_id_1 = channels_create_v1(token_1, "channel1", True)['channel_id']
    channel_id_2 = channels_create_v1(token_2, "channel2", True)['channel_id']

def test_channel_id_invalid(initialize):
    with pytest.raises(InputError):
        message_send_v1(token_1, 213, "World hello")
    with pytest.raises(InputError):
        message_send_v1(token_2, 5, "Testing")

def test_message_length_error(initialize):
    with pytest.raises(InputError):
        # length of message is less than 1
        message_send_v1(token_1, channel_id_1, "")
    with pytest.raises(InputError):
        # length of message is more than 1000
        message_send_v1(token_1, channel_id_1, "ZfWaKanXxwXhI9imo8QM4L0PN70h28UoLAvn1i785WMPcxerv5PQyMj \
        nAJqT00w8oTLb1CR9rs4n2PFciR8sdqOVn0QoduOgcLS4KLfVw4FkUEI2x5Pno7eviriPp9L7kqWJARpiIDK6OP85QImrmoi \
        699OIsb1bGDLPjMlIHFsoFCQaf8jRyIipBb4eckL5o5KhZJ4uNH3cMTkHVB11c0g3ntKUNczsY3jK1QrVaSCNzF8l2YU7x6zyC \
        9ATv164cETPPjOdYqDPq1n9q9jBMUosy0V9QpW65VhHEtYfuk6wvYAA5ewEgUVMwp4P2fxfqTJYD2lYBUQRjgcWcjIPT4hcW1kV \
        sENc66oumOe7kJQj3frLLjHkK4xHr6AhoA7glTjU44S9mdfiBN6MzscMwjfH7sdAgzCDfGCQ7GlCtF96BOtMhwXLgufenoJF8gJ \
        0W3nt52e9ckFdP8Veq1lvtQkzuOTmaMmKTjtVhWjkaHrFGupGkzmgibvZUBfCR1M0FApYAef11IgvsBRQ1mSVl5vOv9dP5BGvsSA \
        frqPE6xF6yBr0KnBWQ2y0tvdXebW4zKoLgj55R7gjcsJ06PBj9g7WO2EVSkRj3Iw8IKH2REA7VG5iykCziZLufgCcfABEtJXXlfSA \
        C9Avvv6mtD3ygKdOx5jIBhZNoUwcqyTfMRRJV8J7BNq8U8RK4LCZyf9b4sTaKLWQlBsc8rixEqeUZP7eQUZlxb8aWHXckcArOrzm \
        PbGx0oM3rOiShwYWj0qGUZNGafE7cykW14DmszJl9iyZiYZn UmdeCbd3ipKfXfIDF80nRMU7jTfTBHHAkQl6yGfnTqM7eFWmWsUoO \
        mjAMOaOOwzbSEGINj7rmBFgpvNPOKFM4cYIYsA2jbp8kg3FcC7rTWt4ZBEoMFnZ9guncbPgXoLYIwuJLnoqLFo6TNTZm0dAmrl5F5 \
        gyRDI2CindCBTlRyA5ZtIjkJatL1nsH8DVoZ8Hg0tIYDyVFvxj")
    

def test_user_not_member(initialize):
    with pytest.raises(AccessError):
        message_send_v1(token_2, channel_id_1, "this is a test message")
    with pytest.raises(AccessError):
        message_send_v1(token_1, channel_id_2, "hello world")

def test_both_error(initialize):
    with pytest.raises(AccessError):
        message_send_v1(token_2, channel_id_1, "")
    with pytest.raises(AccessError):
        message_send_v1(token_1, channel_id_2, "SlF419AcWyrcb4g0kcCamQdBd0dC3Jo4usw3N7c7MY83VmyqbsMVXNkUdqh6bjm \
        SncIVtRqc0HQoDheXdxF0Q1FsMxF0eE1aEPyAnwTGH3EuYyPyp7tJ5xqF7TpQGq9yczXdnI2JH1MqDTIwobzbRWlnAQDwWfMEBQdJ3oc \
        7Z90hY1azs9IKedz9YSC3eUpax4XEKnhCNI7Do7MfDt7s86Bgiws5FRdwihJ259RfmWNLMBspX5YKQtvKIRw8cDuD4EhcudIgGZz7Qx \
        ljFc6GAnuQ46aXDuo7JlVj5HVyrS4Y6nKvkMhUFlqJvSaNkktx1B0JMb4fsEZ61CObfXVuJC7c5sAMdT3BUQkmGyRh1B5MJLrPeWmfXV \
        p9OJAdbbgnQJTIRjVYHbyiG5Nc9L8Xd1yKtb4VyEHWJEsNDEJTenbApFvbmQcHbvdEB6y8odNKGDm1UNSPDkISrhXNa13YDyAG2pbmJ0 \
        bfhNlluVx9poiBzn9ZjttkZ9BOzyTAjW8uScDJyjKbYTOqblEd7zv8ql4m3Ak0AB6MGW5WHTUZbEX7uj72t8iEbkJRmOsAsZkQY2jeK4 \
        9fQzailntvOOyDzljI5Kp4EtzFuqwfcNZYKj3WUy3sIHbmB8qjAiO43sYG9GsbjIOeHw8P4ENavKRDjHEuLEaug1GRWuBL8RuKZaSxOn \
        nef0nk48WZw1TS1V6etUTLznfQL981xaCXDqbuHWBul3IXzoeetlREwtM3l6M7TCkIvi5FJBHJtx6bKBX1Ahl1GEeFaRbTycqsxInGFNI \
        m1txJNKKttTWc1AZMWtWNAWWFbGmsOc0ysaHCUPWhnsS8ffOSSCPg6BeLLcw7OHg2GRJkqVdDxJrcgXufUo1O2irJu7HCNRkZQ2QmosS \
        eHOC1qTBTB3cUklyIcTRn8oH921iaASujcAU8kVstGonJTnsgb6ZAGo6ouXwcwHDDSMTlyWTEry9SgVgrItWEtZGYAZTu8MyiIu6zcec \
        3ui")

def test_valid_return_id(initialize):
    assert message_send_v1(token_1, channel_id_1, "Hello world")["message_id"] == 1
    assert message_send_v1(token_1, channel_id_1, "3Aom4SYU0Z")["message_id"] == 2
    assert message_send_v1(token_1, channel_id_1, "ropmispdfpnt")["message_id"] == 3
    assert message_send_v1(token_2, channel_id_2, "WAPCHWWDFPUD")["message_id"] == 4
    assert message_send_v1(token_2, channel_id_2, "SBNQRBnfacKtIukceONJFa")["message_id"] == 5
    assert message_send_v1(token_2, channel_id_2, "O")["message_id"] == 6
    assert message_send_v1(token_2, channel_id_2, "3ZMJo8OZ7t8p75d1MJzUQSRvxSYTlnapiB8C0ts5LWzKjS6P0Kf11mpLl3Wr3l\
    GyxdiN3IGTjAyS69YmRzMdS8mARZfZPQuNo3P3hyyMmlYniDbACILpzOGCxNR4jf0VzFnamyXnm7scO6qbJTYS3EdIpVIy9X2xdXjyUVptDhY\
    XzgwcUl1UcIY6gQ5pm8EGNDp34ZzqpB4jIN0OaUYAfBSMa1OHnmPzNCEzWM9RPqezcDUn5BH0gz5XAZqX7pm0oHxZzfIifRQrAUOJYPEXY9S6\
    TkiUuVzpMTu8Yuf40k9m4A28fQbkEnAu5DJAh5KEGoFV6azElm7gRVRjBbaFTxsfhPLAwfXeJrij1XxnABRxku66xGbSR0kZNt69spebWLu2y\
    7klRJfiAdG5AYtXcg3ezX35sUbiznVGcCIJT84FoBulHkZQg9LAOtncTVPjmc3mvHkxabKEDncYtOJLVFAZvG2FnPgNqrJAzcUhpyXHQVQXaB\
    ykYdz6pDWdbvJz5Zyl7CPNLgrmxPoHE7SYaIcAWoMkDQ8vmPV4IREnH8UPkx9LnRYf6tGizEe9L6D2ot3lpnBpivBSnfv1mh86cGUPsOoSeY4\
    zxbBPWovYiS8q3ZGu0LSADYFvS1XPyO8UFhE6NDr3QBhfUrCVxK7wOM3nUzp8vc2clDBTTxntlHAWpbertj8FG8NIaKoNh8xI2dHBd2B1pOJz\
    lc9zQF4vfsgGBjMK4DjzLXEegbW2kCuSeSunqNBh1s4196nBzj1ZQJfcugDwmJMVw2MObTj83kaQ5V9ap1Ln7kvaxs9NfCHPpg4dBmrSKYSb8\
    CICPi767aDlBjJOxV7G8i4X66BShVceCxBREz2PauNc3srUsFZsjYZCFhvt23oYKIPWO5lrUWQ63gedyKzKDng1FQ4stt4x4W0zvGGbx5Laef\
    9qyYpZUYIoxLJH3S")["message_id"] == 7 

def test_valid_sent(initialize):
    message_send_v1(token_1, channel_id_1, "hello world")
    message_send_v1(token_1, channel_id_1, "3Aom4SYU0Z")

    store = data_store.get()
    channel_list = store["channels"]

    for channel in channel_list:
        if channel["channel_id"] == channel_id_1:
            assert channel["messages"][0]["message"] == "3Aom4SYU0Z"
            assert channel["messages"][0]["message_id"] == 2
            assert channel["messages"][0]["u_id"] == token_1
            assert channel["messages"][1]["message"] == "hello world"
            assert channel["messages"][1]["message_id"] == 1
            assert channel["messages"][1]["u_id"] == token_1

    message_send_v1(token_2, channel_id_2, "hello world")
    message_send_v1(token_2, channel_id_2, "world hello")

    for channel in channel_list:
        if channel["channel_id"] == channel_id_2:
            assert channel["messages"][0]["message"] == "world hello"
            assert channel["messages"][0]["message_id"] == 4
            assert channel["messages"][0]["u_id"] == token_2
            assert channel["messages"][1]["message"] == "hello world"
            assert channel["messages"][1]["message_id"] == 3
            assert channel["messages"][1]["u_id"] == token_2

@pytest.fixture
def flask_initialize():
    requests.delete(config.url + 'clear/v1')
    
    r1 = requests.post(config.url + 'auth/register/v2', json={'email': 'email1@gmail.com', 'password': 'password', 'name_first': 'name_first1', 'name_last': 'name_last1'})
    r2 = requests.post(config.url + 'auth/register/v2', json={'email': 'email2@gmail.com', 'password': 'password', 'name_first': 'name_first2', 'name_last': 'name_last2'})
    r1_token = json.loads(r1.text)['token']
    r2_token = json.loads(r2.text)['token']

    requests.post(config.url + 'channels/create/v2', json={'token': r1_token, 'name': 'channel1', 'is_public': True})
    requests.post(config.url + 'channels/create/v2', json={'token': r2_token, 'name': 'channel2', 'is_public': True})

    return [r1_token, r2_token]

def test_flask_channel_id_invalid(flask_initialize):
    resp = requests.post(config.url + 'message/send/v1', json={'token': flask_initialize[0], 'channel_id': 213, 'message': "World Hello"})
    assert resp.status_code == 400
    resp = requests.post(config.url + 'message/send/v1', json={'token': flask_initialize[1], 'channel_id': 5, 'message': "testing"})
    assert resp.status_code == 400

def test_flask_message_length_error(flask_initialize):
    resp = requests.post(config.url + 'message/send/v1', json={'token': flask_initialize[0], 'channel_id': 1, 'message': ""})
    assert resp.status_code == 400
    resp = requests.post(config.url + 'message/send/v1', json={'token': flask_initialize[0], 'channel_id': 1, 
    'message': "ZfWaKanXxwXhI9imo8QM4L0PN70h28UoLAvn1i785WMPcxerv5PQyMj \
    nAJqT00w8oTLb1CR9rs4n2PFciR8sdqOVn0QoduOgcLS4KLfVw4FkUEI2x5Pno7eviriPp9L7kqWJARpiIDK6OP85QImrmoi \
    699OIsb1bGDLPjMlIHFsoFCQaf8jRyIipBb4eckL5o5KhZJ4uNH3cMTkHVB11c0g3ntKUNczsY3jK1QrVaSCNzF8l2YU7x6zyC \
    9ATv164cETPPjOdYqDPq1n9q9jBMUosy0V9QpW65VhHEtYfuk6wvYAA5ewEgUVMwp4P2fxfqTJYD2lYBUQRjgcWcjIPT4hcW1kV \
    sENc66oumOe7kJQj3frLLjHkK4xHr6AhoA7glTjU44S9mdfiBN6MzscMwjfH7sdAgzCDfGCQ7GlCtF96BOtMhwXLgufenoJF8gJ \
    0W3nt52e9ckFdP8Veq1lvtQkzuOTmaMmKTjtVhWjkaHrFGupGkzmgibvZUBfCR1M0FApYAef11IgvsBRQ1mSVl5vOv9dP5BGvsSA \
    frqPE6xF6yBr0KnBWQ2y0tvdXebW4zKoLgj55R7gjcsJ06PBj9g7WO2EVSkRj3Iw8IKH2REA7VG5iykCziZLufgCcfABEtJXXlfSA \
    C9Avvv6mtD3ygKdOx5jIBhZNoUwcqyTfMRRJV8J7BNq8U8RK4LCZyf9b4sTaKLWQlBsc8rixEqeUZP7eQUZlxb8aWHXckcArOrzm \
    PbGx0oM3rOiShwYWj0qGUZNGafE7cykW14DmszJl9iyZiYZn UmdeCbd3ipKfXfIDF80nRMU7jTfTBHHAkQl6yGfnTqM7eFWmWsUoO \
    mjAMOaOOwzbSEGINj7rmBFgpvNPOKFM4cYIYsA2jbp8kg3FcC7rTWt4ZBEoMFnZ9guncbPgXoLYIwuJLnoqLFo6TNTZm0dAmrl5F5 \
    gyRDI2CindCBTlRyA5ZtIjkJatL1nsH8DVoZ8Hg0tIYDyVFvxj"})
    assert resp.status_code == 400

def test_flask_user_not_member(flask_initialize):
    resp = requests.post(config.url + 'message/send/v1', json={'token': flask_initialize[1], 'channel_id': 1, 'message': "testing"})
    assert resp.status_code == 403
    resp = requests.post(config.url + 'message/send/v1', json={'token': flask_initialize[0], 'channel_id': 2, 'message': "testing"})
    assert resp.status_code == 403

def test_flask_both_error(flask_initialize):
    resp = requests.post(config.url + 'message/send/v1', json={'token': flask_initialize[1], 'channel_id': 1, 'message': ""})
    assert resp.status_code == 403
    resp = requests.post(config.url + 'message/send/v1', json={'token': flask_initialize[0], 'channel_id': 2, 
    'message': "SlF419AcWyrcb4g0kcCamQdBd0dC3Jo4usw3N7c7MY83VmyqbsMVXNkUdqh6bjm \
    SncIVtRqc0HQoDheXdxF0Q1FsMxF0eE1aEPyAnwTGH3EuYyPyp7tJ5xqF7TpQGq9yczXdnI2JH1MqDTIwobzbRWlnAQDwWfMEBQdJ3oc \
    7Z90hY1azs9IKedz9YSC3eUpax4XEKnhCNI7Do7MfDt7s86Bgiws5FRdwihJ259RfmWNLMBspX5YKQtvKIRw8cDuD4EhcudIgGZz7Qx \
    ljFc6GAnuQ46aXDuo7JlVj5HVyrS4Y6nKvkMhUFlqJvSaNkktx1B0JMb4fsEZ61CObfXVuJC7c5sAMdT3BUQkmGyRh1B5MJLrPeWmfXV \
    p9OJAdbbgnQJTIRjVYHbyiG5Nc9L8Xd1yKtb4VyEHWJEsNDEJTenbApFvbmQcHbvdEB6y8odNKGDm1UNSPDkISrhXNa13YDyAG2pbmJ0 \
    bfhNlluVx9poiBzn9ZjttkZ9BOzyTAjW8uScDJyjKbYTOqblEd7zv8ql4m3Ak0AB6MGW5WHTUZbEX7uj72t8iEbkJRmOsAsZkQY2jeK4 \
    9fQzailntvOOyDzljI5Kp4EtzFuqwfcNZYKj3WUy3sIHbmB8qjAiO43sYG9GsbjIOeHw8P4ENavKRDjHEuLEaug1GRWuBL8RuKZaSxOn \
    nef0nk48WZw1TS1V6etUTLznfQL981xaCXDqbuHWBul3IXzoeetlREwtM3l6M7TCkIvi5FJBHJtx6bKBX1Ahl1GEeFaRbTycqsxInGFNI \
    m1txJNKKttTWc1AZMWtWNAWWFbGmsOc0ysaHCUPWhnsS8ffOSSCPg6BeLLcw7OHg2GRJkqVdDxJrcgXufUo1O2irJu7HCNRkZQ2QmosS \
    eHOC1qTBTB3cUklyIcTRn8oH921iaASujcAU8kVstGonJTnsgb6ZAGo6ouXwcwHDDSMTlyWTEry9SgVgrItWEtZGYAZTu8MyiIu6zcec \
    3ui"})
    assert resp.status_code == 403

def test_flask_valid_return_id(flask_initialize):
    resp = requests.post(config.url + 'message/send/v1', json={'token': flask_initialize[0], 'channel_id': 1, 'message': "hello world"})
    assert resp.json() == {"message_id": 1}
    resp = requests.post(config.url + 'message/send/v1', json={'token': flask_initialize[0], 'channel_id': 1, 'message': "3Aom4SYU0Z"})
    assert resp.json() == {"message_id": 2}
    resp = requests.post(config.url + 'message/send/v1', json={'token': flask_initialize[0], 'channel_id': 1, 'message': "ropmispdfpnt"})
    assert resp.json() == {"message_id": 3}
    resp = requests.post(config.url + 'message/send/v1', json={'token': flask_initialize[1], 'channel_id': 2, 'message': "WAPCHWWDFPUD"})
    assert resp.json() == {"message_id": 4}
    resp = requests.post(config.url + 'message/send/v1', json={'token': flask_initialize[1], 'channel_id': 2, 'message': "SBNQRBnfacKtIukceONJFa"})
    assert resp.json() == {"message_id": 5}
    resp = requests.post(config.url + 'message/send/v1', json={'token': flask_initialize[1], 'channel_id': 2, 'message': "O"})
    assert resp.json() == {"message_id": 6}
