import discord
from discord.ext import commands
import os

from helper import get_guild_data, save_guild_data, get_object, create_embed, list_to_string
from constants import SETTINGS, CLIENT_ID
from cogs.roblox import get_group_name

class default(commands.Cog, description = "Default commands and commands for settings."):
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
            "title": f"Loading bot invite...",
            "color": discord.Color.gold()
        }))

        try:
            invite_url = discord.utils.oauth_url(client_id = CLIENT_ID, permissions = discord.Permissions(8))
            await response.edit(embed = create_embed({
                "title": f"Invite Bot",
                "url": invite_url
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load bot invite",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
            
    """

    @commands.command(aliases = ["set"], description = "Changes guild settings.", brief = "administrator")
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
            elif name == "points_per_message":
                value = int(value)
                if value < 0:
                    await response.edit(embed = create_embed({
                        "title": f"{value} must be greater than or equal to 0",
                        "color": discord.Color.red()
                    }))
                    return

                guild_data["points_per_message"] = int(value)
                save_guild_data(guild_data)
                await response.edit(embed = create_embed({
                    "title": f"Set points per message to {value}",
                    "color": discord.Color.green()
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
                        "title": f"Added {value} from AOTD keywords",
                        "color": discord.Color.green()
                    }))
            elif name == "points_per_aotd":
                value = int(value)
                if value < 0:
                    await response.edit(embed = create_embed({
                        "title": f"{value} must be greater than or equal to 0",
                        "color": discord.Color.red()
                    }))
                    return

                guild_data["points_per_aotd"] = int(value)
                save_guild_data(guild_data)
                await response.edit(embed = create_embed({
                    "title": f"Set points per AOTD to {value}",
                    "color": discord.Color.green()
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
            elif name == "group_award":
                value = int(value)
                if value < 0:
                    await response.edit(embed = create_embed({
                        "title": f"{value} must be greater than or equal to 0",
                        "color": discord.Color.red()
                    }))
                    return

                guild_data["group_award"] = int(value)
                save_guild_data(guild_data)
                await response.edit(embed = create_embed({
                    "title": f"Set group award to {value}",
                    "color": discord.Color.green()
                }))            
            elif name == "roblox_games":
                game_id = int(value)
                if game_id in guild_data["roblox_games"]:
                    guild_data["roblox_games"].remove(game_id)
                    save_guild_data(guild_data)
                    await response.edit(embed = create_embed({
                        "title": f"Removed {game_id} from roblox games",
                        "color": discord.Color.green()
                    }))
                else:
                    guild_data["roblox_games"].append(game_id)
                    save_guild_data(guild_data)
                    await response.edit(embed = create_embed({
                        "title": f"Added {game_id} from roblox games",
                        "color": discord.Color.green()
                    }))
            elif name == "game_award":
                value = int(value)
                if value < 0:
                    await response.edit(embed = create_embed({
                        "title": f"{value} must be greater than or equal to 0",
                        "color": discord.Color.red()
                    }))
                    return

                guild_data["game_award"] = int(value)
                save_guild_data(guild_data)
                await response.edit(embed = create_embed({
                    "title": f"Set game award to {value}",
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
            
    @commands.command(aliases = ["settings"], description = "Retrieves guild settings.", brief = "administrator")
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

    @commands.command()
    @commands.guild_only()
    async def help(self, context, flag: str = None, value: str = None):
        response = await context.send(embed = create_embed({
            "title": "Loading commands...",
            "color": discord.Color.gold()
        }))

        try:
            if not flag:
                await response.edit(embed = create_embed({
                    "title": "Help Command Usage",
                }, {
                    "Commands": "help command <command_name>",
                    "Cogs": "help cog <cog_name>",
                    "Settings": "help settings",
                }))
            elif flag == "command":
                for command in self.client.commands:
                    command_name = command.name
                    if command_name == value:
                        cog_name = command.cog_name
                        if not cog_name:
                            cog_name = "cog"

                        aliases = list_to_string(command.aliases)
                        if len(aliases) > 0:
                            aliases = " (" + aliases + ")"

                        description = command.description
                        if description:
                            description = description
                        else:
                            description = ""

                        parameters = list_to_string(command.clean_params)
                        if parameters:
                            parameters = " <" + parameters + ">"

                        brief = command.brief
                        if brief:
                            brief = " Requires " + brief + " permissions."
                        else:
                            brief = " Requires no permissions."

                        await response.edit(embed = create_embed({
                            "title": f"{command_name}{aliases}{parameters}",
                            "description": f"{description}{brief}" or "\u200b"
                        }))
                        return
                await response.edit(embed = create_embed({
                    "title": f"Could not find command {value}",
                    "color": discord.Color.red()
                }))       
            elif flag == "cog":
                command_info = {}
                for command in self.client.commands:
                    cog_name = command.cog_name
                    if not cog_name:
                        cog_name = "cog"

                    command_name = command.name

                    aliases = list_to_string(command.aliases)
                    if len(aliases) > 0:
                        aliases = " (" + aliases + ")"

                    description = command.description
                    if description:
                        description = description
                    else:
                        description = ""

                    parameters = list_to_string(command.clean_params)
                    if parameters:
                        parameters = " <" + parameters + ">"

                    brief = command.brief
                    if brief:
                        brief = " Requires " + brief + " permissions."
                    else:
                        brief = " Requires no permissions."

                    if not command_info.get(cog_name):
                        command_info[cog_name] = {}
                    command_info[cog_name][f"{command_name}{aliases}{parameters}"] = f"{description}{brief}" or "\u200b"

                if not value:
                    cogs = {"cog": "Cog management."}
                    for cog_name, cog_info in self.client.cogs.items():
                        cogs[cog_name] = cog_info.description or "\u200b"

                    await response.edit(embed = create_embed({
                        "title": f"Cogs",
                    }, cogs))
                else:
                    commands = command_info.get(value)
                    if not commands:
                        await response.edit(embed = create_embed({
                            "title": f"Could not find cog {value}",
                            "color": discord.Color.red()
                        }))
                    else: 
                        await response.edit(embed = create_embed({
                            "title": f"{value} Commands",
                        }, commands))
            elif flag == "settings":
                await response.edit(embed = create_embed({
                    "title": "Settings"
                }, SETTINGS))
            else:
                await response.edit(embed = create_embed({
                    "title": f"Invalid flag {flag}",
                    "color": discord.Color.red()
                }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not load commands",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))     

    """

def setup(client):
    client.add_cog(default(client))