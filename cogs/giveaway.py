import discord
from discord.ext import commands, tasks
from time import time, ctime

from helper import get_guild_data, save_guild_data, get_all_guild_data, get_object, parse_time, draw_dictionary
from constants import GIVEAWAY_UPDATE_DELAY

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

        endsin = parse_time(endsin)
        endsin_timestamp = round(time() + endsin)
        endsin_time_text = ctime(endsin_timestamp)

        giveaway_info = {
            "title": title,
            "price": price,
            "creator": context.author.id,
            "endsin": endsin_timestamp,
            "join_emoji": join_emoji,
            "id": len(guild_data["giveaways"]) > 0 and guild_data["giveaways"][-1]["id"] + 1 or 1
        }

        message = await giveaway_channel.send(draw_dictionary({
            "Title": giveaway_info["title"],
            "Price": giveaway_info["price"],
            "Creator": context.author,
            "Ends In": endsin_time_text,
            "ID": giveaway_info["id"]
        }))
        await message.add_reaction(join_emoji)

        guild_data["giveaways"].append(giveaway_info)
        save_guild_data(guild_data)

        await context.send(f"Created giveaway in {giveaway_channel.mention}")

    @commands.command()
    async def giveaways(self, context):
        guild_data = get_guild_data(context.guild.id)
        all_giveaways_text = ""
        for giveaway_info in guild_data["giveaways"]:
            all_giveaways_text += draw_dictionary({
                "Title": giveaway_info["title"],
                "Price": giveaway_info["price"],
                "Creator": giveaway_info["creator"],
                "Ends In": giveaway_info["endsin"],
                "ID": giveaway_info["id"]
            })
        await context.send(len(all_giveaways_text) > 0 and all_giveaways_text or "No giveaways present")

    @commands.command()
    async def deletegiveaway(self, context, id: int):
        guild_data = get_guild_data(context.guild.id)
        for index, giveaway_info in enumerate(guild_data["giveaways"]):
            if giveaway_info["id"] == id:
                guild_data["giveaways"].pop(index)
                await context.send(f"Deleted giveaway {id}")
                save_guild_data(guild_data)
                return
        await context.send(f"Could not find giveaway {id}")

def setup(client):
    client.add_cog(cog(client))