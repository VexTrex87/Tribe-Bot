import discord
from discord.ext import commands
import json

from secrets import CLIENT_ID
from helper import get_guild_data, save_guild_data, draw_dictionary

class events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, context):
        try:
            ping = round(self.client.latency * 1000)
            await context.send(f"{ping} ms")
        except Exception as error_message:
            await context.send(error_message)

    @commands.command()
    async def invite(self, context):
        try:
            invite_url = discord.utils.oauth_url(client_id = CLIENT_ID, permissions = discord.Permissions(8))
            await context.send(invite_url)
        except Exception as error_message:
            await context.send(error_message)

    @commands.command(aliases = ["set"])
    async def setsettings(self, context, name, *, value):
        try:
            if name == "prefix":
                guild_data = get_guild_data(context.guild.id)
                guild_data["prefix"] = value
                save_guild_data(guild_data)
            else:
                await context.send(f"{name} is an invalid setting")
                return
            await context.send(f"Changed {name} to {value}")
        except Exception as error_message:
            await context.send(error_message)

    @commands.command(aliases = ["settings"])
    async def getsettings(self, context):
        try:
            guild_data = get_guild_data(context.guild.id)
            guild_data.pop("_id")
            await context.send(draw_dictionary(guild_data))
        except Exception as error_message:
            await context.send(error_message)

def setup(client):
    client.add_cog(events(client))