import os
import json
import pickle

'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

## YOU SHOULD MODIFY THIS OBJECT BELOW

'''
This is our agreed upon structure:

initial_object = {
    'users': [
        {
            'name_first': "",
            'name_last': "",
            'name_handle': "",
            'email': "",
            'password': "",
            'auth_user_id': 0,
            'permission_id': 2,  # Member by default (not a global owner)
            'session_ids': [],   # List of all sessions that the user is currently active in
            'notifications': [
                {
                    channel_id: -1,      # (int), -1 if the notification is not in a channel
                    dm_id: -1,           # (int), -1 if the notification is not in a dm
                    notification_message # (str)
                }
            ]
        }
    ],
    'channels': [
        {
            'channel_id': 0,
            'name': "",
            'is_public': True,
            'owner_members': [],
            'all_members': [],
            'messages': [
                {
                'message_id': 0, 
                'u_id': 0, 
                'message': "", 
                'time_created': 0,
                'reacts': [
                    {
                    react_id: 1, # As of 30/10/21, the only react_id is 1
                    u_ids: []
                    }
                ],
                is_pinned: 0/1,   # 0 is false, 1 is true
                owner_id: 0
                }
            ]
        }
    ],
    'dms': [
        {
            'dm_id': 0,     # Entire DM identifier (like channel ID)
            'owner_id': 0,  # DM creator's user ID
            'u_ids': [],    # Users who receive DMs
            'name': "",     # Name of DM
            'messages': [
                {
                'message_id': 0, 
                'u_id': 0, 
                'message': "", 
                'time_created': 0,
                'reacts': [
                    {
                    react_id: 1, # As of 30/10/21, the only react_id is 1
                    u_ids: []
                    }
                ],
                is_pinned: 0/1,   # 0 is false, 1 is true
                owner_id: 0
                }
            ]
        }
    ],
    'session_id': 0,
    'message_id': 0,
    'dm_id': 0
}
'''

# We will start with empty lists and a session_id zero value:
initial_object = {
    'users': [],
    'channels': [],
    'dms': [],
    'session_id': 0,
    'message_id': 0,
    'dm_id': 0
}

## YOU SHOULD MODIFY THIS OBJECT ABOVE

class Datastore:
    """
    Persistence process:
    When server.py is run, data_store is loaded from data_save.(json/p), and
    each time data_store is set, the data_save.(json/p) is updated to data_store.

    More details:
    1. When server.py is run, it will import and load from data_store.py, the
       Datastore class. When this class is called for the first time, the class
       variable <self.__server> is called first, which initialises at zero.
    
    2. If <self.__server> is zero, from the point-of-view of the Datastore
       class, the server was not active prior to this point, and therefore would
       not have loaded from the offline persistence file. Therefore, when
       <self.__server> == zero, the offline file is attempted to either be
       loaded if present, or created.
    
    3. After loading or creating the offline file, the server's primary
       data_store version (that is passed around in the functions) is the
       virtual data_store, not re-loading from the offline file with every
       data_store.get() call. I.e., the offline file is ONLY used on the very
       first data_store.get() call.
    
    4. Vice-versa, the server will continually write to the offline file with
       each data_store.set() call.

    One can turn on or off the storage format, either using JSON <.json> or
    Pickle <.p>. The persistence file will therefore be in the root folder,
    called either data_save.json, or data_save.p.
    """

    def __init__(self):
        self.__store = initial_object
        self.__server = 0      # If zero, server has just started
        self.__directory = ""  # Path to root folder of project
        self.save_location()   # Class function to find relative path to root

        """
        Activate boolean to utilise that particular persistence route. Both can
        be active, or none. None active is the original Datastore method.
        """
        
        self.__json_persistence = True
        self.__pickle_persistence = False

    def get(self):
        """
        Apart from the original loading of the virtual data_store, get() checks
        if the server was restarted. If server start is True, then load from
        the local data_save file. If no such file exists, then it is created,
        and the virtual data_store is instead saved into it. This load only
        happens when the server restarts; no other get() call will trigger a
        file load.
        """

        if self.__server == 0:  # Start loading from file into server

            if self.__json_persistence == True:
                try:
                    with open(self.__directory + '.json', 'r') as FILE:
                        self.__store = json.load(FILE)
                except (EOFError, FileNotFoundError, json.decoder.JSONDecodeError):
                    with open(self.__directory + '.json', 'w') as FILE:
                        json.dump(self.__store, FILE)
            
            if self.__pickle_persistence == True:
                try:
                    with open(self.__directory + '.p', 'rb') as FILE:
                        self.__store = pickle.load(FILE)
                except (EOFError, FileNotFoundError):
                    with open(self.__directory + '.p', 'wb') as FILE:
                        pickle.dump(self.__store, FILE)

        self.__server += 1  # Now server != 0 until a server restart

        # Original code
        return self.__store

    def set(self, store):
        # Original code
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

        """
        Write to data_save file(s) upon every data_store.set() call. Not server-
        status dependant.
        """
        
        if self.__json_persistence == True:
            try:
                with open(self.__directory + '.json', 'r') as FILE:
                    json.load(FILE)
                with open(self.__directory + '.json', 'w') as FILE:
                    json.dump(self.__store, FILE)
            except (EOFError, FileNotFoundError, json.decoder.JSONDecodeError):
                with open(self.__directory + '.json', 'w') as FILE:
                    json.dump(self.__store, FILE)
        
        if self.__pickle_persistence == True:
            try:
                with open(self.__directory + '.p', 'rb') as FILE:
                    pickle.load(FILE)
                with open(self.__directory + '.p', 'wb') as FILE:
                    pickle.dump(self.__store, FILE)
            except (EOFError, FileNotFoundError):
                with open(self.__directory + '.p', 'wb') as FILE:
                    pickle.dump(self.__store, FILE)
    
    def save_location(self):
        """
        Finds the root directory of the project, project-backend, even from the
        src and tests subdirectory.
        """

        location_to_save = os.path.join(os.getcwd(), 'data_save')
        location_to_save = location_to_save.replace('/src', '')
        location_to_save = location_to_save.replace('/tests', '')
        self.__directory = location_to_save

print('Loading Datastore...')

global data_store
data_store = Datastore()
