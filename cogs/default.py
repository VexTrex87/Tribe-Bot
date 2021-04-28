import discord
from discord.ext import commands
import os

from helper import get_guild_data, save_guild_data, draw_dictionary, get_object, create_embed
from cogs.roblox import get_group_name

CLIENT_ID = os.getenv("TB_CLIENT_ID")

class default(commands.Cog):
    def __init__(self, client):
        self.client = client
 
    @commands.command()
    @commands.guild_only()
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
    @commands.check_any(commands.has_permissions(create_instant_invite = True))
    @commands.guild_only()
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
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    @commands.guild_only()
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
                            "title": f"Removed {channel.name} from point channels",
                            "color": discord.Color.green()
                        }))
                    else:
                        guild_data["point_channels"].append(channel.id)
                        save_guild_data(guild_data)
                        await response.edit(embed = create_embed({
                            "title": f"Added {channel.name} to point channels",
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
                        "title": f"Set QOTD channel to {channel.name}",
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
                        "title": f"Set giveaway channel to {channel.name}",
                        "color": discord.Color.green()
                    }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"Could not find text channel {value}",
                        "color": discord.Color.red()
                    }))
            elif name == "aotd_keywords":
                value = value.lower()
                if value in guild_data["aotd_keywords"]:
                    guild_data["aotd_keywords"].remove(value)
                    save_guild_data(guild_data)
                    await response.edit(embed = create_embed({
                        "title": f"Removed {value} from AOTD keywords",
                        "color": discord.Color.green()
                    }))
                else:
                    guild_data["aotd_keywords"].append(value)
                    save_guild_data(guild_data)
                    await response.edit(embed = create_embed({
                        "title": f"Added {value} to AOTD keywords",
                        "color": discord.Color.green()
                    }))
            elif name == "giveaway_entry_cost":
                guild_data["giveaway_entry_cost"] = int(value)
                save_guild_data(guild_data)
                await response.edit(embed = create_embed({
                    "title": f"Set giveaway entry cost to {value}",
                    "color": discord.Color.green()
                }))
            elif name == "roblox_groups":
                group_id = int(value)
                group_name = await get_group_name(group_id)
                if not group_name:
                    await response.edit(embed = create_embed({
                        "title": f"Could not find roblox group {group_id}",
                        "color": discord.Color.red()
                    }))
                    return

                if group_id in guild_data["roblox_groups"]:
                    guild_data["roblox_groups"].remove(group_id)
                    save_guild_data(guild_data)
                    await response.edit(embed = create_embed({
                        "title": f"Removed {group_name} ({group_id}) from roblox groups",
                        "color": discord.Color.green()
                    }))
                else:
                    guild_data["roblox_groups"].append(group_id)
                    save_guild_data(guild_data)
                    await response.edit(embed = create_embed({
                        "title": f"Added {group_name} ({group_id}) to roblox groups",
                        "color": discord.Color.green()
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
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    @commands.guild_only()
    async def getsettings(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Loading settings...",
            "color": discord.Color.gold()
        }))
        
        try:
            guild_data = get_guild_data(context.guild.id)

            if guild_data.get("_id"):
                guild_data.pop("_id")
            if guild_data.get("guild_id"):
                guild_data.pop("guild_id")

            if guild_data.get("point_channels"):
                point_channels = []
                for channel_id in guild_data["point_channels"]:
                    channel = context.guild.get_channel(channel_id)
                    if channel:
                        point_channels.append(channel.mention)
                guild_data["point_channels"] = ", ".join(point_channels)

            if guild_data.get("roblox_groups"):
                roblox_groups = []
                for group_id in guild_data["roblox_groups"]:
                    group_name = await get_group_name(group_id)
                    if group_name:
                        roblox_groups.append(f"{group_name} ({group_id})")
                guild_data["roblox_groups"] = ", ".join(roblox_groups)

            if guild_data.get("qotd_channel"):
                channel = context.guild.get_channel(channel_id)
                if channel:
                    guild_data["qotd_channel"] = channel.mention

            if guild_data.get("giveaway_channel"):
                channel = context.guild.get_channel(channel_id)
                if channel:
                    guild_data["giveaway_channel"] = channel.mention

            if guild_data.get("aotd_keywords"):
                guild_data["aotd_keywords"] = ", ".join(guild_data["aotd_keywords"])

            await response.edit(embed = create_embed({
                "title": f"Guild Settings",
                "inline": True,
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