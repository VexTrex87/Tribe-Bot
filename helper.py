from pymongo import MongoClient
import discord
import json

from secrets import MONGO_TOKEN
from constants import DEFAULT_GUILD_DATA, DEFAULT_USER_DATA

cluster = MongoClient(MONGO_TOKEN)
guild_datastore = cluster["database1"]["guild"]
user_datastore = cluster["database1"]["user"]
giveaways_datastore = cluster["database1"]["giveaways"]

# guild data

def attach_default_guild_data(guild_data):
    new_guild_data = DEFAULT_GUILD_DATA.copy()
    for key in new_guild_data.keys():
        if guild_data.get(key):
            new_guild_data[key] = guild_data[key]
    return new_guild_data

def get_guild_data(guild_id: int):
    guild_data = guild_datastore.find_one({"guild_id": guild_id}) 
    data_is_new = False

    if not guild_data:
        data_is_new = True
        guild_data = DEFAULT_GUILD_DATA.copy()
        guild_data["guild_id"] = guild_id

    guild_data = attach_default_guild_data(guild_data)

    if data_is_new:
        guild_datastore.insert_one(guild_data)

    return guild_data

def save_guild_data(guild_data):
    guild_datastore.update_one({"guild_id": guild_data["guild_id"]}, {"$set": guild_data})

def get_all_guild_data(sort_value: str = None):
    all_cursor_data = sort_value and guild_datastore.find().sort(sort_value, -1) or guild_datastore.find({})
    all_data = []

    for data in all_cursor_data:
        data = attach_default_guild_data(data)
        all_data.append(data)

    return all_data

# user data

def attach_default_user_data(user_data):
    if not user_data.get("points"):
        user_data["points"] = DEFAULT_USER_DATA["points"]
    if not user_data.get("claimed_daily_reward_time"):
        user_data["claimed_daily_reward_time"] = DEFAULT_USER_DATA["claimed_daily_reward_time"]
    if not user_data.get("answered_qotd"):
        user_data["answered_qotd"] = DEFAULT_USER_DATA["answered_qotd"]
    return user_data

def get_user_data(user_id: int):
    user_data = user_datastore.find_one({"user_id": user_id}) 
    data_is_new = False

    if not user_data:
        data_is_new = True
        user_data = DEFAULT_USER_DATA.copy()
        user_data["user_id"] = user_id

    attach_default_user_data(user_data)

    if data_is_new:
        user_datastore.insert_one(user_data)

    return user_data

def save_user_data(user_data):
    user_datastore.update_one({"user_id": user_data["user_id"]}, {"$set": user_data})

def get_all_user_data(sort_value: str = None):
    all_cursor_data = sort_value and user_datastore.find().sort(sort_value, -1) or user_datastore.find({})
    all_data = []

    for data in all_cursor_data:
        data = attach_default_user_data(data)
        all_data.append(data)

    return all_data

# giveaways data

def get_giveaway(message_id: int):
    return giveaways_datastore.find_one({"message_id": message_id}) 

def save_giveaway(giveaway_data):
    giveaways_datastore.update_one({"message_id": giveaway_data["message_id"]}, {"$set": giveaway_data})

def create_giveaway(giveaway_data):
    giveaways_datastore.insert_one(giveaway_data)

def get_all_giveaways():
    return giveaways_datastore.find({})

def delete_giveaway(message_id: int):
    giveaways_datastore.delete_one({"message_id": message_id})

# other

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

def get_object(objects: [], value):
    for obj in objects:
        try:
            if obj.name == value or value == obj.mention or obj.id == int(value):
                return obj
        except:
            pass

def parse_to_timestamp(time):
    prefix = int(time[:-1])
    suffix = time[-1:]

    if suffix == "s":
        return prefix
    elif suffix == "m":
        return prefix * 60
    elif suffix == "h":
        return prefix * 60 * 60
    elif suffix == "d":
        return prefix * 60 * 60 * 24
    else:
        return int(time)

def create_embed(info: {} = {}, fields: {} = {}):
    embed = discord.Embed(
        title = info.get("title") or "",
        description = info.get("description") or "",
        colour = info.get("color") or discord.Color.blue(),
        url = info.get("url") or "",
    )

    for name, value in fields.items():
        embed.add_field(name = name, value = value, inline = info.get("inline") or False)

    if info.get("author"):
        embed.set_author(name = info.author.name, url = info.author.mention, icon_url = info.author.avatar_url)
    if info.get("footer"):
        embed.set_footer(text = info.footer)
    if info.get("image"):
        embed.set_image(url = info.url)
    if info.get("thumbnail"):
        embed.set_thumbnail(url = info.get("thumbnail"))
    
    return embed

def convert_dictionary_to_tree(dictionary: dict):
    return json.dumps(dictionary, indent = 4)
