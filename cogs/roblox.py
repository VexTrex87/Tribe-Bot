import discord
from discord.ext import commands
import aiohttp

from helper import create_embed, convert_dictionary_to_tree
from constants import GROUP_INFO_URL

async def get_group_name(group_id: int):
    url = GROUP_INFO_URL.replace("GROUP_ID", str(group_id))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data.get("name")
class roblox(commands.Cog):
    def __init__(self, client):
        self.client = client

def setup(client):
    client.add_cog(roblox(client))