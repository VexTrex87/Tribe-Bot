import discord
from discord.ext import commands

from secrets import CLIENT_ID
from helper import get_guild_data, save_guild_data, draw_dictionary, get_text_channel

class cog(commands.Cog):
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
            guild_data = get_guild_data(context.guild.id)
            if name == "prefix":
                guild_data["prefix"] = value    
                save_guild_data(guild_data)
                await context.send(f"Set prefix to {value}")   
            elif name == "daily_reward":
                guild_data["daily_reward"] = int(value)
                save_guild_data(guild_data)
                await context.send(f"Set daily reward to {value}")   
            elif name == "point_channels":
                channel = get_text_channel(context.guild.text_channels, value)
                if channel:
                    if channel.id in guild_data["point_channels"]:
                        guild_data["point_channels"].remove(channel.id)
                        save_guild_data(guild_data)
                        await context.send(f"Removed {value} from point channels")   
                    else:
                        guild_data["point_channels"].append(channel.id)
                        save_guild_data(guild_data)
                        await context.send(f"Added {value} to point channels")   
                else:
                    await context.send(f"Could not find text channel {value}")
            elif name == "message_cooldown":
                guild_data["message_cooldown"] = int(value)
                save_guild_data(guild_data)
                await context.send(f"Set message cooldown to {value} second(s)")   
            else:
                await context.send(f"{name} is an invalid setting")
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
    client.add_cog(cog(client))