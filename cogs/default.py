import discord
from discord.ext import commands

from secrets import CLIENT_ID

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

def setup(client):
    client.add_cog(events(client))