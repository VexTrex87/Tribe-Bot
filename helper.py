from pymongo import MongoClient
from secrets import MONGO_TOKEN
from constants import DEFAULT_GUILD_DATA, DEFAULT_USER_DATA

cluster = MongoClient(MONGO_TOKEN)
guild_datastore = cluster["database1"]["guild"]
user_datastore = cluster["database1"]["user"]

def get_guild_data(guild_id: int):
    guild_data = guild_datastore.find_one({"guild_id": guild_id}) 
    data_is_new = False

    if not guild_data:
        data_is_new = True
        guild_data = DEFAULT_GUILD_DATA.copy()
        guild_data["guild_id"] = guild_id

    if not guild_data.get("prefix"):
        guild_data["prefix"] = DEFAULT_GUILD_DATA["prefix"]
    if not guild_data.get("daily_reward"):
        guild_data["daily_reward"] = DEFAULT_GUILD_DATA["daily_reward"]
        
    if data_is_new:
        guild_datastore.insert_one(guild_data)

    return guild_data

def save_guild_data(guild_data):
    guild_datastore.update_one({"guild_id": guild_data["guild_id"]}, {"$set": guild_data})

def get_user_data(user_id: int):
    user_data = user_datastore.find_one({"user_id": user_id}) 
    data_is_new = False

    if not user_data:
        data_is_new = True
        user_data = DEFAULT_USER_DATA.copy()
        user_data["user_id"] = user_id

    if not user_data.get("points"):
        user_data["points"] = DEFAULT_USER_DATA["points"]
    if not user_data.get("claimed_daily_reward_time"):
        user_data["claimed_daily_reward_time"] = DEFAULT_USER_DATA["claimed_daily_reward_time"]

    if data_is_new:
        user_datastore.insert_one(user_data)

    return user_data

def save_user_data(user_data):
    user_datastore.update_one({"user_id": user_data["user_id"]}, {"$set": user_data})

def draw_dictionary(dictionary: dict):
    message = "```"
    max_key_length = 0

    for key in dictionary.keys():
        if len(key) > max_key_length:
            max_key_length = len(key)
    max_key_length += 5

    for key, value in dictionary.items():
        spaces = max_key_length - len(key)
        tab = " " * spaces
        message = message + f"{key}{tab}{value}\n"

    message = message + "```"
    return message