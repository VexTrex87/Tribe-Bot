import discord
from discord.ext import commands
from time import time

from helper import get_guild_data, get_user_data, save_user_data, get_all_user_data, create_embed

class events(commands.Cog, description = "Default events."):
    def __init__(self, client):
        self.client = client
        self.recent_messagers = {}

    @commands.Cog.listener()
    async def on_command_error(self, context, error):
        if isinstance(error, commands.NoPrivateMessage):
            await context.send(embed = create_embed({
                "title": f"Commands must be used in servers",
                "color": discord.Color.red()
            }))
        elif isinstance(error, commands.MissingPermissions) or isinstance(error, commands.CheckFailure):
            await context.send(embed = create_embed({
                "title": f"You do not have permission to run this command",
                "color": discord.Color.red()
            }))
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            await context.send(embed = create_embed({
                "title": f"Incorrect syntax",
                "color": discord.Color.red()
            }))
            
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
        if message.author.bot or not message.guild:
            return

        guild_data = get_guild_data(message.guild.id)

        if message.content == "<@!834455533423427584>":
            await message.channel.send(embed = create_embed({
                "title": "Prefix is `{}`. Type `{}help` for a list of commands.".format(guild_data["prefix"], guild_data["prefix"])
            }))

        user_data = get_user_data(message.author.id)
        if message.channel.id in guild_data["point_channels"]:
            time_since_last_message = self.recent_messagers.get(message.author.id)
            if time_since_last_message and time() - time_since_last_message < guild_data["message_cooldown"]:
                return
            
            self.recent_messagers[message.author.id] = time()
            user_data["points"] += guild_data["points_per_message"]
            save_user_data(user_data)

        qotd_channel = message.guild.get_channel(guild_data["qotd_channel"])
        if qotd_channel:
            if message.channel == qotd_channel:
                for user_data in get_all_user_data():
                    user_data["answered_qotd"] = False
                    save_user_data(user_data)

            for aotd_keyword in guild_data["aotd_keywords"]:
                if aotd_keyword in message.content.lower() or qotd_channel.mention in message.content.lower():
                    if not user_data["answered_qotd"]:
                        points_to_give = guild_data["points_per_aotd"]

                        user_data["answered_qotd"] = True
                        user_data["points"] += points_to_give
                        save_user_data(user_data)

                        await message.author.send(embed = create_embed({
                            "title": f"You earned {points_to_give} points for answering the QOTD",
                        }))
                        
                        break

def setup(client):
    client.add_cog(events(client))
