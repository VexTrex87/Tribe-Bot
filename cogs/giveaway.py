import discord
from discord.ext import commands, tasks
from time import time, ctime

from helper import get_user_data, save_user_data, get_guild_data, save_guild_data, get_all_guild_data, get_object, parse_to_timestamp, draw_dictionary
from constants import GIVEAWAY_UPDATE_DELAY, GIVEAWAY_ENTRY_COST

class cog(commands.Cog):
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
        for guild_data in get_all_guild_data():
            for giveaway_info in guild_data["giveaways"]:
                pass

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
                    await user.send(f"You already entered {message.id}")
                    return

                user_data = get_user_data(user.id)
                if user_data["points"] < GIVEAWAY_ENTRY_COST:
                    await user.send(f"You do not have enough points to join giveaway {message.id}")
                    return

                # process giveaway entry
                user_data["points"] -= GIVEAWAY_ENTRY_COST
                save_user_data(user_data)

                guild_data["giveaways"][index]["member_pool"].append(user.id)
                save_guild_data(guild_data)

                await user.send(f"You joined giveaway {message.id}")
                return

    @commands.command()
    async def creategiveaway(self, context, endsin, price: int, join_emoji, *, title: str):
        guild_data = get_guild_data(context.guild.id)

        giveaway_channel_id = guild_data.get("giveaway_channel")
        if not giveaway_channel_id:
            await context.send("No giveaway channel set")
            return

        giveaway_channel = get_object(context.guild.text_channels, giveaway_channel_id)
        if not giveaway_channel:
            await context.send("No giveaway channel set")
            return

        endsin = parse_to_timestamp(endsin)
        endsin_timestamp = round(time() + endsin)
        endsin_time_text = ctime(endsin_timestamp)

        message = await giveaway_channel.send(draw_dictionary({
            "Title": title,
            "Price": price,
            "Creator": context.author,
            "Ends In": endsin_time_text,
        }))
        await message.add_reaction(join_emoji)

        guild_data["giveaways"].append({
            "title": title,
            "price": price,
            "creator": context.author.id,
            "endsin": endsin_timestamp,
            "join_emoji": join_emoji,
            "message_id": message.id,
            "member_pool": []
        })
        save_guild_data(guild_data)

        await context.send(f"Created giveaway in {giveaway_channel.mention}")

    @commands.command()
    async def giveaways(self, context):
        guild_data = get_guild_data(context.guild.id)
        all_giveaways_text = ""
        for giveaway_info in guild_data["giveaways"]:
            creator = await context.guild.fetch_member(giveaway_info["creator"])

            member_pool = []
            for member_id in giveaway_info["member_pool"]:
                member = await context.guild.fetch_member(member_id)
                if member:
                    member_pool.append(str(member))

            all_giveaways_text += draw_dictionary({
                "Title": giveaway_info["title"],
                "Price": "{} Points".format(giveaway_info["price"]),
                "Creator": creator,
                "Ends In": ctime(giveaway_info["endsin"]),
                "Message ID": giveaway_info["message_id"],
                "Member Pool": member_pool,
            })
        await context.send(len(all_giveaways_text) > 0 and all_giveaways_text or "No giveaways present")

    @commands.command()
    async def deletegiveaway(self, context, message_id: int):
        guild_data = get_guild_data(context.guild.id)
        for index, giveaway_info in enumerate(guild_data["giveaways"]):
            if giveaway_info["message_id"] == message_id:
                guild_data["giveaways"].pop(index)
                await context.send(f"Deleted giveaway {message_id}")
                save_guild_data(guild_data)
                return
        await context.send(f"Could not find giveaway {message_id}")

def setup(client):
    client.add_cog(cog(client))