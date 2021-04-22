import discord
from discord.ext import commands
from time import time

from helper import get_guild_data, get_user_data, save_user_data

class cog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.recent_messagers = {}

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
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild_data = get_guild_data(message.guild.id)
        if message.channel.id in guild_data["point_channels"]:
            time_since_last_message = self.recent_messagers.get(message.author.id)
            if time_since_last_message and time() - time_since_last_message < guild_data["message_cooldown"]:
                return
            
            self.recent_messagers[message.author.id] = time()
            user_data = get_user_data(message.author.id)
            user_data["points"] += guild_data["points_per_message"]
            save_user_data(user_data)
    
def setup(client):
    client.add_cog(cog(client))