import discord
from discord.ext import commands
import aiohttp

from helper import create_embed, convert_dictionary_to_tree
from constants import GROUP_INFO_URL, USER_GROUPS_URL, USER_INFO_URL, USERS_URL

async def get_group_name(group_id: int):
    url = GROUP_INFO_URL.replace("GROUP_ID", str(group_id))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data.get("name")

async def get_user_groups(user_id: int):
    url = USER_GROUPS_URL.replace("USER_ID", str(user_id))
    groups = []
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_data = await response.json()
                for group_info in response_data["data"]:
                    group_id = group_info["group"]["id"]
                    groups.append(group_id)
                return groups

async def get_username(user_id: int):
    url = USER_INFO_URL.replace("USER_ID", str(user_id))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data["name"]

async def get_user_id(username: str):
    data = {"usernames": [username], "excludeBannedUsers": False}
    async with aiohttp.ClientSession() as session:
        async with session.post(USERS_URL, data = data) as response:
            if response.status == 200:
                response_data = await response.json()
                user = response_data["data"][0]
                if not user:
                    return None
                return user["name"]

class roblox(commands.Cog):
    def __init__(self, client):
        self.client = client

def setup(client):
    client.add_cog(roblox(client))