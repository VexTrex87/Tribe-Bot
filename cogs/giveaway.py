import discord
from discord.ext import commands, tasks
from time import time, ctime
import random

from helper import get_user_data, save_user_data, get_guild_data, save_guild_data, get_all_guild_data, get_object, parse_to_timestamp, draw_dictionary, create_embed
from constants import GIVEAWAY_UPDATE_DELAY, GIVEAWAY_ENTRY_COST

class giveaway(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    def cog_load(self):
        self.check_giveaways.start()

    @tasks.loop(seconds = GIVEAWAY_UPDATE_DELAY)
    async def check_giveaways(self):
        await self.client.wait_until_ready()

        timestamp = round(time())
        for guild_data in get_all_guild_data():
            guild = self.client.get_guild(guild_data["guild_id"])

            # get giveaway channel
            giveaway_channel_id = guild_data.get("giveaway_channel")
            if not giveaway_channel_id:
                continue

            giveaway_channel = guild.get_channel(giveaway_channel_id)
            if not giveaway_channel:
                continue

            # check giveaways
            for index, giveaway_info in enumerate(guild_data["giveaways"]):
                if timestamp >= giveaway_info["endsin"]:
                    # end giveaway
                    message = await giveaway_channel.fetch_message(giveaway_info["message_id"])
                    title = giveaway_info["title"]
                    prize = giveaway_info["prize"]
                    endsin_time_text = ctime(giveaway_info["endsin"])

                    creator = await guild.fetch_member(giveaway_info["creator"])
                    creator = creator and creator.mention or "Unknown"

                    if len(giveaway_info["member_pool"]) == 0:
                        await message.edit(embed = create_embed({
                            "title": f"ENDED: {title}",
                            "color": discord.Color.green()
                        }, {
                            "Winner": "None",
                            "Prize": f"{prize} points",
                            "Creator": creator,
                            "Ended": endsin_time_text
                        }))
                    else:
                        # get winner
                        winner = None
                        winner_id = None
                        while True:
                            winner_id = random.choice(giveaway_info["member_pool"])
                            winner = await guild.fetch_member(winner_id)
                            if winner:
                                break

                        # reward winner
                        winner_user_data = get_user_data(winner_id)
                        winner_user_data["points"] += giveaway_info["prize"]
                        save_user_data(winner_user_data)
                        
                        await message.edit(embed = create_embed({
                            "title": f"ENDED: {title}",
                            "color": discord.Color.green()
                        }, {
                            "Winner": winner.mention,
                            "Prize": f"{prize} points",
                            "Creator": creator,
                            "Ended": endsin_time_text,
                        }))

                        await winner.send(embed = create_embed({
                            "title": "You won {} points from giveaway {}".format(
                                giveaway_info["prize"],
                                giveaway_info["message_id"]
                            ),
                        }))

                        # contact losers
                        for loser_id in giveaway_info["member_pool"]:
                            if loser_id == winner_id:
                                continue

                            loser = await guild.fetch_member(loser_id)
                            if loser:
                                await loser.send(embed = create_embed({
                                    "title": "You did not win giveaway {}".format(giveaway_info["message_id"]),
                                }))

                    guild_data["giveaways"].pop(index)
            save_guild_data(guild_data)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        message = reaction.message
        guild = message.guild
        guild_data = get_guild_data(guild.id)

        # check giveaway channel
        giveaway_channel_id = guild_data["giveaway_channel"]
        if not giveaway_channel_id:
            return

        giveaway_channel = get_object(guild.text_channels, giveaway_channel_id)
        if not giveaway_channel:
            return

        # check if user reacted to a giveaway
        for index, giveaway_info in enumerate(guild_data["giveaways"]):
            if giveaway_info["message_id"] == message.id:
                # check giveaway entry
                if user.id in giveaway_info["member_pool"]:
                    await user.send(embed = create_embed({
                        "title": f"You already entered giveaway {message.id}",
                        "color": discord.Color.red()
                    }))
                    return

                user_data = get_user_data(user.id)
                if user_data["points"] < GIVEAWAY_ENTRY_COST:
                    await user.send(embed = create_embed({
                        "title": f"You do not have enough points to join giveaway {message.id}",
                        "color": discord.Color.red()
                    }))
                    return

                # process giveaway entry
                user_data["points"] -= GIVEAWAY_ENTRY_COST
                save_user_data(user_data)

                guild_data["giveaways"][index]["member_pool"].append(user.id)
                save_guild_data(guild_data)

                await user.send(embed = create_embed({
                    "title": f"You joined giveaway {message.id}",
                    "color": discord.Color.green()
                }))
                return

    @commands.command()
    async def creategiveaway(self, context, endsin, prize: int, join_emoji, *, title: str):
        response = await context.send(embed = create_embed({
            "title": f"Creating giveaway...",
            "color": discord.Color.gold()
        }, {
            "Title": title,
            "Ends in": endsin,
            "Prize": f"{prize} points",
            "Join Emoji": join_emoji,
        }))
        
        try:
            guild_data = get_guild_data(context.guild.id)

            giveaway_channel_id = guild_data.get("giveaway_channel")
            if not giveaway_channel_id:
                await response.edit(embed = create_embed({
                    "title": f"No giveaway channel set",
                    "color": discord.Color.red()
                }, {
                    "Title": title,
                    "Ends in": endsin,
                    "Prize": f"{prize} points",
                    "Join Emoji": join_emoji,
                }))
                return

            giveaway_channel = get_object(context.guild.text_channels, giveaway_channel_id)
            if not giveaway_channel:
                await response.edit(embed = create_embed({
                    "title": f"No giveaway channel set",
                    "color": discord.Color.red()
                }, {
                    "Title": title,
                    "Ends in": endsin,
                    "Prize": f"{prize} points",
                    "Join Emoji": join_emoji,
                }))
                return

            endsin = parse_to_timestamp(endsin)
            endsin_timestamp = round(time() + endsin)
            endsin_time_text = ctime(endsin_timestamp)

            message = await giveaway_channel.send(embed = create_embed({
                "title": title,
                "color": discord.Color.gold()
            }, {
                "Prize": f"{prize} points",
                "Creator": context.author.mention,
                "Ends In": endsin_time_text
            }))
            await message.add_reaction(join_emoji)

            guild_data["giveaways"].append({
                "title": title,
                "prize": prize,
                "creator": context.author.id,
                "endsin": endsin_timestamp,
                "join_emoji": join_emoji,
                "message_id": message.id,
                "member_pool": []
            })
            save_guild_data(guild_data)

            await response.edit(embed = create_embed({
                "title": f"Created giveaway in {giveaway_channel}",
                "color": discord.Color.green()
            }, {
                "Title": title,
                "Ends in": endsin,
                "Prize": f"{prize} points",
                "Join Emoji": join_emoji,
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not create giveaway",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message,
                "Title": title,
                "Ends in": endsin,
                "Prize": f"{prize} points",
                "Join Emoji": join_emoji,
            }))
            
    @commands.command()
    async def giveaways(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Loading giveaways...",
            "color": discord.Color.gold()
        }))
        
        try:
            guild_data = get_guild_data(context.guild.id)
            fields = {}
            for giveaway_info in guild_data["giveaways"]:
                creator = await context.guild.fetch_member(giveaway_info["creator"])
                title = giveaway_info["title"]
                prize = giveaway_info["prize"]
                endsin = ctime(giveaway_info["endsin"])
                message_id = giveaway_info["message_id"]

                member_pool_count = 0
                for member_id in giveaway_info["member_pool"]:
                    member = await context.guild.fetch_member(member_id)
                    if member:
                        member_pool_count += 1

                fields[title] = f"Prize: {prize} points | Creator: {creator} | Ends In: {endsin} | Message ID: {message_id} | Member Pool: {member_pool_count} members"

            await response.edit(embed = create_embed({
                "title": f"Giveaways",
            }, fields))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load giveaways",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message,
            }))

    @commands.command()
    async def deletegiveaway(self, context, message_id: int):
        response = await context.send(embed = create_embed({
            "title": f"Deleting giveaway {message_id}...",
            "color": discord.Color.gold()
        }))
        
        try:
            guild_data = get_guild_data(context.guild.id)
            for index, giveaway_info in enumerate(guild_data["giveaways"]):
                if giveaway_info["message_id"] == message_id:
                    guild_data["giveaways"].pop(index)
                    save_guild_data(guild_data)

                    giveaway_channel_id = guild_data.get("giveaway_channel")
                    if giveaway_channel_id:
                        giveaway_channel = context.guild.get_channel(giveaway_channel_id)
                        if giveaway_channel:
                            try:
                                message = await giveaway_channel.fetch_message(giveaway_info["message_id"])
                                if message:
                                    await message.delete()
                            except discord.NotFound:
                                pass # sometimes giveaway message is deleted
                            except Exception as error_message:
                                raise Exception(error_message)

                    await response.edit(embed = create_embed({
                        "title": f"Deleted giveaway {message_id}",
                        "color": discord.Color.green()
                    }))
                    return
            await response.edit(embed = create_embed({
                "title": f"Could not find giveaway {message_id}",
                "color": discord.Color.red()
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not delete giveaway {message_id}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message,
            }))
            
def setup(client):
    client.add_cog(giveaway(client))