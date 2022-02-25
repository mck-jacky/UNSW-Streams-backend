# Assumptions

*(Assumptions we would like marked, are prefixed and denoted with a [M].)*

**channels_create_v1**
* [M] Channels with the same name can be created but each have unique channel_id.
* [M] The creator of the channel is in both 'owner_members' and 'all_members'.

**channel_message_v1**
* The order of messages list to return will be (latest to the least latest). Because channel stores messages in this order as well.
* When start is less than 0, it will raise error or return an empty list. Because negative integer cannot represent message index.

**channel_join**
* We are storing the auth_user_id (as an integer) of users in the 'all_members' and 'owner_members' lists, within the 'channels' dictionary.

**channel_invite**
* [M] A global owner does not have permission to invite users to a channel if they, the global owner, are not a member of that channel.

**channel_list_v1 & channel_listall_v1**
* In the channels dictionary, channel_id is always assumed to be an integer.
* [M] Assume channels_list and channels_listall will not be called before any channels_create function is called. However, code has been written to handle an empty datastore list.
* For the function in channels.py, channels_list_v1(auth_user_id), assume auth_user_id is of type string. Is appropriately converted within function for safe measure.

**channel_leave_v1**
* Will not throw an error if the only channel owner leaves

**auth_register_v1**
* [M] It is assumed that no more than 10 users have the exact same name --> this means that index of the name handle needs to be only one digit long to uniquely identify a user.
* [M] It is assumed that the first and last name are not only composed of special characters, so the name_handle will not be the empty string.

**admin_userpermission_change_v1**
* Assume setting a user the their current permission id is allowed. E.g. Setting a global owner to be a global owner 
* Assume a user can demote themselves (if they are a global owner but not the sole global owner)

**search/v1**
* If a user leaves a channel/dm, the messages which they send in these channels
will not be returned.
* The order of the returned messages doesn't matter???

