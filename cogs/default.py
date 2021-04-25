import discord
from discord.ext import commands

from secrets import CLIENT_ID
from helper import get_guild_data, save_guild_data, draw_dictionary, get_object, create_embed

class default(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Loading ping...",
            "color": discord.Color.gold()
        }))

        try:
            ping = round(self.client.latency * 1000)
            await response.edit(embed = create_embed({
                "title": f"Your ping is {ping} ms",
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load ping",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
            
    @commands.command()
    async def invite(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Loading bot invite link...",
            "color": discord.Color.gold()
        }))

        try:
            invite_url = discord.utils.oauth_url(client_id = CLIENT_ID, permissions = discord.Permissions(8))
            await response.edit(embed = create_embed({
                "title": f"Bot invite link",
                "url": invite_url
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load bot invite link",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
            
    @commands.command(aliases = ["set"])
    async def setsettings(self, context, name, *, value):
        response = await context.send(embed = create_embed({
            "title": f"Setting {name} to {value}...",
            "color": discord.Color.gold()
        }))

        try:
            guild_data = get_guild_data(context.guild.id)
            if name == "prefix":
                guild_data["prefix"] = value    
                save_guild_data(guild_data)
                await response.edit(embed = create_embed({
                    "title": f"Set prefix to {value}",
                    "color": discord.Color.green()
                }))
            elif name == "daily_reward":
                guild_data["daily_reward"] = int(value)
                save_guild_data(guild_data)
                await response.edit(embed = create_embed({
                    "title": f"Set daily reward to {value}",
                    "color": discord.Color.green()
                }))
            elif name == "point_channels":
                channel = get_object(context.guild.text_channels, value)
                if channel:
                    if channel.id in guild_data["point_channels"]:
                        guild_data["point_channels"].remove(channel.id)
                        save_guild_data(guild_data)
                        await response.edit(embed = create_embed({
                            "title": f"Removed {value} from point channels",
                            "color": discord.Color.green()
                        }))
                    else:
                        guild_data["point_channels"].append(channel.id)
                        save_guild_data(guild_data)
                        await response.edit(embed = create_embed({
                            "title": f"Added {value} to point channels",
                            "color": discord.Color.green()
                        }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"Could not find text channel {value}",
                        "color": discord.Color.red()
                    }))
            elif name == "message_cooldown":
                guild_data["message_cooldown"] = int(value)
                save_guild_data(guild_data)
                await response.edit(embed = create_embed({
                    "title": f"Set message cooldown to {value} second(s)",
                    "color": discord.Color.green()
                }))
            elif name == "qotd_channel":
                channel = get_object(context.guild.text_channels, value)
                if channel:
                    guild_data["qotd_channel"] = channel.id
                    save_guild_data(guild_data)
                    await response.edit(embed = create_embed({
                        "title": f"Set QOTD channel to {value}",
                        "color": discord.Color.green()
                    }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"Could not find text channel {value}",
                        "color": discord.Color.red()
                    }))
            elif name == "aotd_channel":
                channel = get_object(context.guild.text_channels, value)
                if channel:
                    guild_data["aotd_channel"] = channel.id
                    save_guild_data(guild_data)
                    await response.edit(embed = create_embed({
                        "title": f"Set AOTD channel to {value}",
                        "color": discord.Color.green()
                    }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"Could not find text channel {value}",
                        "color": discord.Color.red()
                    }))
            elif name == "giveaway_channel":
                channel = get_object(context.guild.text_channels, value)
                if channel:
                    guild_data["giveaway_channel"] = channel.id
                    save_guild_data(guild_data)
                    await response.edit(embed = create_embed({
                        "title": f"Set giveaway channel to {value}",
                        "color": discord.Color.green()
                    }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"Could not find text channel {value}",
                        "color": discord.Color.red()
                    }))
            else:
                await response.edit(embed = create_embed({
                    "title": f"{name} is an invalid setting",
                    "color": discord.Color.red()
                }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not change settings",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
            
    @commands.command(aliases = ["settings"])
    async def getsettings(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Loading settings...",
            "color": discord.Color.gold()
        }))
        
        try:
            guild_data = get_guild_data(context.guild.id)
            guild_data.pop("_id")
            guild_data.pop("guild_id")
            guild_data.pop("giveaways")
            await response.edit(embed = create_embed({
                "title": f"Guild Settings",
            }, guild_data))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load settings",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
            
def setup(client):
    client.add_cog(default(client))