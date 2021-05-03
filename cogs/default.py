import discord
from discord.ext import commands
import os
import time
import asyncio
import traceback

from helper import get_guild_data, save_guild_data, get_object, create_embed, list_to_string, format_time, is_number, parse_to_timestamp
from constants import SETTINGS, CLIENT_ID, COMMANDS, NEXT_EMOJI, BACK_EMOJI, CHANGE_EMOJI, DEFAULT_GUILD_DATA, WAIT_DELAY
from cogs.roblox import get_group_name

class default(commands.Cog, description = "Default commands and commands for settings."):
    def __init__(self, client):
        self.client = client
        self.uptime = time.time()
 
    @commands.command()
    @commands.guild_only()
    async def info(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Loading bot info...",
            "color": discord.Color.gold()
        }))

        try:
            ping = round(self.client.latency * 1000)
            invite_url = discord.utils.oauth_url(client_id = CLIENT_ID, permissions = discord.Permissions(8))
            uptime = format_time(round(time.time() - self.uptime))
            servers = len(await self.client.fetch_guilds(limit = None).flatten())
            users = len([member for member in self.client.get_all_members()])

            await response.edit(embed = create_embed({
                "title": f"Bot Info",
                "url": invite_url,
            }, {
                "Ping": f"{ping} ms",
                "Uptime": uptime,
                "Servers": servers,
                "Users": users
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load bot info",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
 
    @commands.command()
    @commands.guild_only()
    async def help(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Loading commands...",
            "color": discord.Color.gold()
        }))

        try:
            pages = []
            current_page = 0
            for category, commands in COMMANDS.items():
                pages.append(create_embed({
                    "title": category,
                }, commands))

            await response.edit(embed = pages[current_page])

            while True:
                def check_response(reaction, user):
                    return user == context.author and reaction.message == response

                try:
                    await response.add_reaction(BACK_EMOJI)
                    await response.add_reaction(NEXT_EMOJI)

                    reaction, user = await self.client.wait_for("reaction_add", check = check_response, timeout = 60)

                    if str(reaction.emoji) == NEXT_EMOJI:
                        if current_page + 1 >= len(pages):
                            current_page = len(pages) - 1
                        else:
                            current_page += 1
                    elif str(reaction.emoji) == BACK_EMOJI:
                        if current_page == 0:
                            current_page = 0
                        else:
                            current_page -= 1

                    await response.edit(embed = pages[current_page])
                    await response.remove_reaction(reaction.emoji, user)
                except asyncio.TimeoutError:
                    await response.edit(embed = create_embed({
                        "title": f"You did not respond in time",
                        "color": discord.Color.red()
                    }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load commands",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    @commands.guild_only()
    async def settings(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Loading settings...",
            "color": discord.Color.gold()
        }))
        
        try:
            while True:
                guild_data = get_guild_data(context.guild.id)

                # format settings

                if guild_data.get("_id"):
                    guild_data.pop("_id")
                if guild_data.get("guild_id"):
                    guild_data.pop("guild_id")
   
                if guild_data.get("point_channels") and len(guild_data["point_channels"]) > 0:
                    point_channels = []
                    for point_channel_id in guild_data["point_channels"]:
                        point_channel = context.guild.get_channel(point_channel_id)
                        if point_channel:
                            point_channels.append(point_channel.mention)
                    guild_data["point_channels"] = ", ".join(point_channels)
                else:
                    guild_data["point_channels"] = "None"

                qotd_channel_id = guild_data.get("qotd_channel") 
                if qotd_channel_id:
                    qotd_channel = context.guild.get_channel(qotd_channel_id)
                    if qotd_channel:
                        guild_data["qotd_channel"] = qotd_channel.mention

                if guild_data.get("aotd_keywords") and len(guild_data["aotd_keywords"]) > 0:
                    guild_data["aotd_keywords"] = ", ".join(guild_data["aotd_keywords"])
                else:
                    guild_data["aotd_keywords"] = "None"

                giveaway_channel_id = guild_data.get("giveaway_channel") 
                if giveaway_channel_id:
                    giveaway_channel = context.guild.get_channel(giveaway_channel_id)
                    if giveaway_channel:
                        guild_data["giveaway_channel"] = giveaway_channel.mention

                if guild_data.get("roblox_groups") and len(guild_data["roblox_groups"]) > 0:
                    roblox_groups = []
                    for group_id in guild_data["roblox_groups"]:
                        group_name = await get_group_name(group_id)
                        if group_name:
                            roblox_groups.append(f"{group_name} ({group_id})")
                    guild_data["roblox_groups"] = ", ".join(roblox_groups)
                else:
                    guild_data["roblox_groups"] = "None"

                if guild_data.get("roblox_games") and len(guild_data["roblox_games"]) > 0:
                    guild_data["roblox_games"] = ", ".join(str(game_id) for game_id in guild_data["roblox_games"])
                else:
                    guild_data["roblox_games"] = "None"

                await response.edit(embed = create_embed({
                    "title": f"Guild Settings",
                    "description": f"Press the {CHANGE_EMOJI} to change settings",
                    "inline": True,
                }, guild_data))

                # Changing settings

                def check_response(reaction, user):
                    return user == context.author and reaction.message == response and str(reaction.emoji) == CHANGE_EMOJI

                try:
                    await response.add_reaction(CHANGE_EMOJI)
                    reaction, user = await self.client.wait_for("reaction_add", check = check_response, timeout = 60)
                except asyncio.TimeoutError:
                    await response.edit(embed = create_embed({
                        "title": f"Guild Settings",
                        "inline": True,
                    }, guild_data))
                    await response.clear_reaction(CHANGE_EMOJI)
                    return
                    
                # get setting to change

                def check_message_response(message):
                    return user == context.author and message.channel == response.channel

                await response.clear_reaction(CHANGE_EMOJI)
                await response.edit(embed = create_embed({
                    "title": "Please type the setting you would like to change",
                    "inline": True,
                    "color": discord.Color.gold()
                }, guild_data))

                name = None
                try:
                    message = await self.client.wait_for("message", check = check_message_response, timeout = 60)
                    await message.delete()
                    name = message.content
                except asyncio.TimeoutError:
                    await response.edit(embed = create_embed({
                        "title": f"You did not enter a setting to change",
                        "inline": True,
                        "color": discord.Color.red()
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue

                if not name:
                    await response.edit(embed = create_embed({
                        "title": f"You did not enter a setting to change",
                        "inline": True,
                        "color": discord.Color.red()
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue

                name = name.lower()
                settings_list = list(DEFAULT_GUILD_DATA.keys())
                settings_list.remove("guild_id")
                if not name in settings_list:
                    await response.edit(embed = create_embed({
                        "title": f"{name} is an invalid setting",
                        "inline": True,
                        "color": discord.Color.red()
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue

                # get value to change setting to

                await response.edit(embed = create_embed({
                    "title": f"Please type the value you would like to change {name} to",
                    "inline": True,
                    "color": discord.Color.gold()
                }, guild_data))

                value = None
                try:
                    message = await self.client.wait_for("message", check = check_message_response, timeout = 60)
                    await message.delete()
                    value = message.content
                except asyncio.TimeoutError:
                    await response.edit(embed = create_embed({
                        "title": f"You did not enter a value to change {name} to",
                        "inline": True,
                        "color": discord.Color.red()
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue

                # changing settings

                if name == "prefix":
                    value = value.lower()

                    if len(value) > 1:
                        await response.edit(embed = create_embed({
                            "title": "Prefix must be one letter",
                            "inline": True,
                            "color": discord.Color.red()
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    if is_number(value):
                        await response.edit(embed = create_embed({
                            "title": "Prefix must be a letter",
                            "inline": True,
                            "color": discord.Color.red()
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    new_guild_data = get_guild_data(context.guild.id)
                    guild_data["prefix"] = value
                    new_guild_data["prefix"] = value
                    save_guild_data(new_guild_data)

                    await response.edit(embed = create_embed({
                        "title": f"Changed prefix to {value}",
                        "inline": True,
                        "color": discord.Color.green()
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                elif name == "message_cooldown":
                    seconds = parse_to_timestamp(value)
                    if not seconds:
                        await response.edit(embed = create_embed({
                            "title": "Could not parse {value}",
                            "inline": True,
                            "color": discord.Color.red(),
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    new_guild_data = get_guild_data(context.guild.id)
                    new_guild_data["message_cooldown"] = seconds
                    guild_data["message_cooldown"] = seconds
                    save_guild_data(new_guild_data)

                    await response.edit(embed = create_embed({
                        "title": f"Changed message cooldown to {value} ({seconds} seconds)",
                        "inline": True,
                        "color": discord.Color.green()
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue
                elif name == "daily_reward":
                    try:
                        value = int(value)
                    except ValueError:
                        await response.edit(embed = create_embed({
                            "title": f"The daily reward ({value}) must be a number",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    if value < 0:
                        await response.edit(embed = create_embed({
                            "title": f"The daily reward ({value}) must be greater than or equal to 0",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    new_guild_data = get_guild_data(context.guild.id)
                    new_guild_data["daily_reward"] = value
                    guild_data["daily_reward"] = value
                    save_guild_data(new_guild_data)

                    await response.edit(embed = create_embed({
                        "title": f"Changed daily reward to {value}",
                        "inline": True,
                        "color": discord.Color.green()
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue
                elif name == "point_channels":
                    channel = get_object(context.guild.text_channels, value)
                    if not channel:
                        await response.edit(embed = create_embed({
                            "title": f"Could not find text channel {channel or value}",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    new_guild_data = get_guild_data(context.guild.id)
                    if channel.id in new_guild_data["point_channels"]:
                        new_guild_data["point_channels"].remove(channel.id)
                        save_guild_data(new_guild_data)

                        if new_guild_data.get("point_channels") and len(new_guild_data["point_channels"]) > 0:
                            point_channels = []
                            for point_channel_id in new_guild_data["point_channels"]:
                                point_channel = context.guild.get_channel(point_channel_id)
                                if point_channel:
                                    point_channels.append(point_channel.mention)
                            guild_data["point_channels"] = ", ".join(point_channels)
                        else:
                            guild_data["point_channels"] = "None"

                        await response.edit(embed = create_embed({
                            "title": f"Removed text channel {channel} from point channels",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue
                    else:
                        new_guild_data["point_channels"].append(channel.id)
                        guild_data["point_channels"] += f", {channel.mention}"
                        save_guild_data(new_guild_data)

                        if new_guild_data.get("point_channels") and len(new_guild_data["point_channels"]) > 0:
                            point_channels = []
                            for point_channel_id in new_guild_data["point_channels"]:
                                point_channel = context.guild.get_channel(point_channel_id)
                                if point_channel:
                                    point_channels.append(point_channel.mention)
                            guild_data["point_channels"] = ", ".join(point_channels)
                        else:
                            guild_data["point_channels"] = "None"

                        await response.edit(embed = create_embed({
                            "title": f"Added text channel {channel} to point channels",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue
                elif name == "points_per_message":
                    try:
                        value = int(value)
                    except ValueError:
                        await response.edit(embed = create_embed({
                            "title": f"The points per message ({value}) must be a number",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    if value < 0:
                        await response.edit(embed = create_embed({
                            "title": f"The points per message ({value}) must be greater than or equal to 0",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    new_guild_data = get_guild_data(context.guild.id)
                    new_guild_data["points_per_message"] = value
                    guild_data["points_per_message"] = value
                    save_guild_data(new_guild_data)

                    await response.edit(embed = create_embed({
                        "title": f"Changed points per message to {value}",
                        "inline": True,
                        "color": discord.Color.green()
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue
                elif name == "qotd_channel":
                    if value.lower() == "none":
                        new_guild_data = get_guild_data(context.guild.id)
                        new_guild_data["qotd_channel"] = None
                        guild_data["qotd_channel"] = None
                        save_guild_data(new_guild_data)
                        await response.edit(embed = create_embed({
                            "title": f"Removed QOTD channel",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    channel = get_object(context.guild.text_channels, value)
                    if not channel:
                        await response.edit(embed = create_embed({
                            "title": f"Could not find text channel {channel or value}",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    new_guild_data = get_guild_data(context.guild.id)
                    new_guild_data["qotd_channel"] = channel.id
                    guild_data["qotd_channel"] = channel.mention
                    save_guild_data(new_guild_data)
                    await response.edit(embed = create_embed({
                        "title": f"Changed QOTD channel to {channel}",
                        "color": discord.Color.green(),
                        "inline": True,
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue
                elif name == "aotd_keywords":
                    value = value.lower()
                    new_guild_data = get_guild_data(context.guild.id)
                    if value in new_guild_data["aotd_keywords"]:
                        new_guild_data["aotd_keywords"].remove(value)
                        save_guild_data(new_guild_data)

                        if new_guild_data.get("aotd_keywords") and len(new_guild_data["aotd_keywords"]) > 0:
                            aotd_keywords = []
                            for keyword in new_guild_data["aotd_keywords"]:
                                aotd_keywords.append(keyword)
                            guild_data["aotd_keywords"] = ", ".join(aotd_keywords)
                        else:
                            guild_data["aotd_keywords"] = "None"


                        await response.edit(embed = create_embed({
                            "title": f"Removed {value} as an AOTD keywords",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue
                    else:
                        new_guild_data["aotd_keywords"].append(value)
                        save_guild_data(new_guild_data)

                        if new_guild_data.get("aotd_keywords") and len(new_guild_data["aotd_keywords"]) > 0:
                            aotd_keywords = []
                            for keyword in new_guild_data["aotd_keywords"]:
                                aotd_keywords.append(keyword)
                            guild_data["aotd_keywords"] = ", ".join(aotd_keywords)
                        else:
                            guild_data["aotd_keywords"] = "None"

                        await response.edit(embed = create_embed({
                            "title": f"Added {value} as an AOTD keywords",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue
                elif name == "points_per_aotd":
                    try:
                        value = int(value)
                    except ValueError:
                        await response.edit(embed = create_embed({
                            "title": f"The points per AOTD ({value}) must be a number",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    if value < 0:
                        await response.edit(embed = create_embed({
                            "title": f"The points per AOTD ({value}) must be greater than or equal to 0",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    new_guild_data = get_guild_data(context.guild.id)
                    new_guild_data["points_per_aotd"] = value
                    guild_data["points_per_aotd"] = value
                    save_guild_data(new_guild_data)

                    await response.edit(embed = create_embed({
                        "title": f"Changed points per AOTD to {value}",
                        "inline": True,
                        "color": discord.Color.green()
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue
                elif name == "giveaway_channel":
                    if value.lower() == "none":
                        new_guild_data = get_guild_data(context.guild.id)
                        new_guild_data["giveaway_channel"] = None
                        guild_data["giveaway_channel"] = None
                        save_guild_data(new_guild_data)
                        await response.edit(embed = create_embed({
                            "title": f"Removed giveaway channel",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    channel = get_object(context.guild.text_channels, value)
                    if not channel:
                        await response.edit(embed = create_embed({
                            "title": f"Could not find text channel {channel or value}",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    new_guild_data = get_guild_data(context.guild.id)
                    new_guild_data["giveaway_channel"] = channel.id
                    guild_data["giveaway_channel"] = channel.mention
                    save_guild_data(new_guild_data)
                    await response.edit(embed = create_embed({
                        "title": f"Changed giveaway channel to {channel}",
                        "color": discord.Color.green(),
                        "inline": True,
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue
                elif name == "roblox_groups":
                    try:
                        value = int(value)
                    except ValueError:
                        await response.edit(embed = create_embed({
                            "title": f"The roblox group ID {value} must be a number",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    group_name = await get_group_name(value)
                    if not group_name:
                        await response.edit(embed = create_embed({
                            "title": f"Could not find roblox group with ID {value}",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    new_guild_data = get_guild_data(context.guild.id)
                    if value in new_guild_data["roblox_groups"]:
                        new_guild_data["roblox_groups"].remove(value)
                        save_guild_data(new_guild_data)

                        if new_guild_data.get("roblox_groups") and len(new_guild_data["roblox_groups"]) > 0:
                            roblox_groups = []
                            for group_id in new_guild_data["roblox_groups"]:
                                group_name = await get_group_name(group_id)
                                if group_name:
                                    roblox_groups.append(f"{group_name} ({group_id})")
                            guild_data["roblox_groups"] = ", ".join(roblox_groups)
                        else:
                            guild_data["roblox_groups"] = "None"

                        await response.edit(embed = create_embed({
                            "title": f"Removed {group_name} ({value}) as a roblox group",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue
                    else:
                        new_guild_data["roblox_groups"].append(value)
                        save_guild_data(new_guild_data)

                        if new_guild_data.get("roblox_groups") and len(new_guild_data["roblox_groups"]) > 0:
                            roblox_groups = []
                            for group_id in new_guild_data["roblox_groups"]:
                                group_name = await get_group_name(group_id)
                                if group_name:
                                    roblox_groups.append(f"{group_name} ({group_id})")
                            guild_data["roblox_groups"] = ", ".join(roblox_groups)
                        else:
                            guild_data["roblox_groups"] = "None"

                        await response.edit(embed = create_embed({
                            "title": f"Added {group_name} ({value}) as a roblox group",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))

                        await asyncio.sleep(WAIT_DELAY)
                        continue
                elif name == "roblox_games":
                    try:
                        value = int(value)
                    except ValueError:
                        await response.edit(embed = create_embed({
                            "title": f"The roblox game ID {value} must be a number",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    new_guild_data = get_guild_data(context.guild.id)
                    if value in new_guild_data["roblox_games"]:
                        new_guild_data["roblox_games"].remove(value)
                        save_guild_data(new_guild_data)

                        if new_guild_data.get("roblox_games") and len(new_guild_data["roblox_games"]) > 0:
                            guild_data["roblox_games"] = ", ".join(str(game_id) for game_id in new_guild_data["roblox_games"])
                        else:
                            guild_data["roblox_games"] = "None"

                        await response.edit(embed = create_embed({
                            "title": f"Removed game with id {value} as a roblox game",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue
                    else:
                        new_guild_data["roblox_games"].append(value)
                        save_guild_data(new_guild_data)

                        if new_guild_data.get("roblox_games") and len(new_guild_data["roblox_games"]) > 0:
                            guild_data["roblox_games"] = ", ".join(str(game_id) for game_id in new_guild_data["roblox_games"])
                        else:
                            guild_data["roblox_games"] = "None"

                        await response.edit(embed = create_embed({
                            "title": f"Added game with id {value} as a roblox game",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))

                        await asyncio.sleep(WAIT_DELAY)
                        continue
                else:
                    await response.edit(embed = create_embed({
                        "title": f"{name} is an invalid setting",
                        "color": discord.Color.red()
                    }))
                    await asyncio.sleep(WAIT_DELAY)
                    continue
        except Exception as error_message:
            traceback.print_exc()
            await response.edit(embed = create_embed({
                "title": f"Could not load settings",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(default(client))
