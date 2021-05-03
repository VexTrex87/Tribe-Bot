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

                if guild_data.get("point_channels"):
                    point_channels = []
                    for channel_id in guild_data["point_channels"]:
                        channel = context.guild.get_channel(channel_id)
                        if channel:
                            point_channels.append(channel.mention)
                    guild_data["point_channels"] = ", ".join(point_channels)

                if guild_data.get("qotd_channel"):
                    channel = context.guild.get_channel(channel_id)
                    if channel:
                        guild_data["qotd_channel"] = channel.mention

                if guild_data.get("aotd_keywords") and len(guild_data["aotd_keywords"]) > 0:
                    guild_data["aotd_keywords"] = ", ".join(guild_data["aotd_keywords"])
                else:
                    guild_data["aotd_keywords"] = "None"

                if guild_data.get("giveaway_channel"):
                    channel = context.guild.get_channel(channel_id)
                    if channel:
                        guild_data["giveaway_channel"] = channel.mention

                if guild_data.get("roblox_groups"):
                    roblox_groups = []
                    for group_id in guild_data["roblox_groups"]:
                        group_name = await get_group_name(group_id)
                        if group_name:
                            roblox_groups.append(f"{group_name} ({group_id})")
                    guild_data["roblox_groups"] = ", ".join(roblox_groups)

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
                    save_guild_data(new_guild_data)

                    await response.edit(embed = create_embed({
                        "title": f"Changed message cooldown to {value} ({seconds} seconds)",
                        "inline": True,
                        "color": discord.Color.green()
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
            # traceback.print_exc()
            await response.edit(embed = create_embed({
                "title": f"Could not load settings",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(default(client))
