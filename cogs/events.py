import discord
from discord.ext import commands

class events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_connect(self):
        print("connected") 

    @commands.Cog.listener()
    async def on_disconnect(self):
        print("disconnected")  

    @commands.Cog.listener()
    async def on_resumed(self):
        print("resumed")  

    @commands.Cog.listener()
    async def on_ready(self):
        print("ready")
        
def setup(client):
    client.add_cog(events(client))