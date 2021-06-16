from pymongo import MongoClient
import discord
import os
import math
from dotenv import load_dotenv
from constants import DEFAULT_GUILD_DATA, DEFAULT_USER_DATA, IS_TESTING, LIVE_DATABASE, TESTING_DATABASE
import asyncio

load_dotenv('.vscode/.env')

MONGO_TOKEN = os.getenv("DB_TOKEN")
cluster = MongoClient(MONGO_TOKEN)
database_name = IS_TESTING and TESTING_DATABASE or LIVE_DATABASE
guild_datastore = cluster[database_name]["guild"]
user_datastore = cluster[database_name]["user"]
giveaways_datastore = cluster[database_name]["giveaways"]

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
    new_user_data = DEFAULT_USER_DATA.copy()
    for key in new_user_data.keys():
        if user_data.get(key):
            new_user_data[key] = user_data[key]
    return new_user_data

def get_user_data(user_id: int):
    user_data = user_datastore.find_one({"user_id": user_id}) 
    data_is_new = False

    if not user_data:
        data_is_new = True
        user_data = DEFAULT_USER_DATA.copy()
        user_data["user_id"] = user_id

    user_data = attach_default_user_data(user_data)

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

def get_object(objects: list, value):
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

def create_embed(info: dict = {}, fields: dict = {}):
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

def list_to_string(list: list):
    return ", ".join(list)

def format_time(timestamp):
    hours = math.floor(timestamp / 60 / 60)
    minutes = math.floor((timestamp - (hours * 60 * 60)) / 60)
    seconds = math.floor((timestamp) - (hours * 60 * 60) - (minutes * 60))

    hours = str(hours)
    if len(hours) == 1:
        hours = "0" + hours

    minutes = str(minutes)
    if len(minutes) == 1:
        minutes = "0" + minutes

    seconds = str(seconds)
    if len(seconds) == 1:
        seconds = "0" + seconds

    timestamp_text = f"{hours}:{minutes}:{seconds}"
    return timestamp_text

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def check_if_bot_manager(context):
    if not context.guild:
        return False
        
    if context.author == context.guild.owner:
        return True
    elif context.author.guild_permissions.administrator:
        return True

    guild_data = get_guild_data(context.guild.id)

    bot_manager_id = guild_data["bot_manager"]
    if not bot_manager_id:
        return False

    bot_manage_role = context.guild.get_role(bot_manager_id)
    if not bot_manage_role:
        return False

    if bot_manage_role in context.author.roles:
        return True
    else:
        return False

def sort_dictionary(dictionary, is_reversed = False):
    sorted_dictionary = {}
    sorted_list = sorted(dictionary.items(), key = lambda x: x[1], reverse = is_reversed)
    for value in sorted_list:
        sorted_dictionary[value[0]] = value[1]
    return sorted_dictionary

def get_first_n_items(dictionary, number):
    new_dictionary = {}
    for index in list(dictionary)[:number]:
        new_dictionary[index] = dictionary.get(index)
    return new_dictionary

async def wait_for_reaction(client, context, emoji, timeout=30):
    def check_response(reaction, user):
        if user == context.author:
            if type(emoji) == list and reaction.emoji in emoji or reaction.emoji == emoji:
                if reaction.message.channel == context.channel:
                    return True

    try:
        reaction, user = await client.wait_for("reaction_add", check=check_response, timeout=timeout)
        return reaction, user
    except asyncio.TimeoutError:
        return None, None

async def wait_for_message(client, context, timeout=30):
    def check_message(message):
        return message.author == context.author

    try:
        message = await client.wait_for("message", check=check_message, timeout=timeout)
        return message
    except asyncio.TimeoutError:
        return None
