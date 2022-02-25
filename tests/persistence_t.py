import sys
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.data_store import data_store
from src.other import clear_v1

# ZERO
def clear_data_store():
    clear_v1()

# ONE
def print_data_store():
    store = data_store.get()
    print(store)

# TWO
def register_general_kenobi():
    auth_register_v1("e@mail1.com", "hunter1", "General", "Kenobi")

# THREE
def register_bold_one():
    auth_register_v1("e@mail2.com", "hunter2", "Bold", "One")

# FOUR
def register_self_senate():
    auth_register_v1("e@mail3.com", "hunter3", "IAM", "THESENATE")

# FIVE
def create_senate_channel(user):
    channels_create_v1(user["auth_user_id"], "THESENATE", True)

################################################################################

if __name__ == "__main__":
    # Usage: python3 -m tests.persistence_t NUMBER
    arg = (sys.argv[1])
    
    funcList = [
        clear_data_store,
        print_data_store,
        register_general_kenobi,
        register_bold_one,
        register_self_senate,
        create_senate_channel
        ]

    funcList[int(arg)]()
