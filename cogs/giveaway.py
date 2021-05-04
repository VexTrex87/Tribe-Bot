import discord
from discord.ext import commands, tasks
from time import time, ctime
import random
import asyncio

from helper import get_user_data, save_user_data, get_guild_data, save_guild_data, get_all_guild_data, get_object, parse_to_timestamp, create_embed, get_giveaway, save_giveaway, get_all_giveaways, delete_giveaway, create_giveaway
from constants import GIVEAWAY_UPDATE_DELAY, DEFAULT_GIVEAWAYS_DATA, WAIT_DELAY

class giveaway(commands.Cog, description = "Commands for managing and entering giveaways."):
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

        for giveaway_info in get_all_giveaways():
            guild = self.client.get_guild(giveaway_info["guild_id"])
            guild_data = get_guild_data(guild.id)

            # get giveaway channel
            giveaway_channel_id = guild_data.get("giveaway_channel")
            if not giveaway_channel_id:
                continue

            giveaway_channel = guild.get_channel(giveaway_channel_id)
            if not giveaway_channel:
                continue

            if timestamp >= giveaway_info["endsin"]:
                # end giveaway
                message = await giveaway_channel.fetch_message(giveaway_info["message_id"])
                title = giveaway_info["title"]
                prize = giveaway_info["reward"]
                endsin_time_text = ctime(giveaway_info["endsin"])

                creator = await guild.fetch_member(giveaway_info["creator"])
                creator = creator and creator.mention or "Unknown"

                if len(giveaway_info["member_pool"]) == 0:
                    await message.edit(embed = create_embed({
                        "title": f"ENDED: {title}",
                        "color": discord.Color.green()
                    }, {
                        "Winner": "||None||",
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
                    winner_user_data["points"] += giveaway_info["reward"]
                    save_user_data(winner_user_data)
                    
                    await message.edit(embed = create_embed({
                        "title": f"ENDED: {title}",
                        "color": discord.Color.green()
                    }, {
                        "Winner": f"||{winner.mention}||",
                        "Prize": f"{prize} points",
                        "Creator": creator,
                        "Ended": endsin_time_text,
                    }))

                    await winner.send(embed = create_embed({
                        "title": "You won {} points from giveaway {}".format(
                            giveaway_info["reward"],
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

                delete_giveaway(giveaway_info["message_id"])

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or not reaction.message.guild:
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
        giveaway_info = get_giveaway(message.id)
        if giveaway_info:
            # check giveaway entry
            if user.id in giveaway_info["member_pool"]:
                await user.send(embed = create_embed({
                    "title": f"You already entered giveaway {message.id}",
                    "color": discord.Color.red()
                }))
                return

            user_data = get_user_data(user.id)
            if user_data["points"] < giveaway_info["price"]:
                await user.send(embed = create_embed({
                    "title": f"You do not have enough points to join giveaway {message.id}",
                    "color": discord.Color.red()
                }))
                return

            # process giveaway entry
            user_data["points"] -= giveaway_info["price"]
            save_user_data(user_data)

            giveaway_info["member_pool"].append(user.id)
            save_giveaway(giveaway_info)

            await user.send(embed = create_embed({
                "title": f"You joined giveaway {message.id}",
                "color": discord.Color.green()
            }))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    @commands.guild_only()
    async def giveaway(self, context):
        response = await context.send(embed = create_embed({
            "title": "Please enter the title of the giveaway",
            "color": discord.Color.gold()
        }))

        try:
            giveaway = DEFAULT_GIVEAWAYS_DATA.copy()
            def check_message_response(message):
                return message.author == context.author and message.channel == response.channel

            # title
            message = await self.client.wait_for("message", check = check_message_response, timeout = 60)
            await message.delete()
            giveaway["title"] = message.content

            # price 
            while True:
                await response.edit(embed = create_embed({
                    "title": "Please enter the price requirement to join the giveaway",
                    "color": discord.Color.gold()
                }))

                message = await self.client.wait_for("message", check = check_message_response, timeout = 30)
                price = message.content

                try:
                    price = int(price)
                except ValueError:
                    await response.edit(embed = create_embed({
                        "title": f"The price ({price}) must be a number",
                        "color": discord.Color.red()
                    }))
                    await asyncio.sleep(WAIT_DELAY)
                    continue
        
                if price < 0:
                    await response.edit(embed = create_embed({
                        "title": f"The price ({price}) must be greater than or equal to 0",
                        "color": discord.Color.red()
                    }))
                    await asyncio.sleep(WAIT_DELAY)
                    continue

                giveaway["price"] = price
                await message.delete()
                break

            # reward 
            while True:
                await response.edit(embed = create_embed({
                    "title": "Please enter the reward of the giveaway",
                    "color": discord.Color.gold()
                }))

                message = await self.client.wait_for("message", check = check_message_response, timeout = 30)
                reward = message.content

                try:
                    reward = int(reward)
                except ValueError:
                    await response.edit(embed = create_embed({
                        "title": f"The reward ({reward}) must be a number",
                        "color": discord.Color.red()
                    }))
                    await asyncio.sleep(WAIT_DELAY)
                    continue
        
                if reward < 0:
                    await response.edit(embed = create_embed({
                        "title": f"The reward ({reward}) must be greater than or equal to 0",
                        "color": discord.Color.red()
                    }))
                    await asyncio.sleep(WAIT_DELAY)
                    continue

                giveaway["reward"] = reward
                await message.delete()
                break

            # ends in 
            while True:
                await response.edit(embed = create_embed({
                    "title": "Please enter the duration of the giveaway",
                    "description": "Example: 86400, 86400s, 1440m, 24h, 1d",
                    "color": discord.Color.gold()
                }))

                message = await self.client.wait_for("message", check = check_message_response, timeout = 30)
                duration = message.content

                try:
                    parsed_timestamp = parse_to_timestamp(duration)
                    endsin_timestamp = round(time() + parsed_timestamp)
                    endsin_time_text = ctime(endsin_timestamp)
                except ValueError:
                    await response.edit(embed = create_embed({
                        "title": f"Could not parse duration {duration} to a real duration",
                        "color": discord.Color.red()
                    }))
                    await asyncio.sleep(WAIT_DELAY)
                    continue

                giveaway["endsin"] = endsin_timestamp
                await message.delete()
                break

            # join emoji
            while True:
                await response.edit(embed = create_embed({
                    "title": "Please react with the emoji users will react with to join the giveaway",
                    "color": discord.Color.gold()
                }))

                def check_reaction_response(reaction, user):
                    return user == context.author and reaction.message == response

                reaction, user = await self.client.wait_for("reaction_add", check = check_reaction_response, timeout = 30)
                join_emoji = reaction.emoji
                giveaway["join_emoji"] = str(join_emoji)
                await response.clear_reactions()
                break
              
            # other info
            giveaway["creator"] = context.author.id
            giveaway["guild_id"] = context.guild.id

            # create giveaway announcement

            await response.edit(embed = create_embed({
                "title": "Announcing giveaway...",
                "color": discord.Color.gold()
            }, {
                "Title": giveaway["title"],
                "Price": giveaway["price"],
                "Reward": giveaway["reward"],
                "Ends In": endsin_time_text,
                "Join Emoji": giveaway["join_emoji"],
                "Creator": context.author.mention,

            }))

            await asyncio.sleep(2)

            guild_data = get_guild_data(context.guild.id)

            giveaway_channel_id = guild_data.get("giveaway_channel")
            if not giveaway_channel_id:
                await response.edit(embed = create_embed({
                    "title": f"No giveaway channel set",
                    "color": discord.Color.red()
                }))
                return

            giveaway_channel = get_object(context.guild.text_channels, giveaway_channel_id)
            if not giveaway_channel:
                await response.edit(embed = create_embed({
                    "title": f"No giveaway channel set",
                    "color": discord.Color.red()
                }))
                return

            embed = create_embed({
                "title": giveaway["title"],
                "color": discord.Color.gold(),
            }, {
                "Price": "{} points".format(giveaway["price"]),
                "Reward": "{} points".format(giveaway["reward"]),
                "Ends On": ctime(giveaway["endsin"]),
                "Creator": context.author.mention
            })
            giveaway_message = await giveaway_channel.send(embed = embed)

            await giveaway_message.add_reaction(join_emoji)

            # other info & save
            giveaway["message_id"] = giveaway_message.id
            create_giveaway(giveaway)

            await response.edit(embed = create_embed({
                "title": "Created giveaway",
                "color": discord.Color.green()
            }, {
                "Title": giveaway["title"],
                "Price": giveaway["price"],
                "Reward": giveaway["reward"],
                "Ends In": endsin_time_text,
                "Join Emoji": giveaway["join_emoji"],
                "Creator": context.author.mention,

            }))
        except asyncio.TimeoutError:
            await response.edit(embed = create_embed({
                "title": f"No response entered",
                "color": discord.Color.red()
            }))
        except Exception as error_message:
            traceback.print_exc()
            await response.edit(embed = create_embed({
                "title": "Could not create giveaway",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(giveaway(client))