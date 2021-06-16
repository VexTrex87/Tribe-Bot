import discord
from discord.ext import commands, tasks
from time import time, ctime
import random
import asyncio

from helper import get_user_data, save_user_data, get_guild_data, get_object, parse_to_timestamp, create_embed, get_giveaway, save_giveaway, get_all_giveaways, delete_giveaway, create_giveaway, wait_for_message, wait_for_reaction
from constants import GIVEAWAY_UPDATE_DELAY, DEFAULT_GIVEAWAYS_DATA, DECLINE_EMOJI

def check_if_giveaway_manager(context):
    if context.author == context.guild.owner:
        return True
    elif context.author.guild_permissions.administrator:
        return True

    guild_data = get_guild_data(context.guild.id)

    giveaway_manager_id = guild_data["giveaway_manager"]
    if not giveaway_manager_id:
        return False

    bot_manage_role = context.guild.get_role(giveaway_manager_id)
    if not bot_manage_role:
        return False

    if bot_manage_role in context.author.roles:
        return True
    else:
        return False

class get_giveaway_data():
    def __init__(self, client, context, response):
        self.client = client
        self.context = context
        self.response = response

    async def get_title(self):
        message = await wait_for_message(self.client, self.context)
        if not message:
            raise asyncio.TimeoutError

        await message.delete()
        return message.content

    async def get_price(self):
        await self.response.edit(embed = create_embed({
            "title": "Please enter the price requirement to join the giveaway",
            "color": discord.Color.gold()
        }))

        message = await wait_for_message(self.client, self.context)
        if not message:
            raise asyncio.TimeoutError

        price = message.content

        try:
            price = int(price)
        except ValueError:
            raise Exception(f"The price ({price}) must be a number")

        if price < 0:
            raise Exception(f"The price ({price}) must be greater than or equal to 0")

        await message.delete()
        return price

    async def get_reward(self):
        await self.response.edit(embed = create_embed({
            "title": "Please enter the reward of the giveaway",
            "color": discord.Color.gold()
        }))

        message = await wait_for_message(self.client, self.context)
        if not message:
            raise asyncio.TimeoutError

        reward = message.content

        try:
            reward = int(reward)
        except ValueError:
            raise Exception(f"The reward ({reward}) must be a number")

        if reward < 0:
            raise Exception(f"The reward ({reward}) must be greater than or equal to 0")

        await message.delete()
        return reward

    async def get_endsin(self):
        await self.response.edit(embed = create_embed({
            "title": "Please enter the duration of the giveaway",
            "description": "Example: 86400, 86400s, 1440m, 24h, 1d",
            "color": discord.Color.gold()
        }))

        message = await wait_for_message(self.client, self.context)
        if not message:
            raise asyncio.TimeoutError

        duration = message.content

        try:
            endsin_timestamp = round(time() + parse_to_timestamp(duration))
        except ValueError:
            raise Exception(f"Could not parse duration {duration} to a real duration")

        await message.delete()
        return endsin_timestamp

    async def get_join_emoji(self):
        await self.response.edit(embed = create_embed({
            "title": "Please react with the emoji users will react with to join the giveaway",
            "color": discord.Color.gold()
        }))

        reaction, user = await wait_for_reaction(self.client, self.context)
        await self.response.clear_reactions()
        return str(reaction.emoji)

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
            try:
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
                    message = None
                    try:
                        message = await giveaway_channel.fetch_message(giveaway_info["message_id"])
                    except discord.errors.NotFound:
                        print("Could not find giveaway message {}".format(giveaway_info["message_id"]))
                        delete_giveaway(giveaway_info["message_id"])
                        continue
                    
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

                        try:
                            await winner.send(embed = create_embed({
                                "title": "You won {} points from giveaway {}".format(
                                    giveaway_info["reward"],
                                    giveaway_info["message_id"]
                                ),
                            }))
                        except discord.Forbidden:
                            print("Cannot DM the winner of giveaway {} {}".format(giveaway_info["message_id"], winner))

                        # contact losers
                        for loser_id in giveaway_info["member_pool"]:
                            if loser_id == winner_id:
                                continue

                            loser = await guild.fetch_member(loser_id)
                            if loser:
                                try:
                                    await loser.send(embed = create_embed({
                                        "title": "You did not win giveaway {}".format(giveaway_info["message_id"]),
                                    }))
                                except discord.Forbidden:
                                    print("Cannot DM the winner of giveaway {} {}".format(giveaway_info["message_id"], winner))
                    delete_giveaway(giveaway_info["message_id"])
            except Exception as error_message:
                message_id = giveaway["message_id"]
                print(f"Could not access giveaway {message_id}: {error_message}")

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
        if giveaway_info and giveaway_info["endsin"] > time():
            if str(reaction.emoji) == giveaway_info["join_emoji"]:
                # check giveaway entry
                if user.id in giveaway_info["member_pool"]:
                    try:
                        await user.send(embed = create_embed({
                            "title": f"You already entered giveaway {message.id}",
                            "color": discord.Color.red()
                        }))
                        return
                    except discord.Forbidden:
                        print("Cannot DM {} to tell them that they already entered giveaway {}".format(user, message.id))

                user_data = get_user_data(user.id)
                if user_data["points"] < giveaway_info["price"]:
                    try:
                        await user.send(embed = create_embed({
                            "title": f"You do not have enough points to join giveaway {message.id}",
                            "color": discord.Color.red()
                        }))
                        return
                    except discord.Forbidden:
                        print("Cannot DM {} to tell them that they don't have enough points to join giveaway {}".format(user, message.id))

                # process giveaway entry
                user_data["points"] -= giveaway_info["price"]
                save_user_data(user_data)

                giveaway_info["member_pool"].append(user.id)
                save_giveaway(giveaway_info)

                try:
                    await user.send(embed = create_embed({
                        "title": f"You joined giveaway {message.id}",
                        "color": discord.Color.green()
                    }))
                except discord.Forbidden:
                    print("Cannot DM {} to tell them that they joined giveaway {}".format(user, message.id))
            elif str(reaction.emoji) == DECLINE_EMOJI:
                if user.id == giveaway_info["creator"]:
                    delete_giveaway(message.id)

                    await message.edit(embed = create_embed({
                        "title": "CANCELED: {}".format(giveaway_info["title"]),
                        "color": discord.Color.red(),
                    }, {
                        "Price": "{} points".format(giveaway_info["price"]),
                        "Reward": "{} points".format(giveaway_info["reward"]),
                        "Ends On": ctime(giveaway_info["endsin"]),
                        "Creator": user.mention
                    }))

                    try:
                        await user.send(embed = create_embed({
                            "title": f"Deleted giveaway {message.id}",
                            "color": discord.Color.green()
                        }))
                    except discord.Forbidden:
                        print("Cannot DM {} to tell them that they deleted giveaway {}".format(user, message.id))

    @commands.command()
    @commands.check(check_if_giveaway_manager)
    @commands.guild_only()
    async def giveaway(self, context):
        response = await context.send(embed = create_embed({
            "title": "Please enter the title of the giveaway",
            "color": discord.Color.gold()
        }))

        try:
            # get data
            giveaway = DEFAULT_GIVEAWAYS_DATA.copy()
            giveaway_class = get_giveaway_data(self.client, context, response)
            giveaway["title"] = await giveaway_class.get_title()
            giveaway["price"] = await giveaway_class.get_price()
            giveaway["reward"] = await giveaway_class.get_reward()
            giveaway["endsin"] = await giveaway_class.get_endsin()
            giveaway["join_emoji"] = await giveaway_class.get_join_emoji()
            giveaway["creator"] = context.author.id
            giveaway["guild_id"] = context.guild.id

            # send response
            await response.edit(embed = create_embed({
                "title": "Announcing giveaway...",
                "color": discord.Color.gold()
            }, {
                "Title": giveaway["title"],
                "Price": giveaway["price"],
                "Reward": giveaway["reward"],
                "Ends In": ctime(giveaway["endsin"]),
                "Join Emoji": giveaway["join_emoji"],
                "Creator": context.author.mention,
            }))

            # announce giveaway
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

            giveaway_message = await giveaway_channel.send(embed=create_embed({
                "title": giveaway["title"],
                "color": discord.Color.gold(),
            }, {
                "Price": "{} points".format(giveaway["price"]),
                "Reward": "{} points".format(giveaway["reward"]),
                "Ends On": ctime(giveaway["endsin"]),
                "Creator": context.author.mention
            }))

            await giveaway_message.add_reaction(giveaway["join_emoji"])
            giveaway["message_id"] = giveaway_message.id
            create_giveaway(giveaway)

            await response.edit(embed = create_embed({
                "title": "Giveaway announced in #{giveaway_channel.name}",
                "color": discord.Color.gold()
            }, {
                "Title": giveaway["title"],
                "Price": giveaway["price"],
                "Reward": giveaway["reward"],
                "Ends In": ctime(giveaway["endsin"]),
                "Join Emoji": giveaway["join_emoji"],
                "Creator": context.author.mention,
                "Message": giveaway_message.jump_url
            }))
        except asyncio.TimeoutError:
            await response.edit(embed = create_embed({
                "title": f"No response entered",
                "color": discord.Color.red()
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not create giveaway",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(giveaway(client))
